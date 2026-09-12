import React, { useState } from "react";
import { SheetData, CellData } from "../types";
import { Table, Eye, Info } from "lucide-react";

interface ExcelViewerProps {
  sheetData: SheetData | null;
  onSelectSheet: (sheetName: string) => void;
  isLoading: boolean;
}

export const ExcelViewer: React.FC<ExcelViewerProps> = ({
  sheetData,
  onSelectSheet,
  isLoading
}) => {
  const [selectedCell, setSelectedCell] = useState<CellData | null>(null);

  if (!sheetData) {
    return null;
  }

  const getCellClassName = (cell: CellData): string => {
    let classes = "px-3 py-2 text-xs border border-slate-200 transition-colors cursor-pointer ";

    if (cell.fill === "YELLOW") {
      classes += "font-bold select-all ";
    } else if (cell.fill === "RED") {
      classes += "font-bold select-all ";
    } else if (cell.fill === "HEADER_DARK") {
      classes += "bg-slate-900 text-white font-bold text-center ";
    } else if (cell.fill === "HEADER_LIGHT") {
      classes += "bg-slate-100 font-semibold text-slate-700 ";
    } else if (cell.row === 1) {
      classes += "bg-slate-800 text-white font-semibold text-center ";
    } else {
      classes += "bg-white text-slate-800 hover:bg-slate-50 ";
    }

    if (selectedCell?.coord === cell.coord) {
      classes += "ring-2 ring-blue-600 z-10 relative ";
    }

    return classes;
  };

  const getCellStyle = (cell: CellData): React.CSSProperties => {
    if (cell.fill === "YELLOW") {
      return { backgroundColor: "#FFEB9C", color: "#9C6500" };
    }
    if (cell.fill === "RED") {
      return { backgroundColor: "#FFC7CE", color: "#9C0006" };
    }
    return {};
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs" id="excel-workbook-viewer">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-slate-500" />
          <h3 className="text-sm font-bold text-slate-900">3. Interactive Reconciled Workbook Viewer</h3>
          <span className="text-xs text-slate-400">| Direct OpenPyXL format preview</span>
        </div>

        {/* Sheet Tabs */}
        <div className="flex flex-wrap items-center gap-1.5" id="sheet-tabs-container">
          {sheetData.sheet_names.map((name) => {
            const isActive = name === sheetData.active_sheet;
            return (
              <button
                key={name}
                type="button"
                onClick={() => onSelectSheet(name)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors cursor-pointer ${
                  isActive
                    ? "bg-slate-900 text-white shadow-xs"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200 hover:text-slate-900"
                }`}
              >
                {name === "Reconciliation Summary" ? "★ Summary Sheet" : name}
              </button>
            );
          })}
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-xs text-slate-400 font-mono">
          Loading sheet data from Python engine...
        </div>
      ) : (
        <div className="space-y-4">
          {/* Cell Inspector Bar */}
          {selectedCell && (
            <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-between text-xs text-blue-900">
              <div className="flex items-center gap-3">
                <Eye className="w-4 h-4 text-blue-600" />
                <span>
                  Selected Cell: <strong className="font-mono text-sm">{selectedCell.coord}</strong>
                </span>
                <span>
                  Value: <strong className="font-mono bg-white px-2 py-0.5 rounded border border-blue-200">{selectedCell.val || "(empty)"}</strong>
                </span>
                <span>
                  Classification:{" "}
                  <strong
                    className="px-2 py-0.5 rounded font-bold"
                    style={{
                      backgroundColor: selectedCell.fill === "YELLOW" ? "#FFEB9C" : selectedCell.fill === "RED" ? "#FFC7CE" : "#E2E8F0",
                      color: selectedCell.fill === "YELLOW" ? "#9C6500" : selectedCell.fill === "RED" ? "#9C0006" : "#1E293B"
                    }}
                  >
                    {selectedCell.fill === "YELLOW"
                      ? "Close Match (>80% similarity / 5% diff)"
                      : selectedCell.fill === "RED"
                      ? "Mismatch or Empty/Null Value"
                      : selectedCell.row === 1 || selectedCell.fill.startsWith("HEADER")
                      ? "Table Header"
                      : "Exact Match (Normal)"}
                  </strong>
                </span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedCell(null)}
                className="text-blue-500 hover:text-blue-800 text-xs font-semibold cursor-pointer"
              >
                Clear
              </button>
            </div>
          )}

          {/* Spreadsheet Table Container */}
          <div className="border border-slate-200 rounded-lg overflow-x-auto max-h-[480px] overflow-y-auto">
            <table className="min-w-full divide-y divide-slate-200 text-left border-collapse">
              <tbody>
                {sheetData.rows.map((row, rIdx) => (
                  <tr key={`row-${rIdx}`} className="divide-x divide-slate-200">
                    {/* Row Index indicator */}
                    <td className="w-10 px-2 py-1 text-[10px] font-mono text-slate-400 bg-slate-50 text-center select-none sticky left-0 border-r border-slate-200">
                      {rIdx + 1}
                    </td>

                    {row.map((cell, cIdx) => (
                      <td
                        key={`cell-${rIdx}-${cIdx}`}
                        onClick={() => setSelectedCell(cell)}
                        className={getCellClassName(cell)}
                        style={getCellStyle(cell)}
                        title={`Cell: ${cell.coord} | Value: ${cell.val}`}
                      >
                        <span className="truncate block max-w-[240px]">
                          {cell.val !== "" ? cell.val : <span className="text-slate-300 italic">null</span>}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <div className="flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5" />
              <span>Click on any cell to inspect its coordinate, values, and status.</span>
            </div>
            <span>Showing top evaluated rows</span>
          </div>
        </div>
      )}
    </div>
  );
};
