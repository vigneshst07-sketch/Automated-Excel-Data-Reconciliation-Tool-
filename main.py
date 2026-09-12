"""
Main Application Launcher for Excel Data Reconciler
Provides simple execution across:
1. Streamlit Desktop Web UI: python main.py --mode streamlit
2. FastAPI Desktop Web UI:   python main.py --mode fastapi --port 8000
3. Command Line Execution:   python main.py --mode cli --raw data/raw_input.xlsx --source data/sources
"""

import sys
import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Automated Excel Data Reconciler Launcher")
    parser.add_argument(
        "--mode",
        choices=["streamlit", "fastapi", "cli"],
        default="streamlit",
        help="Interface mode to launch (default: streamlit)"
    )
    parser.add_argument("--port", type=int, default=8000, help="Port for FastAPI or Streamlit (default: 8000)")
    parser.add_argument("--raw", default="data/raw_input.xlsx", help="Raw Excel file path (for CLI mode)")
    parser.add_argument("--source", default="data/sources", help="Source Excel folder or file (for CLI mode)")
    parser.add_argument("--user", default="Reconciliation Operator", help="Operator username")

    args = parser.parse_args()

    # Ensure demo data exists if data/ does not
    if not os.path.exists("data/raw_input.xlsx"):
        print("[Launcher] Generating demo sample data in 'data/'...")
        from generate_sample_data import generate_samples
        generate_samples()

    if args.mode == "streamlit":
        print(f"[Launcher] Launching Streamlit Desktop UI on port {args.port}...")
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(args.port),
            "--server.address", "127.0.0.1",
            "--browser.gatherUsageStats", "false"
        ]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n[Launcher] Streamlit stopped.")

    elif args.mode == "fastapi":
        print(f"[Launcher] Launching FastAPI Desktop UI on http://127.0.0.1:{args.port}...")
        import uvicorn
        from fastapi_app import app
        uvicorn.run(app, host="127.0.0.1", port=args.port)

    elif args.mode == "cli":
        print("[Launcher] Executing CLI Reconciliation...")
        from reconciler import ExcelReconciler
        reconciler = ExcelReconciler(
            raw_file_path=args.raw,
            source_path=args.source,
            user_name=args.user,
            progress_callback=lambda pct, msg: print(f"[{pct}%] {msg}")
        )
        stats = reconciler.reconcile()
        print("\nReconciliation Completed:")
        print(f"Evaluated Cells: {stats['total_evaluated']}")
        print(f"Accuracy Rate:   {stats['accuracy_pct']}%")
        print(f"Report File:     {stats['output_file_path']}")

if __name__ == "__main__":
    main()
