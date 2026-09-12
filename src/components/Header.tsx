import React from "react";
import { FileSpreadsheet, ShieldCheck, Cpu } from "lucide-react";

interface HeaderProps {
  userName: string;
}

export const Header: React.FC<HeaderProps> = ({ userName }) => {
  return (
    <header className="border-b border-slate-200 bg-white px-6 py-4 shadow-xs" id="app-header">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-xs">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Excel Data Reconciler</h1>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                <ShieldCheck className="w-3.5 h-3.5" /> Offline Desktop Engine
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Automated multi-source workbook reconciliation with RapidFuzz similarity & OpenPyXL reporting
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5 flex items-center gap-2">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-500">Operator:</span>
            <span className="font-semibold text-slate-700">{userName || "Reconciliation Operator"}</span>
          </div>
          <div className="bg-slate-50 border border-slate-200 rounded-md px-3 py-1.5 font-mono text-slate-600">
            Python 3.11 • OpenPyXL
          </div>
        </div>
      </div>
    </header>
  );
};
