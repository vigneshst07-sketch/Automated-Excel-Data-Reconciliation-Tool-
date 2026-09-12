export interface SheetBreakdown {
  sheet_name: string;
  evaluated_cells: number;
  exact_matches: number;
  close_matches: number;
  mismatches: number;
  accuracy_pct: number;
}

export interface DiffDetail {
  sheet: string;
  cell: string;
  row: number;
  col: number;
  header: string;
  raw_value: string;
  source_value: string;
  status: "CLOSE_MATCH" | "MISMATCH";
  score_diff: number;
}

export interface ReconciliationStats {
  total_evaluated: number;
  exact_matches: number;
  close_matches: number;
  mismatches: number;
  accuracy_pct: number;
  sheets_evaluated: number;
  source_files_count: number;
  source_files: string[];
  timestamp: string;
  sheet_breakdown: SheetBreakdown[];
  diff_details?: DiffDetail[];
  output_file_path?: string;
}

export interface CellData {
  val: string;
  fill: "NORMAL" | "YELLOW" | "RED" | "HEADER_DARK" | "HEADER_LIGHT";
  coord: string;
  row: number;
  col: number;
}

export interface SheetData {
  sheet_names: string[];
  active_sheet: string;
  rows: CellData[][];
}
