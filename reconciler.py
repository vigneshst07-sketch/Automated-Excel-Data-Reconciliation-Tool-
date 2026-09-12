"""
Excel Data Reconciliation Engine
Core reconciliation logic comparing raw Excel workbooks against 1 to 4+ source workbooks.
Supports exact matching, fuzzy close matching (>80% similarity or within 5% numeric difference),
and mismatch/null detection with OpenPyXL color highlighting and executive summary sheet generation.
"""

import os
import glob
import datetime
from typing import List, Dict, Any, Tuple, Optional, Callable
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Try importing rapidfuzz, fallback to difflib
try:
    from rapidfuzz import fuzz
    def calculate_text_similarity(s1: str, s2: str) -> float:
        return fuzz.ratio(str(s1).lower().strip(), str(s2).lower().strip()) / 100.0
except ImportError:
    import difflib
    def calculate_text_similarity(s1: str, s2: str) -> float:
        matcher = difflib.SequenceMatcher(None, str(s1).lower().strip(), str(s2).lower().strip())
        return matcher.ratio()


# Color styling constants as requested in project specifications
YELLOW_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
YELLOW_FONT = Font(name="Calibri", size=11, color="9C6500", bold=True)

RED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
RED_FONT = Font(name="Calibri", size=11, color="9C0006", bold=True)

HEADER_FILL = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, color="FFFFFF", bold=True)

CARD_HEADER_FILL = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
THIN_BORDER_SIDE = Side(border_style="thin", color="CBD5E1")
CELL_BORDER = Border(left=THIN_BORDER_SIDE, right=THIN_BORDER_SIDE, top=THIN_BORDER_SIDE, bottom=THIN_BORDER_SIDE)


def is_numeric(val: Any) -> bool:
    """Check if value can be parsed as a float."""
    if val is None or isinstance(val, bool):
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


def compare_values(raw_val: Any, src_val: Any) -> Tuple[str, float]:
    """
    Compare raw_val and src_val.
    Returns:
        (status, score_or_diff)
        status: "EXACT", "CLOSE", "MISMATCH", or "EMPTY"
    """
    # 1. Null / Empty checks
    raw_empty = raw_val is None or (isinstance(raw_val, str) and raw_val.strip() == "")
    src_empty = src_val is None or (isinstance(src_val, str) and src_val.strip() == "")

    if raw_empty and src_empty:
        return "EXACT", 1.0

    if raw_empty or src_empty:
        return "MISMATCH", 0.0

    # 2. Exact match check
    if raw_val == src_val:
        return "EXACT", 1.0

    str_raw = str(raw_val).strip()
    str_src = str(src_val).strip()

    if str_raw.lower() == str_src.lower():
        return "EXACT", 1.0

    # 3. Numeric Comparison (within 5% difference)
    if is_numeric(raw_val) and is_numeric(src_val):
        num_raw = float(raw_val)
        num_src = float(src_val)

        if num_raw == num_src:
            return "EXACT", 1.0

        diff = abs(num_raw - num_src)
        denom = max(abs(num_raw), abs(num_src))

        if denom > 0:
            rel_diff = diff / denom
            if rel_diff <= 0.05:
                # Within 5% difference -> Close Match!
                return "CLOSE", round((1.0 - rel_diff) * 100, 2)

        return "MISMATCH", 0.0

    # 4. Text Similarity (>80% similarity)
    similarity = calculate_text_similarity(str_raw, str_src)
    if similarity >= 0.80:
        return "CLOSE", round(similarity * 100, 2)

    return "MISMATCH", round(similarity * 100, 2)


class ExcelReconciler:
    def __init__(
        self,
        raw_file_path: str,
        source_path: str,
        user_name: str = "Reconciliation Operator",
        progress_callback: Optional[Callable[[float, str], None]] = None
    ):
        self.raw_file_path = raw_file_path
        self.source_path = source_path
        self.user_name = user_name or "Reconciliation Operator"
        self.progress_callback = progress_callback or (lambda pct, msg: None)

        # Statistics
        self.stats = {
            "total_evaluated": 0,
            "exact_matches": 0,
            "close_matches": 0,
            "mismatches": 0,
            "accuracy_pct": 0.0,
            "sheets_evaluated": 0,
            "source_files_count": 0,
            "source_files": [],
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sheet_breakdown": []
        }

    def resolve_source_files(self) -> List[str]:
        """Resolve all Excel source files from source_path (file or folder)."""
        if os.path.isfile(self.source_path):
            return [self.source_path]

        if os.path.isdir(self.source_path):
            files = []
            for ext in ("*.xlsx", "*.xlsm", "*.xltx", "*.xltm"):
                files.extend(glob.glob(os.path.join(self.source_path, ext)))
                files.extend(glob.glob(os.path.join(self.source_path, ext.upper())))
            # Exclude temporary Excel lock files (~$)
            files = [f for f in sorted(list(set(files))) if not os.path.basename(f).startswith("~$")]
            return files

        # Check if comma-separated or wildcard
        matched = glob.glob(self.source_path)
        if matched:
            return [f for f in sorted(matched) if not os.path.basename(f).startswith("~$")]

        return []

    def reconcile(self, output_file_path: Optional[str] = None) -> Dict[str, Any]:
        """Run the complete reconciliation process."""
        self.progress_callback(5, "Resolving input and source Excel files...")

        if not os.path.exists(self.raw_file_path):
            raise FileNotFoundError(f"Raw Excel workbook not found: {self.raw_file_path}")

        source_files = self.resolve_source_files()
        if not source_files:
            raise FileNotFoundError(
                f"No valid Excel (.xlsx) source files found in source path: {self.source_path}"
            )

        self.stats["source_files_count"] = len(source_files)
        self.stats["source_files"] = [os.path.basename(f) for f in source_files]

        self.progress_callback(15, f"Found {len(source_files)} source workbook(s). Loading raw workbook...")

        # Load Raw Workbook with openpyxl
        raw_wb = openpyxl.load_workbook(self.raw_file_path, data_only=True)
        
        self.progress_callback(25, "Loading and indexing source workbook(s)...")

        # Load all source workbooks and build lookup indices
        # Structure: sources_data[sheet_name] = list of row dicts or cell coordinates
        sources_wb_list = []
        for sf in source_files:
            try:
                wb = openpyxl.load_workbook(sf, data_only=True)
                sources_wb_list.append((sf, wb))
            except Exception as e:
                print(f"Warning: could not open source file {sf}: {e}")

        if not sources_wb_list:
            raise ValueError("Failed to load any of the specified source workbooks.")

        # Prepare evaluation tracking
        total_evaluated = 0
        total_exact = 0
        total_close = 0
        total_mismatch = 0

        # Create output file path if not provided
        if not output_file_path:
            base_dir = os.path.dirname(self.raw_file_path) or "."
            base_name = os.path.splitext(os.path.basename(self.raw_file_path))[0]
            output_file_path = os.path.join(base_dir, f"{base_name}_Reconciled.xlsx")

        raw_sheet_names = raw_wb.sheetnames
        sheet_count = len(raw_sheet_names)

        diff_details = []

        # Iterate over raw sheets
        for sheet_idx, sheet_name in enumerate(raw_sheet_names):
            pct = 30 + int(50 * (sheet_idx / max(sheet_count, 1)))
            self.progress_callback(pct, f"Reconciling sheet '{sheet_name}' ({sheet_idx + 1}/{sheet_count})...")

            raw_sheet = raw_wb[sheet_name]
            max_row = raw_sheet.max_row
            max_col = raw_sheet.max_column

            if max_row < 1 or max_col < 1:
                continue

            # Read raw header row (Row 1)
            raw_headers = []
            for col in range(1, max_col + 1):
                val = raw_sheet.cell(row=1, column=col).value
                raw_headers.append(str(val).strip() if val is not None else f"Column_{col}")

            # Identify key column if any (e.g. ID, Code, SKU, Key, Item, Invoice)
            key_col_idx = 1
            for idx, h in enumerate(raw_headers, start=1):
                h_clean = h.lower().replace("_", "").replace(" ", "")
                if h_clean in ("id", "code", "itemid", "sku", "invoiceno", "invoice", "key", "accountid", "ref"):
                    key_col_idx = idx
                    break

            # Index all sources for this sheet (or fallback to source sheet 1)
            # source_records_by_key: key -> {header: value}
            # source_records_by_row: row_idx -> {col_idx: value}
            source_records_by_key = {}
            source_records_by_row = {}

            for src_file, src_wb in sources_wb_list:
                # Find matching sheet in source or use active sheet
                if sheet_name in src_wb.sheetnames:
                    src_sheet = src_wb[sheet_name]
                else:
                    src_sheet = src_wb.active

                src_max_r = src_sheet.max_row
                src_max_c = src_sheet.max_column

                if src_max_r < 1 or src_max_c < 1:
                    continue

                # Read source headers
                src_headers = []
                for col in range(1, src_max_c + 1):
                    val = src_sheet.cell(row=1, column=col).value
                    src_headers.append(str(val).strip() if val is not None else f"Column_{col}")

                src_key_col_idx = 1
                for idx, h in enumerate(src_headers, start=1):
                    h_clean = h.lower().replace("_", "").replace(" ", "")
                    if h_clean in ("id", "code", "itemid", "sku", "invoiceno", "invoice", "key", "accountid", "ref"):
                        src_key_col_idx = idx
                        break

                # Read source rows
                for r in range(2, src_max_r + 1):
                    row_data = {}
                    row_by_col = {}
                    key_val = src_sheet.cell(row=r, column=src_key_col_idx).value
                    key_str = str(key_val).strip().lower() if key_val is not None else None

                    for c in range(1, src_max_c + 1):
                        cell_v = src_sheet.cell(row=r, column=c).value
                        col_h = src_headers[c - 1] if (c - 1) < len(src_headers) else f"Column_{c}"
                        row_data[col_h] = cell_v
                        row_by_col[c] = cell_v

                    if key_str and key_str not in source_records_by_key:
                        source_records_by_key[key_str] = row_data

                    if r not in source_records_by_row:
                        source_records_by_row[r] = row_by_col

            sheet_exact = 0
            sheet_close = 0
            sheet_mismatch = 0
            sheet_evaluated = 0

            # Compare each data row in raw_sheet
            for r in range(2, max_row + 1):
                raw_key_val = raw_sheet.cell(row=r, column=key_col_idx).value
                raw_key_str = str(raw_key_val).strip().lower() if raw_key_val is not None else None

                # Find corresponding source row:
                src_row_dict = None
                if raw_key_str and raw_key_str in source_records_by_key:
                    src_row_dict = source_records_by_key[raw_key_str]

                src_col_dict = source_records_by_row.get(r, {})

                for c in range(1, max_col + 1):
                    cell = raw_sheet.cell(row=r, column=c)
                    raw_val = cell.value
                    header_name = raw_headers[c - 1] if (c - 1) < len(raw_headers) else f"Column_{c}"

                    # Determine source value
                    if src_row_dict and header_name in src_row_dict:
                        src_val = src_row_dict[header_name]
                    elif c in src_col_dict:
                        src_val = src_col_dict[c]
                    else:
                        src_val = None

                    # If both are entirely null/empty in a trailing row, we still evaluate if within active table
                    status, score = compare_values(raw_val, src_val)
                    sheet_evaluated += 1

                    cell_coord = f"{get_column_letter(c)}{r}"

                    if status == "EXACT":
                        sheet_exact += 1
                        # Exact match -> Keep normal formatting (user requirement)
                    elif status == "CLOSE":
                        sheet_close += 1
                        # Close match -> Highlight cell YELLOW (#FFEB9C text #9C6500)
                        cell.fill = YELLOW_FILL
                        cell.font = YELLOW_FONT
                        diff_details.append({
                            "sheet": sheet_name,
                            "cell": cell_coord,
                            "row": r,
                            "col": c,
                            "header": header_name,
                            "raw_value": str(raw_val) if raw_val is not None else "",
                            "source_value": str(src_val) if src_val is not None else "",
                            "status": "CLOSE_MATCH",
                            "score_diff": score
                        })
                    else:  # MISMATCH or Empty/Null
                        sheet_mismatch += 1
                        # Mismatch or Empty/Null value -> Highlight cell RED (#FFC7CE text #9C0006)
                        cell.fill = RED_FILL
                        cell.font = RED_FONT
                        diff_details.append({
                            "sheet": sheet_name,
                            "cell": cell_coord,
                            "row": r,
                            "col": c,
                            "header": header_name,
                            "raw_value": str(raw_val) if raw_val is not None else "",
                            "source_value": str(src_val) if src_val is not None else "",
                            "status": "MISMATCH",
                            "score_diff": score
                        })

            total_evaluated += sheet_evaluated
            total_exact += sheet_exact
            total_close += sheet_close
            total_mismatch += sheet_mismatch

            acc = round(((sheet_exact + sheet_close) / sheet_evaluated * 100), 2) if sheet_evaluated > 0 else 0.0
            self.stats["sheet_breakdown"].append({
                "sheet_name": sheet_name,
                "evaluated_cells": sheet_evaluated,
                "exact_matches": sheet_exact,
                "close_matches": sheet_close,
                "mismatches": sheet_mismatch,
                "accuracy_pct": acc
            })

        self.progress_callback(85, "Building executive Reconciliation Summary sheet...")

        # Calculate overall accuracy
        overall_accuracy = (
            round(((total_exact + total_close) / total_evaluated * 100), 2)
            if total_evaluated > 0
            else 0.0
        )
        self.stats["total_evaluated"] = total_evaluated
        self.stats["exact_matches"] = total_exact
        self.stats["close_matches"] = total_close
        self.stats["mismatches"] = total_mismatch
        self.stats["accuracy_pct"] = overall_accuracy
        self.stats["sheets_evaluated"] = len(self.stats["sheet_breakdown"])
        self.stats["diff_details"] = diff_details[:200]  # sample of diffs for UI

        # 3. Output Excel Report: Insert a new sheet named "Reconciliation Summary" at the first position
        self._insert_summary_sheet(raw_wb)

        self.progress_callback(95, "Saving formatted reconciled workbook...")
        raw_wb.save(output_file_path)

        self.progress_callback(100, "Reconciliation complete!")
        self.stats["output_file_path"] = output_file_path
        return self.stats

    def _insert_summary_sheet(self, wb: openpyxl.Workbook):
        """Insert Reconciliation Summary sheet at index 0 with KPI cards and tables."""
        # Create sheet at index 0
        summary_sheet = wb.create_sheet(title="Reconciliation Summary", index=0)
        summary_sheet.views.sheetView[0].showGridLines = True

        # Header Title Banner
        summary_sheet.merge_cells("A1:G1")
        title_cell = summary_sheet["A1"]
        title_cell.value = "EXCEL RECONCILIATION SUMMARY REPORT"
        title_cell.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
        title_cell.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")
        summary_sheet.row_dimensions[1].height = 36

        # Subtitle / Run Details
        summary_sheet["A3"] = "Reconciliation Operator:"
        summary_sheet["A3"].font = Font(bold=True)
        summary_sheet["B3"] = self.user_name

        summary_sheet["A4"] = "Execution Timestamp:"
        summary_sheet["A4"].font = Font(bold=True)
        summary_sheet["B4"] = self.stats["timestamp"]

        summary_sheet["D3"] = "Raw Input Workbook:"
        summary_sheet["D3"].font = Font(bold=True)
        summary_sheet["E3"] = os.path.basename(self.raw_file_path)

        summary_sheet["D4"] = "Source Files Count:"
        summary_sheet["D4"].font = Font(bold=True)
        summary_sheet["E4"] = f"{self.stats['source_files_count']} file(s)"

        summary_sheet["A5"] = "Source Workbooks:"
        summary_sheet["A5"].font = Font(bold=True)
        summary_sheet["B5"] = ", ".join(self.stats["source_files"][:4]) + (
            f" (+{len(self.stats['source_files']) - 4} more)" if len(self.stats['source_files']) > 4 else ""
        )

        # KPI Metric Cards Banner (Row 7 to 9)
        kpis = [
            ("TOTAL EVALUATED CELLS", str(self.stats["total_evaluated"]), "2563EB", "DBEAFE", "1E40AF"),
            ("EXACT MATCHES", str(self.stats["exact_matches"]), "16A34A", "DCFCE7", "166534"),
            ("CLOSE MATCHES (YELLOW)", str(self.stats["close_matches"]), "D97706", "FEF3C7", "92400E"),
            ("MISMATCHES / EMPTY (RED)", str(self.stats["mismatches"]), "DC2626", "FEE2E2", "991B1B"),
            ("MATCH ACCURACY (%)", f"{self.stats['accuracy_pct']}%", "4F46E5", "EEF2FF", "3730A3"),
        ]

        col_letters = ["A", "B", "C", "D", "E"]
        for idx, (label, val, border_c, bg_c, text_c) in enumerate(kpis):
            col = col_letters[idx]
            
            # Label
            cell_lbl = summary_sheet[f"{col}7"]
            cell_lbl.value = label
            cell_lbl.font = Font(name="Calibri", size=9, bold=True, color="64748B")
            cell_lbl.fill = PatternFill(start_color=bg_c, end_color=bg_c, fill_type="solid")
            cell_lbl.alignment = Alignment(horizontal="center", vertical="center")
            cell_lbl.border = CELL_BORDER

            # Value
            cell_val = summary_sheet[f"{col}8"]
            cell_val.value = val
            cell_val.font = Font(name="Calibri", size=18, bold=True, color=text_c)
            cell_val.fill = PatternFill(start_color=bg_c, end_color=bg_c, fill_type="solid")
            cell_val.alignment = Alignment(horizontal="center", vertical="center")
            cell_val.border = CELL_BORDER

        summary_sheet.row_dimensions[7].height = 20
        summary_sheet.row_dimensions[8].height = 32

        # Sheet Breakdown Table (Row 11)
        summary_sheet["A11"] = "Detailed Breakdown By Sheet"
        summary_sheet["A11"].font = Font(name="Calibri", size=13, bold=True, color="0F172A")

        headers = ["Sheet Name", "Total Evaluated Cells", "Exact Matches", "Close Matches (Yellow)", "Mismatches (Red)", "Accuracy %"]
        for c_idx, h in enumerate(headers, start=1):
            cell = summary_sheet.cell(row=12, column=c_idx)
            cell.value = h
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = CELL_BORDER
        summary_sheet.row_dimensions[12].height = 24

        curr_r = 13
        for item in self.stats["sheet_breakdown"]:
            row_vals = [
                item["sheet_name"],
                item["evaluated_cells"],
                item["exact_matches"],
                item["close_matches"],
                item["mismatches"],
                f"{item['accuracy_pct']}%"
            ]
            for c_idx, v in enumerate(row_vals, start=1):
                cell = summary_sheet.cell(row=curr_r, column=c_idx)
                cell.value = v
                cell.alignment = Alignment(horizontal="center" if c_idx > 1 else "left", vertical="center")
                cell.border = CELL_BORDER
                # Subtly tint close or mismatch counts
                if c_idx == 4 and item["close_matches"] > 0:
                    cell.fill = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")
                elif c_idx == 5 and item["mismatches"] > 0:
                    cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
            curr_r += 1

        # Formatting Legend / Guide (Below Table)
        curr_r += 2
        summary_sheet.cell(row=curr_r, column=1, value="Formatting Legend & Threshold Rules:").font = Font(bold=True)
        curr_r += 1

        legend_items = [
            ("Normal formatting", "Exact Match (Identical normalized text or identical numeric values)"),
            ("Yellow Highlight (#FFEB9C / #9C6500)", "Close Match (>80% text similarity ratio or within 5% numeric difference)"),
            ("Red Highlight (#FFC7CE / #9C0006)", "Mismatch or Empty/Null Value (Missing record, null cell, or similarity < 80%)")
        ]

        for format_name, desc in legend_items:
            c1 = summary_sheet.cell(row=curr_r, column=1, value=format_name)
            c2 = summary_sheet.cell(row=curr_r, column=2, value=desc)
            if "Yellow" in format_name:
                c1.fill = YELLOW_FILL
                c1.font = YELLOW_FONT
            elif "Red" in format_name:
                c1.fill = RED_FILL
                c1.font = RED_FONT
            else:
                c1.font = Font(bold=True)
            c1.border = CELL_BORDER
            c2.border = CELL_BORDER
            curr_r += 1

        # Auto-fit column widths
        for col in summary_sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            summary_sheet.column_dimensions[col_letter].width = max(max_len + 4, 18)


if __name__ == "__main__":
    import json
    import argparse
    parser = argparse.ArgumentParser(description="Automated Excel Data Reconciler")
    parser.add_argument("--raw", required=True, help="File path to input raw Excel")
    parser.add_argument("--source", required=True, help="File or folder path to source Excel(s)")
    parser.add_argument("--user", default="Operator", help="User name")
    parser.add_argument("--output", default=None, help="Output reconciled Excel file path")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()
    reconciler = ExcelReconciler(
        raw_file_path=args.raw,
        source_path=args.source,
        user_name=args.user,
        progress_callback=lambda pct, msg: None if args.json else print(f"[{pct}%] {msg}")
    )
    result = reconciler.reconcile(args.output)
    if args.json:
        print(json.dumps(result))
    else:
        print("\n--- RECONCILIATION SUMMARY ---")
        print(f"User: {args.user}")
        print(f"Evaluated Cells: {result['total_evaluated']}")
        print(f"Exact Matches: {result['exact_matches']}")
        print(f"Close Matches (Yellow): {result['close_matches']}")
        print(f"Mismatches (Red): {result['mismatches']}")
        print(f"Match Accuracy: {result['accuracy_pct']}%")
        print(f"Saved Report: {result['output_file_path']}")
