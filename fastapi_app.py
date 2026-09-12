"""
FastAPI Desktop Web Application for Automated Excel Data Reconciliation
Runs locally on http://127.0.0.1:8000 without requiring an internet connection.
"""

import os
import time
import json
import asyncio
from typing import Optional
from fastapi import FastAPI, Request, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from reconciler import ExcelReconciler
from generate_sample_data import generate_samples

app = FastAPI(
    title="Excel Data Reconciler",
    description="Offline Desktop Web Application for Automated Excel Reconciliation"
)

# In-memory progress tracking for local execution
reconciliation_jobs = {}

class ReconcileRequest(BaseModel):
    raw_file_path: str
    source_path: str
    user_name: Optional[str] = "Operator"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Data Reconciler - FastAPI Desktop</title>
    <style>
        :root {
            --bg-color: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border-color: #E2E8F0;
            --primary: #2563EB;
            --primary-hover: #1D4ED8;
            --yellow-bg: #FFEB9C;
            --yellow-text: #9C6500;
            --red-bg: #FFC7CE;
            --red-text: #9C0006;
            --green-bg: #DCFCE7;
            --green-text: #166534;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background: var(--bg-color); color: var(--text-main); padding: 32px 16px; min-height: 100vh; }
        .container { max-width: 1000px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
        h1 { font-size: 24px; font-weight: 700; color: #0F172A; }
        .badge { background: var(--green-bg); color: var(--green-text); font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 9999px; }
        .card { background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .form-group { margin-bottom: 18px; }
        label { display: block; font-size: 14px; font-weight: 600; margin-bottom: 6px; color: #334155; }
        .help-text { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
        input[type="text"] { width: 100%; padding: 10px 14px; font-size: 14px; border: 1px solid var(--border-color); border-radius: 8px; outline: none; transition: border-color 0.2s; }
        input[type="text"]:focus { border-color: var(--primary); }
        .actions { display: flex; gap: 12px; margin-top: 20px; }
        button { cursor: pointer; padding: 10px 20px; font-size: 14px; font-weight: 600; border-radius: 8px; border: none; transition: 0.2s; }
        .btn-primary { background: var(--primary); color: #FFF; }
        .btn-primary:hover { background: var(--primary-hover); }
        .btn-secondary { background: #F1F5F9; color: #334155; border: 1px solid var(--border-color); }
        .btn-secondary:hover { background: #E2E8F0; }
        .progress-bar-container { width: 100%; height: 10px; background: #E2E8F0; border-radius: 9999px; overflow: hidden; margin: 12px 0; }
        .progress-bar { height: 100%; width: 0%; background: var(--primary); transition: width 0.3s; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin: 20px 0; }
        .kpi-card { background: #F8FAFC; border: 1px solid var(--border-color); border-radius: 8px; padding: 16px; text-align: center; }
        .kpi-label { font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
        .kpi-value { font-size: 24px; font-weight: 700; margin-top: 6px; }
        .legend { display: flex; gap: 16px; margin-top: 16px; font-size: 12px; }
        .legend-item { display: flex; align-items: center; gap: 6px; }
        .legend-box { width: 14px; height: 14px; border-radius: 3px; }
        .table-responsive { overflow-x: auto; margin-top: 16px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th, td { padding: 10px 14px; border: 1px solid var(--border-color); text-align: left; }
        th { background: #F1F5F9; font-weight: 600; color: #1E293B; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Automated Excel Data Reconciler</h1>
                <p style="color: var(--text-muted); font-size: 14px;">Local desktop web server running on http://127.0.0.1:8000</p>
            </div>
            <div>
                <span class="badge">● 100% Offline Desktop Mode</span>
            </div>
        </header>

        <div class="card">
            <h2 style="font-size: 18px; margin-bottom: 16px;">Reconciliation Parameters</h2>
            
            <div class="form-group">
                <label for="userName">User Name (user_name)</label>
                <input type="text" id="userName" value="Vignesh Senior Dev" placeholder="Enter operator name">
            </div>

            <div class="form-group">
                <label for="rawFilePath">File Path to Input Raw Excel (raw_file_path)</label>
                <input type="text" id="rawFilePath" value="data/raw_input.xlsx" placeholder="e.g. data/raw_input.xlsx or /path/to/raw.xlsx">
                <div class="help-text">Absolute or relative file path to the target raw workbook to reconcile.</div>
            </div>

            <div class="form-group">
                <label for="sourcePath">File Path OR Folder Path to Source Excel(s) (source_path)</label>
                <input type="text" id="sourcePath" value="data/sources" placeholder="e.g. data/sources or /path/to/sources">
                <div class="help-text">Path to folder containing 1 to 4+ source Excel files, or single file path.</div>
            </div>

            <div class="actions">
                <button class="btn-primary" id="btnRun" onclick="runReconciliation()">▶ Run Reconciliation</button>
                <button class="btn-secondary" id="btnDemo" onclick="generateDemoData()">⚡ Generate Demo Datasets</button>
            </div>

            <div id="progressSection" style="display: none; margin-top: 24px;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 600;">
                    <span id="statusMessage">Processing...</span>
                    <span id="pctText">0%</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar"></div>
                </div>
            </div>
        </div>

        <div class="card" id="resultsCard" style="display: none;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2 style="font-size: 18px;">Reconciliation Report & Summary</h2>
                <a id="btnDownload" href="#" class="btn-primary" style="text-decoration: none; display: inline-block; padding: 8px 16px;">📥 Download Reconciled Excel</a>
            </div>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Evaluated Cells</div>
                    <div class="kpi-value" id="kpiEvaluated">0</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Exact Matches</div>
                    <div class="kpi-value" style="color: #16A34A;" id="kpiExact">0</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Close Matches (Yellow)</div>
                    <div class="kpi-value" style="color: #D97706;" id="kpiClose">0</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Mismatches / Null (Red)</div>
                    <div class="kpi-value" style="color: #DC2626;" id="kpiMismatch">0</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Accuracy Rate</div>
                    <div class="kpi-value" style="color: #4F46E5;" id="kpiAccuracy">0%</div>
                </div>
            </div>

            <div class="legend">
                <div class="legend-item"><div class="legend-box" style="background:#FFF; border:1px solid #CBD5E1;"></div> Exact Match (Normal)</div>
                <div class="legend-item"><div class="legend-box" style="background:var(--yellow-bg); border:1px solid #FCD34D;"></div> Close Match (>80% / 5% diff)</div>
                <div class="legend-item"><div class="legend-box" style="background:var(--red-bg); border:1px solid #FCA5A5;"></div> Mismatch / Missing</div>
            </div>

            <h3 style="font-size: 15px; margin-top: 24px; margin-bottom: 8px;">Discrepancy Details & Flagged Coordinates</h3>
            <div class="table-responsive">
                <table id="diffTable">
                    <thead>
                        <tr>
                            <th>Sheet</th>
                            <th>Cell</th>
                            <th>Header</th>
                            <th>Raw Value</th>
                            <th>Source Value</th>
                            <th>Classification</th>
                        </tr>
                    </thead>
                    <tbody id="diffBody"></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        async function generateDemoData() {
            const btn = document.getElementById('btnDemo');
            btn.innerText = 'Generating...';
            try {
                const res = await fetch('/api/generate-samples', { method: 'POST' });
                const data = await res.json();
                alert(data.message);
            } catch(e) {
                alert('Error generating demo data: ' + e);
            } finally {
                btn.innerText = '⚡ Generate Demo Datasets';
            }
        }

        async function runReconciliation() {
            const userName = document.getElementById('userName').value;
            const rawFilePath = document.getElementById('rawFilePath').value;
            const sourcePath = document.getElementById('sourcePath').value;

            document.getElementById('progressSection').style.display = 'block';
            document.getElementById('resultsCard').style.display = 'none';

            const bar = document.getElementById('progressBar');
            const pctText = document.getElementById('pctText');
            const statusMsg = document.getElementById('statusMessage');

            bar.style.width = '15%';
            pctText.innerText = '15%';
            statusMsg.innerText = 'Scanning source directory and parsing workbooks...';

            try {
                const response = await fetch('/api/reconcile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        raw_file_path: rawFilePath,
                        source_path: sourcePath,
                        user_name: userName
                    })
                });

                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || 'Reconciliation failed');
                }

                bar.style.width = '100%';
                pctText.innerText = '100%';
                statusMsg.innerText = 'Reconciliation completed!';

                const data = await response.json();
                renderResults(data);
            } catch (err) {
                alert('Error: ' + err.message);
                statusMsg.innerText = 'Failed: ' + err.message;
            }
        }

        function renderResults(data) {
            document.getElementById('resultsCard').style.display = 'block';
            document.getElementById('kpiEvaluated').innerText = Number(data.total_evaluated).toLocaleString();
            document.getElementById('kpiExact').innerText = Number(data.exact_matches).toLocaleString();
            document.getElementById('kpiClose').innerText = Number(data.close_matches).toLocaleString();
            document.getElementById('kpiMismatch').innerText = Number(data.mismatches).toLocaleString();
            document.getElementById('kpiAccuracy').innerText = data.accuracy_pct + '%';

            document.getElementById('btnDownload').href = `/api/download?file_path=${encodeURIComponent(data.output_file_path)}`;

            const tbody = document.getElementById('diffBody');
            tbody.innerHTML = '';
            (data.diff_details || []).slice(0, 50).forEach(d => {
                const tr = document.createElement('tr');
                const isClose = d.status === 'CLOSE_MATCH';
                tr.style.backgroundColor = isClose ? '#FFFBEB' : '#FEF2F2';
                tr.innerHTML = `
                    <td><strong>${d.sheet}</strong></td>
                    <td><code>${d.cell}</code></td>
                    <td>${d.header}</td>
                    <td>${d.raw_value}</td>
                    <td>${d.source_value}</td>
                    <td><span style="font-weight:bold; color: ${isClose ? '#9C6500' : '#9C0006'}">${d.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTML_TEMPLATE

@app.post("/api/generate-samples")
def api_generate_samples():
    res = generate_samples("data")
    return {"status": "ok", "message": "Demo Excel datasets generated in 'data/' and 'data/sources/'!"}

@app.post("/api/reconcile")
def api_reconcile(req: ReconcileRequest):
    if not os.path.exists(req.raw_file_path):
        raise HTTPException(status_code=404, detail=f"Raw Excel workbook not found: {req.raw_file_path}")
    if not os.path.exists(req.source_path):
        raise HTTPException(status_code=404, detail=f"Source path not found: {req.source_path}")

    reconciler = ExcelReconciler(
        raw_file_path=req.raw_file_path,
        source_path=req.source_path,
        user_name=req.user_name
    )

    try:
        results = reconciler.reconcile()
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
def api_download(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested file does not exist.")
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI Local Desktop Reconciler at http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
