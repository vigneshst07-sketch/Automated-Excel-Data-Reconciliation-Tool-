import React from "react";
import { Layers, CheckCircle2, AlertTriangle, XCircle, Percent, Download } from "lucide-react";
import { ReconciliationStats } from "../types";

interface KpiCardsProps {
  stats: ReconciliationStats;
  onDownload: () => void;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ stats, onDownload }) => {
  return (
    <div className="space-y-4" id="kpi-metrics-section">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-900">2. Reconciliation Summary Metrics</h2>
          <p className="text-xs text-slate-500">
            Completed at {stats.timestamp} across {stats.source_files_count} source workbook(s)
          </p>
        </div>
        <button
          id="btn-download-reconciled-excel"
          type="button"
          onClick={onDownload}
          className="inline-flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg text-white bg-emerald-600 hover:bg-emerald-700 shadow-xs transition-colors cursor-pointer"
        >
          <Download className="w-4 h-4" />
          Download Reconciled Excel (.xlsx)
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {/* Total Evaluated */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Evaluated Cells</span>
            <Layers className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 font-mono">
            {stats.total_evaluated.toLocaleString()}
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            Across {stats.sheets_evaluated} sheet(s)
          </span>
        </div>

        {/* Exact Matches */}
        <div className="bg-white border border-emerald-200 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-emerald-600 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-800">Exact Matches</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-bold text-emerald-700 font-mono">
            {stats.exact_matches.toLocaleString()}
          </div>
          <span className="text-[11px] text-emerald-600 font-medium mt-1 block">
            Normal formatting
          </span>
        </div>

        {/* Close Matches (Yellow) */}
        <div className="border rounded-xl p-4 shadow-xs" style={{ backgroundColor: "#FFFDF0", borderColor: "#FDE68A" }}>
          <div className="flex items-center justify-between mb-2" style={{ color: "#9C6500" }}>
            <span className="text-[11px] font-bold uppercase tracking-wider">Close Matches</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold font-mono" style={{ color: "#9C6500" }}>
            {stats.close_matches.toLocaleString()}
          </div>
          <span className="text-[11px] font-semibold mt-1 block" style={{ color: "#9C6500" }}>
            Yellow highlight (#FFEB9C)
          </span>
        </div>

        {/* Mismatches (Red) */}
        <div className="border rounded-xl p-4 shadow-xs" style={{ backgroundColor: "#FFF5F5", borderColor: "#FECACA" }}>
          <div className="flex items-center justify-between mb-2" style={{ color: "#9C0006" }}>
            <span className="text-[11px] font-bold uppercase tracking-wider">Mismatches / Null</span>
            <XCircle className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold font-mono" style={{ color: "#9C0006" }}>
            {stats.mismatches.toLocaleString()}
          </div>
          <span className="text-[11px] font-semibold mt-1 block" style={{ color: "#9C0006" }}>
            Red highlight (#FFC7CE)
          </span>
        </div>

        {/* Accuracy % */}
        <div className="bg-white border border-indigo-200 rounded-xl p-4 shadow-xs">
          <div className="flex items-center justify-between text-indigo-500 mb-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700">Match Accuracy</span>
            <Percent className="w-4 h-4" />
          </div>
          <div className="text-2xl font-bold text-indigo-700 font-mono">
            {stats.accuracy_pct}%
          </div>
          <span className="text-[11px] text-indigo-600 mt-1 block font-medium">
            (Exact + Close) / Total
          </span>
        </div>
      </div>
    </div>
  );
};
