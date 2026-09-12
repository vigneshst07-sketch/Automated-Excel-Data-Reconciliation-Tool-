import React from "react";
import { Loader2 } from "lucide-react";

interface ProgressBarProps {
  progressPct: number;
  statusMessage: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progressPct, statusMessage }) => {
  return (
    <div className="bg-white border border-blue-200 rounded-xl p-5 shadow-xs mb-6" id="progress-indicator">
      <div className="flex items-center justify-between text-xs font-semibold mb-2">
        <div className="flex items-center gap-2 text-blue-800">
          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
          <span className="font-mono text-sm">{statusMessage || "Processing workbooks..."}</span>
        </div>
        <span className="font-mono text-sm text-blue-700 font-bold">{Math.round(progressPct)}%</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${Math.max(progressPct, 5)}%` }}
        />
      </div>
    </div>
  );
};
