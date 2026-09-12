# Automated Excel Data Reconciler (Offline Desktop Web Application)

A high-performance, 100% offline desktop web application built with Python (Streamlit & FastAPI + OpenPyXL) for automated Excel reconciliation.

---

## 🌟 Key Features

1. **User Input Parameters**:
   - `raw_file_path`: Path to input raw Excel workbook (`.xlsx`, `.xlsm`)
   - `source_path`: File path OR folder path containing 1 to 4+ source Excel files
   - `user_name`: Name of the reconciliation operator

2. **Intelligent Multi-Source Comparison Logic**:
   - Combines or iterates through all source Excel workbooks in the folder to match against the raw workbook.
   - **Exact Match** -> Standard cell formatting preserved.
   - **Close Match** (e.g. typos, text similarity > 80% with RapidFuzz/difflib or numeric difference within 5%) -> Highlighted **YELLOW** (`#FFEB9C` text `#9C6500`).
   - **Mismatch or Empty/Null Value** -> Highlighted **RED** (`#FFC7CE` text `#9C0006`).

3. **Executive OpenPyXL Output Report**:
   - Directly formats and saves a copy of the reconciled workbook.
   - Inserts an executive **"Reconciliation Summary"** sheet at the **first position (index 0)** with:
     * Operator Name and Execution Timestamp
     * Total Evaluated Cells
     * Total Exact Matches
     * Total Close Matches (Yellow)
     * Total Mismatches / Missing Values (Red)
     * Match Accuracy Percentage (%)
     * Detailed sheet-by-sheet KPI table and formatting legend.

4. **100% Offline Desktop Interfaces**:
   - **Streamlit Reactive UI**: Interactive dashboards, live progress status indicators, interactive sheet table viewers, and instant Excel download.
   - **FastAPI Desktop UI**: Running locally on `http://127.0.0.1:8000`.
   - **CLI Tool**: Direct script reconciliation.

---

## 📁 Project Directory Layout

```
├── app.py                     # Streamlit Desktop Web Application
├── fastapi_app.py             # FastAPI Desktop Web Application (http://127.0.0.1:8000)
├── reconciler.py              # Core reconciliation engine (difflib/RapidFuzz + OpenPyXL)
├── generate_sample_data.py    # Generates realistic demo datasets (Raw + 4 Sources)
├── main.py                    # Unified CLI and application launcher
├── requirements.txt           # Python dependencies
├── data/                      # Sample datasets
│   ├── raw_input.xlsx         # Raw workbook (Invoices, Inventory)
│   └── sources/               # Source folder (1 to 4+ source workbooks)
│       ├── source_1_erp.xlsx
│       ├── source_2_procurement.xlsx
│       ├── source_3_warehouse.xlsx
│       └── source_4_finance.xlsx
└── README.md
```

---

## 🚀 Quickstart & Execution

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Demo Datasets
```bash
python generate_sample_data.py
```

### 3. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Or use the launcher:
```bash
python main.py --mode streamlit
```

### 4. Launch the FastAPI Desktop Application (`http://127.0.0.1:8000`)
```bash
uvicorn fastapi_app:app --host 127.0.0.1 --port 8000
```
Or use the launcher:
```bash
python main.py --mode fastapi --port 8000
```

### 5. Run via Command Line Interface (CLI)
```bash
python reconciler.py --raw data/raw_input.xlsx --source data/sources --user "Operator"
```
