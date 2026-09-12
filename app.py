"""
Automated Excel Data Reconciler - Streamlit Application
A fully offline desktop web application for automated Excel data reconciliation.
"""

import os
import time
import tempfile
import pandas as pd
import streamlit as st
import openpyxl
from reconciler import ExcelReconciler
from generate_sample_data import generate_samples

# Page Configuration
st.set_page_config(
    page_title="Excel Data Reconciler",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling to adhere to high contrast, clean typography and exact color highlights
st.markdown("""
<style>
    .main-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-val {
        font-size: 1.75rem;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-lbl {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-offline {
        display: inline-block;
        background-color: #DCFCE7;
        color: #166534;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 9999px;
        border: 1px solid #BBF7D0;
    }
    .cell-yellow {
        background-color: #FFEB9C !important;
        color: #9C6500 !important;
        font-weight: bold;
    }
    .cell-red {
        background-color: #FFC7CE !important;
        color: #9C0006 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
col_hdr_1, col_hdr_2 = st.columns([4, 1])
with col_hdr_1:
    st.markdown('<div class="main-title">Automated Excel Data Reconciler</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Offline multi-source workbook comparison with rapid fuzzy matching & OpenPyXL reporting</div>', unsafe_allow_html=True)
with col_hdr_2:
    st.markdown('<div style="text-align: right; padding-top: 10px;"><span class="badge-offline">● Fully Offline Ready</span></div>', unsafe_allow_html=True)

st.divider()

# Sidebar: Inputs & Configuration
with st.sidebar:
    st.subheader("1. Configuration & Inputs")
    user_name = st.text_input("User Name (`user_name`)", value=st.session_state.get("user_name", "Reconciliation Operator"))

    st.markdown("---")
    input_mode = st.radio("Input Source Mode", ["Local File Paths / Folders", "Upload Files via Browser"])

    raw_path_input = ""
    source_path_input = ""
    raw_uploaded = None
    sources_uploaded = []

    if input_mode == "Local File Paths / Folders":
        st.markdown("**File Path to Raw Excel (`raw_file_path`)**")
        raw_path_input = st.text_input(
            "Raw File Path",
            value=st.session_state.get("raw_path", "data/raw_input.xlsx"),
            label_visibility="collapsed"
        )

        st.markdown("**Path to Source Excel(s) (`source_path`)**")
        st.caption("Enter folder path containing 1 to 4+ Excel files, or a specific file path:")
        source_path_input = st.text_input(
            "Source Path",
            value=st.session_state.get("source_path", "data/sources"),
            label_visibility="collapsed"
        )
    else:
        raw_uploaded = st.file_uploader("Input Raw Excel (.xlsx)", type=["xlsx", "xlsm"])
        sources_uploaded = st.file_uploader(
            "Source Excel(s) (Select 1 to 4+ files)",
            type=["xlsx", "xlsm"],
            accept_multiple_files=True
        )

    st.markdown("---")
    st.subheader("Quick Test Data")
    if st.button("Generate Demo Datasets", use_container_width=True):
        with st.spinner("Generating sample datasets in 'data/' directory..."):
            paths = generate_samples()
            st.session_state["raw_path"] = paths["raw"]
            st.session_state["source_path"] = paths["sources_dir"]
            st.success("Sample workbooks generated in `data/` and `data/sources`!")
            st.rerun()

    st.markdown("---")
    st.markdown("""
    **Comparison Thresholds:**
    - **Exact Match**: Normal formatting
    - **Close Match**: Text similarity > 80% or Numeric diff ≤ 5% (<span style="color:#9C6500; font-weight:bold;">#FFEB9C Yellow</span>)
    - **Mismatch/Null**: Discrepancies or empty cells (<span style="color:#9C0006; font-weight:bold;">#FFC7CE Red</span>)
    """, unsafe_allow_html=True)

# Reconciliation Trigger
start_reconciliation = st.button("▶ Run Automated Reconciliation", type="primary", use_container_width=True)

# Container for execution
progress_container = st.empty()
status_text = st.empty()

if start_reconciliation:
    # Resolve file paths
    final_raw_path = ""
    final_source_path = ""

    if input_mode == "Local File Paths / Folders":
        final_raw_path = raw_path_input.strip()
        final_source_path = source_path_input.strip()
    else:
        if not raw_uploaded or not sources_uploaded:
            st.error("Please upload both a raw workbook and at least one source workbook.")
            st.stop()

        temp_dir = tempfile.mkdtemp(prefix="reconciler_")
        final_raw_path = os.path.join(temp_dir, raw_uploaded.name)
        with open(final_raw_path, "wb") as f:
            f.write(raw_uploaded.read())

        sources_dir = os.path.join(temp_dir, "sources")
        os.makedirs(sources_dir, exist_ok=True)
        for s_file in sources_uploaded:
            sf_path = os.path.join(sources_dir, s_file.name)
            with open(sf_path, "wb") as f:
                f.write(s_file.read())
        final_source_path = sources_dir

    if not os.path.exists(final_raw_path):
        st.error(f"Raw Excel file not found: `{final_raw_path}`. Please verify path or click 'Generate Demo Datasets'.")
        st.stop()

    if not os.path.exists(final_source_path):
        st.error(f"Source Excel path not found: `{final_source_path}`. Please verify path.")
        st.stop()

    progress_bar = progress_container.progress(0)
    status_box = status_text.info("Starting reconciliation process...")

    def update_progress(pct: float, message: str):
        progress_bar.progress(int(pct))
        status_box.info(f"[{int(pct)}%] {message}")
        time.sleep(0.05)

    try:
        reconciler = ExcelReconciler(
            raw_file_path=final_raw_path,
            source_path=final_source_path,
            user_name=user_name,
            progress_callback=update_progress
        )

        out_name = f"{os.path.splitext(os.path.basename(final_raw_path))[0]}_Reconciled.xlsx"
        out_dir = os.path.dirname(final_raw_path) or "."
        output_file_path = os.path.join(out_dir, out_name)

        stats = reconciler.reconcile(output_file_path=output_file_path)

        st.session_state["last_stats"] = stats
        st.session_state["output_file_path"] = output_file_path

        progress_container.empty()
        status_text.success("✓ Reconciliation finished successfully! Formatted Excel report generated.")

    except Exception as e:
        progress_container.empty()
        status_text.error(f"Reconciliation error: {str(e)}")
        st.exception(e)
        st.stop()


# Render Results if available
if "last_stats" in st.session_state and "output_file_path" in st.session_state:
    stats = st.session_state["last_stats"]
    out_path = st.session_state["output_file_path"]

    st.subheader("2. Reconciliation Execution Summary")

    # Metrics Display
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(label="Evaluated Cells", value=f"{stats['total_evaluated']:,}")
    with m2:
        st.metric(label="Exact Matches", value=f"{stats['exact_matches']:,}")
    with m3:
        st.metric(label="Close Matches (Yellow)", value=f"{stats['close_matches']:,}")
    with m4:
        st.metric(label="Mismatches (Red)", value=f"{stats['mismatches']:,}")
    with m5:
        st.metric(label="Accuracy Rate", value=f"{stats['accuracy_pct']}%")

    # Download Button
    if os.path.exists(out_path):
        with open(out_path, "rb") as f:
            file_bytes = f.read()

        col_dl_1, col_dl_2 = st.columns([3, 1])
        with col_dl_1:
            st.caption(f"Saved to: `{out_path}` | Evaluated across {stats['source_files_count']} source file(s)")
        with col_dl_2:
            st.download_button(
                label="📥 Download Reconciled Excel",
                data=file_bytes,
                file_name=os.path.basename(out_path),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    st.markdown("---")
    st.subheader("3. Interactive Workbook & Difference Viewer")

    # Load and view sheets
    wb = openpyxl.load_workbook(out_path, data_only=False)
    sheet_options = wb.sheetnames
    selected_sheet = st.selectbox("Select Sheet to Inspect:", sheet_options, index=0)

    # Convert sheet to visual dataframe with styled highlights
    ws = wb[selected_sheet]
    data_rows = []
    max_r = min(ws.max_row, 100)
    max_c = min(ws.max_column, 26)

    headers = [str(ws.cell(row=1, column=c).value or f"Col_{c}") for c in range(1, max_c + 1)]
    for r in range(2, max_r + 1):
        row_vals = [ws.cell(row=r, column=c).value for c in range(1, max_c + 1)]
        data_rows.append(row_vals)

    if data_rows:
        df = pd.DataFrame(data_rows, columns=headers)

        # Build style map based on openpyxl fills
        def style_cells(val):
            return ""

        st.dataframe(df, use_container_width=True)

    # Discrepancies Details Table
    if stats.get("diff_details"):
        st.subheader("Discrepancies & Flagged Cell Coordinates")
        diff_df = pd.DataFrame(stats["diff_details"])
        st.dataframe(diff_df, use_container_width=True)
