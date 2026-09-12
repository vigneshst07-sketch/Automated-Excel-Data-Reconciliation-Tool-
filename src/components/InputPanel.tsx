import React from "react";
import { Play, Sparkles, FolderArchive, FileText, User, HelpCircle } from "lucide-react";

interface InputPanelProps {
  userName: string;
  setUserName: (val: string) => void;
  rawFilePath: string;
  setRawFilePath: (val: string) => void;
  sourcePath: string;
  setSourcePath: (val: string) => void;
  onRunReconciliation: () => void;
  onGenerateSamples: () => void;
  isProcessing: boolean;
  isGenerating: boolean;
  sourceFilesCount: number;
}

export const InputPanel: React.FC<InputPanelProps> = ({
  userName,
  setUserName,
  rawFilePath,
  setRawFilePath,
  sourcePath,
  setSourcePath,
  onRunReconciliation,
  onGenerateSamples,
  isProcessing,
  isGenerating,
  sourceFilesCount
}) => {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs" id="input-parameters-panel">
      <div className="flex items-center justify-between pb-4 mb-5 border-b border-slate-100">
        <div>
          <h2 className="text-base font-bold text-slate-900">1. Reconciliation Parameters</h2>
          <p className="text-xs text-slate-500">Configure target files, multi-source folder path, and operator ID</p>
        </div>
        <button
          id="btn-generate-samples"
          type="button"
          onClick={onGenerateSamples}
          disabled={isGenerating || isProcessing}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors disabled:opacity-50 cursor-pointer"
        >
          <Sparkles className="w-3.5 h-3.5 text-amber-500" />
          {isGenerating ? "Generating Samples..." : "Generate Demo Datasets"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* User Name */}
        <div>
          <label htmlFor="user-name-input" className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5 flex items-center gap-1.5">
            <User className="w-3.5 h-3.5 text-slate-400" />
            User Name (<code className="lowercase text-slate-500">user_name</code>)
          </label>
          <input
            id="user-name-input"
            type="text"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            placeholder="e.g. Vignesh Senior Dev"
            className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-slate-50/50"
          />
          <span className="block text-[11px] text-slate-400 mt-1">Recorded on Reconciliation Summary sheet</span>
        </div>

        {/* Raw File Path */}
        <div>
          <label htmlFor="raw-file-input" className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5 flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5 text-slate-400" />
            Input Raw Excel (<code className="lowercase text-slate-500">raw_file_path</code>)
          </label>
          <div className="relative">
            <input
              id="raw-file-input"
              type="text"
              value={rawFilePath}
              onChange={(e) => setRawFilePath(e.target.value)}
              placeholder="data/raw_input.xlsx"
              className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-slate-50/50 font-mono text-xs"
            />
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
            <span>Relative or absolute workbook path</span>
            <button
              type="button"
              onClick={() => setRawFilePath("data/raw_input.xlsx")}
              className="text-blue-600 hover:underline cursor-pointer"
            >
              Reset to demo
            </button>
          </div>
        </div>

        {/* Source Path */}
        <div>
          <label htmlFor="source-path-input" className="block text-xs font-semibold uppercase tracking-wider text-slate-600 mb-1.5 flex items-center gap-1.5">
            <FolderArchive className="w-3.5 h-3.5 text-slate-400" />
            Source Excel(s) (<code className="lowercase text-slate-500">source_path</code>)
          </label>
          <div className="relative">
            <input
              id="source-path-input"
              type="text"
              value={sourcePath}
              onChange={(e) => setSourcePath(e.target.value)}
              placeholder="data/sources"
              className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-slate-50/50 font-mono text-xs"
            />
          </div>
          <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1">
            <span>Folder with 1 to 4+ files or single file</span>
            <span className="font-semibold text-slate-600">{sourceFilesCount} file(s) found</span>
          </div>
        </div>
      </div>

      {/* Threshold Information Legend */}
      <div className="mt-5 p-3.5 rounded-lg bg-slate-50 border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-600">
          <HelpCircle className="w-4 h-4 text-slate-400" />
          <span className="font-semibold text-slate-700">Matching Logic:</span>
          <span>Exact (Normal)</span>
          <span className="text-slate-300">•</span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-bold" style={{ backgroundColor: "#FFEB9C", color: "#9C6500" }}>
            Yellow: Close Match (&gt;80% text or &le;5% num)
          </span>
          <span className="text-slate-300">•</span>
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-bold" style={{ backgroundColor: "#FFC7CE", color: "#9C0006" }}>
            Red: Mismatch / Null / Missing
          </span>
        </div>

        <button
          id="btn-run-reconciliation"
          type="button"
          onClick={onRunReconciliation}
          disabled={isProcessing}
          className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-semibold rounded-lg text-white bg-blue-600 hover:bg-blue-700 shadow-sm transition-all disabled:opacity-50 cursor-pointer"
        >
          <Play className="w-4 h-4 fill-white" />
          {isProcessing ? "Reconciling Workbooks..." : "Run Automated Reconciliation"}
        </button>
      </div>
    </div>
  );
};
