import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { InputPanel } from "./components/InputPanel";
import { ProgressBar } from "./components/ProgressBar";
import { KpiCards } from "./components/KpiCards";
import { ExcelViewer } from "./components/ExcelViewer";
import { DiffTable } from "./components/DiffTable";
import { PythonSourceViewer } from "./components/PythonSourceViewer";
import { ReconciliationStats, SheetData } from "./types";
import { Table, AlertTriangle, FileCode } from "lucide-react";

export default function App() {
  const [userName, setUserName] = useState<string>("Vignesh Senior Dev");
  const [rawFilePath, setRawFilePath] = useState<string>("data/raw_input.xlsx");
  const [sourcePath, setSourcePath] = useState<string>("data/sources");

  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [progressPct, setProgressPct] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>("");

  const [stats, setStats] = useState<ReconciliationStats | null>(null);
  const [sheetData, setSheetData] = useState<SheetData | null>(null);
  const [isSheetLoading, setIsSheetLoading] = useState<boolean>(false);
  const [sourceFilesCount, setSourceFilesCount] = useState<number>(4);

  const [viewTab, setViewTab] = useState<"viewer" | "discrepancies" | "code">("viewer");

  // Load initial files & run demo reconciliation on startup
  useEffect(() => {
    fetch("/api/files")
      .then((res) => res.json())
      .then((data) => {
        if (data.sourceFiles && data.sourceFiles.length > 0) {
          setSourceFilesCount(data.sourceFiles.length);
        } else {
          // Trigger sample generation if empty
          handleGenerateSamples();
        }
      })
      .catch(() => {
        // demo fallback
      });

    // Run initial demo reconciliation
    handleRunReconciliation(false);
  }, []);

  const handleGenerateSamples = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch("/api/generate-samples", { method: "POST" });
      const data = await res.json();
      if (res.ok) {
        setSourceFilesCount(4);
        await handleRunReconciliation(true);
      } else {
        alert("Could not generate samples: " + data.error);
      }
    } catch (e: any) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  };

  const loadSheetData = async (filePath: string, sheetName?: string) => {
    setIsSheetLoading(true);
    try {
      const url = `/api/sheet-data?file_path=${encodeURIComponent(filePath)}${
        sheetName ? `&sheet_name=${encodeURIComponent(sheetName)}` : ""
      }`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setSheetData(data);
      }
    } catch (e) {
      console.error("Failed to load sheet data", e);
    } finally {
      setIsSheetLoading(false);
    }
  };

  const handleRunReconciliation = async (showStepAnimation = true) => {
    setIsProcessing(true);
    setProgressPct(10);
    setStatusMessage("Scanning source directory and inspecting workbooks...");

    if (showStepAnimation) {
      setTimeout(() => {
        setProgressPct(35);
        setStatusMessage("Parsing raw workbook and indexing multi-source records...");
      }, 300);
      setTimeout(() => {
        setProgressPct(65);
        setStatusMessage("Evaluating exact matches, RapidFuzz text similarity & numeric tolerance...");
      }, 700);
      setTimeout(() => {
        setProgressPct(85);
        setStatusMessage("Applying OpenPyXL color highlights & generating Reconciliation Summary sheet...");
      }, 1100);
    }

    try {
      const res = await fetch("/api/reconcile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          raw_file_path: rawFilePath,
          source_path: sourcePath,
          user_name: userName
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Reconciliation failed");
      }

      setProgressPct(100);
      setStatusMessage("Reconciliation completed successfully!");

      const data: ReconciliationStats = await res.json();
      setStats(data);
      if (data.source_files_count) {
        setSourceFilesCount(data.source_files_count);
      }

      // Load Reconciliation Summary sheet
      if (data.output_file_path) {
        await loadSheetData(data.output_file_path, "Reconciliation Summary");
      }
    } catch (e: any) {
      setStatusMessage(`Error: ${e.message}`);
      alert(`Reconciliation error: ${e.message}`);
    } finally {
      setTimeout(() => {
        setIsProcessing(false);
      }, 600);
    }
  };

  const handleSelectSheet = (sheetName: string) => {
    if (stats?.output_file_path) {
      loadSheetData(stats.output_file_path, sheetName);
    }
  };

  const handleDownload = () => {
    if (stats?.output_file_path) {
      window.location.href = `/api/download?file_path=${encodeURIComponent(stats.output_file_path)}`;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans" id="main-application-container">
      {/* Header */}
      <Header userName={userName} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Input Parameters Panel */}
        <InputPanel
          userName={userName}
          setUserName={setUserName}
          rawFilePath={rawFilePath}
          setRawFilePath={setRawFilePath}
          sourcePath={sourcePath}
          setSourcePath={setSourcePath}
          onRunReconciliation={() => handleRunReconciliation(true)}
          onGenerateSamples={handleGenerateSamples}
          isProcessing={isProcessing}
          isGenerating={isGenerating}
          sourceFilesCount={sourceFilesCount}
        />

        {/* Live Progress Bar during execution */}
        {isProcessing && (
          <ProgressBar progressPct={progressPct} statusMessage={statusMessage} />
        )}

        {/* Results Section */}
        {stats && (
          <div className="space-y-6">
            {/* KPI Metrics */}
            <KpiCards stats={stats} onDownload={handleDownload} />

            {/* View Navigation Tabs */}
            <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
              <button
                type="button"
                onClick={() => setViewTab("viewer")}
                className={`inline-flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg transition-colors cursor-pointer ${
                  viewTab === "viewer"
                    ? "bg-slate-900 text-white shadow-xs"
                    : "text-slate-600 hover:bg-slate-200"
                }`}
              >
                <Table className="w-4 h-4" />
                Workbook Sheet Viewer
              </button>

              <button
                type="button"
                onClick={() => setViewTab("discrepancies")}
                className={`inline-flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg transition-colors cursor-pointer ${
                  viewTab === "discrepancies"
                    ? "bg-slate-900 text-white shadow-xs"
                    : "text-slate-600 hover:bg-slate-200"
                }`}
              >
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Discrepancies Register ({stats.diff_details?.length || 0})
              </button>

              <button
                type="button"
                onClick={() => setViewTab("code")}
                className={`inline-flex items-center gap-2 px-4 py-2 text-xs font-bold rounded-lg transition-colors cursor-pointer ${
                  viewTab === "code"
                    ? "bg-slate-900 text-white shadow-xs"
                    : "text-slate-600 hover:bg-slate-200"
                }`}
              >
                <FileCode className="w-4 h-4 text-blue-500" />
                Python & Streamlit Source Files
              </button>
            </div>

            {/* Tab 1: Sheet Viewer */}
            {viewTab === "viewer" && (
              <ExcelViewer
                sheetData={sheetData}
                onSelectSheet={handleSelectSheet}
                isLoading={isSheetLoading}
              />
            )}

            {/* Tab 2: Discrepancies Register */}
            {viewTab === "discrepancies" && (
              <DiffTable diffs={stats.diff_details || []} />
            )}

            {/* Tab 3: Python & Streamlit Code Repository */}
            {viewTab === "code" && <PythonSourceViewer />}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Automated Excel Data Reconciliation Engine • 100% Offline Desktop Mode</span>
          <span>OpenPyXL • RapidFuzz/difflib • Streamlit • FastAPI (127.0.0.1:8000)</span>
        </div>
      </footer>
    </div>
  );
}
