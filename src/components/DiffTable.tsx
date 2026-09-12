import React, { useState } from "react";
import { DiffDetail } from "../types";
import { Filter, Search, AlertTriangle, XCircle } from "lucide-react";

interface DiffTableProps {
  diffs: DiffDetail[];
}

export const DiffTable: React.FC<DiffTableProps> = ({ diffs }) => {
  const [filter, setFilter] = useState<"ALL" | "CLOSE_MATCH" | "MISMATCH">("ALL");
  const [search, setSearch] = useState("");

  const filtered = diffs.filter((d) => {
    if (filter !== "ALL" && d.status !== filter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      return (
        d.sheet.toLowerCase().includes(q) ||
        d.cell.toLowerCase().includes(q) ||
        d.header.toLowerCase().includes(q) ||
        d.raw_value.toLowerCase().includes(q) ||
        d.source_value.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs" id="discrepancies-table-section">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-4 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900">4. Flagged Cells & Discrepancies Register</h3>
          <p className="text-xs text-slate-500">
            Coordinates requiring review ({filtered.length} of {diffs.length} entries shown)
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search cells..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="text-xs pl-8 pr-3 py-1.5 rounded-lg border border-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg text-xs">
            <button
              type="button"
              onClick={() => setFilter("ALL")}
              className={`px-2.5 py-1 rounded font-semibold transition-colors cursor-pointer ${
                filter === "ALL" ? "bg-white text-slate-900 shadow-xs" : "text-slate-500 hover:text-slate-900"
              }`}
            >
              All ({diffs.length})
            </button>
            <button
              type="button"
              onClick={() => setFilter("CLOSE_MATCH")}
              className={`px-2.5 py-1 rounded font-semibold transition-colors cursor-pointer flex items-center gap-1 ${
                filter === "CLOSE_MATCH" ? "bg-white text-amber-800 shadow-xs" : "text-slate-500 hover:text-slate-900"
              }`}
            >
              <AlertTriangle className="w-3 h-3 text-amber-500" />
              Close ({diffs.filter((d) => d.status === "CLOSE_MATCH").length})
            </button>
            <button
              type="button"
              onClick={() => setFilter("MISMATCH")}
              className={`px-2.5 py-1 rounded font-semibold transition-colors cursor-pointer flex items-center gap-1 ${
                filter === "MISMATCH" ? "bg-white text-red-800 shadow-xs" : "text-slate-500 hover:text-slate-900"
              }`}
            >
              <XCircle className="w-3 h-3 text-red-500" />
              Mismatches ({diffs.filter((d) => d.status === "MISMATCH").length})
            </button>
          </div>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="py-8 text-center text-xs text-slate-400">
          No matching discrepancies found for this filter.
        </div>
      ) : (
        <div className="border border-slate-200 rounded-lg overflow-x-auto max-h-[360px] overflow-y-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-xs">
            <thead className="bg-slate-50 text-slate-600 font-semibold sticky top-0 border-b border-slate-200">
              <tr>
                <th className="px-3.5 py-2.5">Sheet</th>
                <th className="px-3.5 py-2.5">Coordinate</th>
                <th className="px-3.5 py-2.5">Column Header</th>
                <th className="px-3.5 py-2.5">Raw Workbook Value</th>
                <th className="px-3.5 py-2.5">Source Workbook Value</th>
                <th className="px-3.5 py-2.5">Match Classification</th>
                <th className="px-3.5 py-2.5">Score / Variance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {filtered.map((d, idx) => {
                const isClose = d.status === "CLOSE_MATCH";
                return (
                  <tr
                    key={`diff-${idx}`}
                    className="hover:bg-slate-50 transition-colors"
                    style={{
                      backgroundColor: isClose ? "#FFFDF5" : "#FFF9F9"
                    }}
                  >
                    <td className="px-3.5 py-2 font-sans font-medium text-slate-900">{d.sheet}</td>
                    <td className="px-3.5 py-2 font-bold text-blue-600">{d.cell}</td>
                    <td className="px-3.5 py-2 font-sans text-slate-600">{d.header}</td>
                    <td className="px-3.5 py-2 text-slate-900 font-semibold">{d.raw_value || <span className="text-slate-300 italic font-normal">(empty)</span>}</td>
                    <td className="px-3.5 py-2 text-slate-900 font-semibold">{d.source_value || <span className="text-slate-300 italic font-normal">(empty)</span>}</td>
                    <td className="px-3.5 py-2 font-sans">
                      <span
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-bold"
                        style={{
                          backgroundColor: isClose ? "#FFEB9C" : "#FFC7CE",
                          color: isClose ? "#9C6500" : "#9C0006"
                        }}
                      >
                        {isClose ? "Close Match" : "Mismatch / Null"}
                      </span>
                    </td>
                    <td className="px-3.5 py-2 text-slate-500 text-[11px]">
                      {isClose ? `${d.score_diff}% similarity` : "Discrepancy"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
