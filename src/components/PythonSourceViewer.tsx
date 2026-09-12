import React, { useState, useEffect } from "react";
import { Terminal, Copy, Check, FileCode, ExternalLink } from "lucide-react";

export const PythonSourceViewer: React.FC = () => {
  const [files, setFiles] = useState<Record<string, string>>({});
  const [selectedFile, setSelectedFile] = useState<string>("app.py");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch("/api/code-files")
      .then((res) => res.json())
      .then((data) => setFiles(data))
      .catch((err) => console.error("Could not load code files", err));
  }, []);

  const handleCopy = () => {
    const code = files[selectedFile] || "";
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const fileNames = Object.keys(files);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs" id="python-source-viewer-section">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 mb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-slate-700" />
            <h3 className="text-sm font-bold text-slate-900">5. Python & Streamlit Source Code Repository</h3>
          </div>
          <p className="text-xs text-slate-500">
            Offline desktop deployment files (Streamlit UI, FastAPI http://127.0.0.1:8000, Reconciler engine, requirements.txt)
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors cursor-pointer"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
            {copied ? "Copied!" : "Copy File"}
          </button>
        </div>
      </div>

      {/* File Tabs */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {fileNames.map((name) => (
          <button
            key={name}
            type="button"
            onClick={() => setSelectedFile(name)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono rounded-lg transition-colors cursor-pointer ${
              selectedFile === name
                ? "bg-blue-600 text-white font-bold"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            <FileCode className="w-3.5 h-3.5" />
            {name}
          </button>
        ))}
      </div>

      {/* Code Display */}
      <div className="relative rounded-lg bg-slate-900 text-slate-100 p-4 font-mono text-xs overflow-x-auto max-h-[420px] overflow-y-auto">
        <pre>{files[selectedFile] || "Loading source code..."}</pre>
      </div>

      {/* Local execution instructions */}
      <div className="mt-4 p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1">
        <div className="font-semibold text-slate-800 flex items-center gap-1">
          <ExternalLink className="w-3.5 h-3.5 text-blue-600" />
          Offline Desktop Execution Quickstart:
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          <div>
            <span className="font-bold text-slate-700">Streamlit Desktop:</span>
            <code className="block bg-slate-200/70 px-2 py-1 rounded text-slate-900 font-mono mt-0.5">
              streamlit run app.py
            </code>
          </div>
          <div>
            <span className="font-bold text-slate-700">FastAPI Desktop (127.0.0.1:8000):</span>
            <code className="block bg-slate-200/70 px-2 py-1 rounded text-slate-900 font-mono mt-0.5">
              uvicorn fastapi_app:app --host 127.0.0.1 --port 8000
            </code>
          </div>
        </div>
      </div>
    </div>
  );
};
