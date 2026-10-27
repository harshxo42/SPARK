"""
app.py — SPARK Main Streamlit Application
==========================================
Run with:
    python -m streamlit run app.py

SPARK — Spatial AI Repair Knowledge Platform
A final-year B.Tech demonstration prototype.
"""

from __future__ import annotations

import io
import os
import tempfile
from datetime import date, datetime
from pathlib import Path

import streamlit as st
from PIL import Image

import database as db
import reports
import sample_generator
from vision import compare_images

# ── Directory setup ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
ASSETS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

REFERENCE_IMG = ASSETS_DIR / "reference.png"
CURRENT_IMG = ASSETS_DIR / "current.png"

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPARK — Spatial AI Repair Knowledge Platform",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — Industrial dark theme ───────────────────────────────────────────────
st.markdown(
    """
<style>
/* ─── Global base ──────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1c2e;
    color: #c8d8e8;
}

/* ─── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1520 0%, #0d1c2e 100%);
    border-right: 1px solid #1e3a5a;
}
[data-testid="stSidebar"] .stRadio > label {
    color: #8899aa;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    color: #c8d8e8 !important;
    font-size: 0.9rem;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 2px 0;
    transition: all 0.2s;
    cursor: pointer;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(0, 200, 200, 0.08);
    color: #00c8c8 !important;
}

/* ─── Main content ─────────────────────────────────────────────────────── */
.main .block-container {
    background-color: #0d1c2e;
    padding-top: 1.5rem;
    max-width: 1200px;
}

/* ─── Headers ──────────────────────────────────────────────────────────── */
h1 { color: #00c8c8 !important; font-weight: 700; letter-spacing: -0.02em; }
h2 { color: #4ab8d8 !important; font-weight: 600; }
h3 { color: #8ab8cc !important; font-weight: 500; }

/* ─── Dashboard cards ──────────────────────────────────────────────────── */
.spark-card {
    background: linear-gradient(135deg, #1a2d42 0%, #0f2035 100%);
    border: 1px solid #2a4a6a;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.spark-card:hover {
    border-color: #00c8c8;
    box-shadow: 0 0 18px rgba(0, 200, 200, 0.12);
}
.spark-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #5a8faa;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.spark-card-value {
    font-size: 2rem;
    font-weight: 700;
    color: #00c8c8;
    line-height: 1.1;
}
.spark-card-sub {
    font-size: 0.8rem;
    color: #6a8fa8;
    margin-top: 4px;
}

/* ─── Status badges ────────────────────────────────────────────────────── */
.badge-pending  { background:#2a1a0a; color:#e8a030; border:1px solid #8a5010; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-progress { background:#0a1a2a; color:#3090e0; border:1px solid #204070; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-complete { background:#0a2a1a; color:#30e070; border:1px solid #206040; padding:3px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

/* ─── Metric panels ────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #1a2d42;
    border: 1px solid #2a4a6a;
    border-radius: 10px;
    padding: 14px 18px;
}
[data-testid="stMetric"] label { color: #5a8faa !important; font-size: 0.78rem !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #00c8c8 !important; font-size: 1.6rem !important; }

/* ─── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #007a9a 0%, #005a7a 100%);
    color: white;
    border: 1px solid #00a0c0;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.9rem;
    padding: 0.5rem 1.4rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #009ab8 0%, #007a9a 100%);
    border-color: #00c8c8;
    box-shadow: 0 0 14px rgba(0, 200, 200, 0.25);
    transform: translateY(-1px);
}
.stButton > button:active { transform: translateY(0); }

/* ─── Download button ──────────────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, #006040 0%, #004030 100%);
    border-color: #008050;
    color: #80f0a0;
}
[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(135deg, #008050 0%, #006040 100%);
    border-color: #00c060;
}

/* ─── Inputs ───────────────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: #0f2035 !important;
    border: 1px solid #2a4a6a !important;
    color: #c8d8e8 !important;
    border-radius: 8px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #00c8c8 !important;
    box-shadow: 0 0 8px rgba(0, 200, 200, 0.2) !important;
}

/* ─── File uploader ────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: #0f2035;
    border: 1.5px dashed #2a4a6a;
    border-radius: 10px;
    padding: 12px;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover { border-color: #00c8c8; }

/* ─── Divider ──────────────────────────────────────────────────────────── */
hr { border-color: #1e3a5a; }

/* ─── Expanders ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] { background: #0f2035; border: 1px solid #1e3a5a; border-radius: 10px; }

/* ─── Tables ───────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border: 1px solid #1e3a5a; border-radius: 8px; }

/* ─── Alert / info boxes ───────────────────────────────────────────────── */
[data-testid="stInfo"]    { background: #0a1e34; border-left: 4px solid #00c8c8; }
[data-testid="stSuccess"] { background: #0a2010; border-left: 4px solid #30e070; }
[data-testid="stWarning"] { background: #20140a; border-left: 4px solid #e8a030; }
[data-testid="stError"]   { background: #200a0a; border-left: 4px solid #e83030; }

/* ─── Progress bar ─────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #007a9a, #00c8c8);
}

/* ─── Sidebar logo area ────────────────────────────────────────────────── */
.spark-logo {
    text-align: center;
    padding: 20px 10px 16px;
    border-bottom: 1px solid #1e3a5a;
    margin-bottom: 16px;
}
.spark-logo-text {
    font-size: 2rem;
    font-weight: 800;
    color: #00c8c8;
    letter-spacing: 0.08em;
    line-height: 1;
}
.spark-logo-sub {
    font-size: 0.65rem;
    color: #4a7a9a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}
.spark-version {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #2a5a7a;
    margin-top: 6px;
}

/* ─── Section divider ──────────────────────────────────────────────────── */
.section-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #1e3a5a, transparent);
    margin: 20px 0;
}

/* ─── Image caption ────────────────────────────────────────────────────── */
.img-caption {
    font-size: 0.72rem;
    color: #5a8faa;
    text-align: center;
    margin-top: 4px;
}

/* ─── Checklist items ──────────────────────────────────────────────────── */
.checklist-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 10px 14px;
    background: #0f2035;
    border: 1px solid #1e3a5a;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 0.9rem;
}
.checklist-num {
    background: #00c8c8;
    color: #0d1c2e;
    font-weight: 700;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
}

/* ─── Page header banner ───────────────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, #0f2035 0%, #162840 100%);
    border: 1px solid #1e3a5a;
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.page-header-icon { font-size: 2rem; }
.page-header-title { font-size: 1.5rem; font-weight: 700; color: #00c8c8; }
.page-header-sub { font-size: 0.85rem; color: #6a8fa8; margin-top: 2px; }
</style>
""",
    unsafe_allow_html=True,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def status_badge(status: str) -> str:
    cls_map = {
        "Pending Review": "badge-pending",
        "In Progress": "badge-progress",
        "Completed": "badge-complete",
    }
    cls = cls_map.get(status, "badge-pending")
    return f'<span class="{cls}">{status}</span>'


def pil_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def ensure_sample_images() -> None:
    """Generate sample images if missing."""
    if not REFERENCE_IMG.exists() or not CURRENT_IMG.exists():
        sample_generator.generate_sample_images(force=False)


def _save_temp(uploaded_file) -> str:
    """Save a Streamlit UploadedFile to a temp file and return its path."""
    suffix = Path(uploaded_file.name).suffix or ".png"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=DATA_DIR)
    tmp.write(uploaded_file.getbuffer())
    tmp.flush()
    tmp.close()
    return tmp.name


def _image_panel(img_path: str, caption: str) -> None:
    """Display a labelled image panel."""
    if img_path and Path(img_path).exists():
        img = Image.open(img_path)
        st.image(img, use_container_width=True)
        st.markdown(f'<p class="img-caption">{caption}</p>', unsafe_allow_html=True)
    else:
        st.info(f"📷 {caption} — not available")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="spark-logo">
            <div class="spark-logo-text">⚙ SPARK</div>
            <div class="spark-logo-sub">Spatial AI Repair Knowledge Platform</div>
            <div class="spark-version">Prototype v1.0 — B.Tech 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "NAVIGATION",
        options=[
            "🏠  Overview",
            "🔍  Gearbox Inspection",
            "📋  Repair Guidance",
            "📁  Repair Records",
            "📄  Reports",
            "ℹ  About SPARK",
        ],
        label_visibility="visible",
    )

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.7rem;color:#2a5a7a;padding:8px;'>"
        "⚠ This is a software prototype for academic demonstration. "
        "Not for industrial use.</div>",
        unsafe_allow_html=True,
    )

# ── Session state defaults ────────────────────────────────────────────────────
ss = st.session_state
ss.setdefault("comparison_done", False)
ss.setdefault("highlighted_img", None)
ss.setdefault("change_percent", 0.0)
ss.setdefault("comparison_summary", "")
ss.setdefault("ref_tmp_path", "")
ss.setdefault("cur_tmp_path", "")
ss.setdefault("record_saved_id", None)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if "Overview" in page:
    ensure_sample_images()

    # ── Hero banner ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#0a1f35 0%,#0f2840 50%,#0a1f35 100%);
                    border:1px solid #1e3a5a;border-radius:16px;padding:32px 36px;margin-bottom:24px;">
            <div style="font-size:2.8rem;font-weight:800;color:#00c8c8;letter-spacing:-0.02em;margin-bottom:6px;">
                ⚙ SPARK
            </div>
            <div style="font-size:1.1rem;color:#4ab8d8;margin-bottom:10px;font-weight:600;">
                Spatial AI Repair Knowledge Platform
            </div>
            <div style="font-size:0.88rem;color:#8899aa;max-width:680px;line-height:1.6;">
                A software prototype demonstrating structured gearbox inspection workflows, 
                image-based visual comparison, technician guidance, and digital record management. 
                Developed as a B.Tech final-year project. 
                <strong style="color:#e8a030;">Not for industrial deployment.</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stats row ────────────────────────────────────────────────────────────
    counts = db.count_by_status()
    total = counts.get("Total", 0)
    pending = counts.get("Pending Review", 0)
    in_prog = counts.get("In Progress", 0)
    completed = counts.get("Completed", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Records", total, help="All stored inspection records")
    with c2:
        st.metric("Pending Review", pending, help="Records awaiting review")
    with c3:
        st.metric("In Progress", in_prog, help="Records under active review")
    with c4:
        st.metric("Completed", completed, help="Fully reviewed records")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # ── Demo gearbox panel ───────────────────────────────────────────────────
    left, right = st.columns([1, 1])
    with left:
        st.markdown("### 🔩 Demo Gearbox Case")
        st.markdown(
            """
            <div class="spark-card">
                <div class="spark-card-title">Gearbox Case</div>
                <div style="font-size:1.2rem;font-weight:700;color:#c8d8e8;margin-bottom:6px;">GB-DEMO-001</div>
                <div style="font-size:0.82rem;color:#6a8fa8;margin-bottom:10px;">
                    Industrial Spur Gearbox — Illustrative Demo Unit
                </div>
                <div style="display:flex;gap:10px;flex-wrap:wrap;">
                    <span style="background:#0f2035;border:1px solid #2a4a6a;padding:3px 10px;border-radius:20px;font-size:0.78rem;color:#00c8c8;">Sample Case</span>
                    <span style="background:#0f2035;border:1px solid #2a4a6a;padding:3px 10px;border-radius:20px;font-size:0.78rem;color:#8ab8cc;">Schematic</span>
                    <span style="background:#0f2035;border:1px solid #2a4a6a;padding:3px 10px;border-radius:20px;font-size:0.78rem;color:#e8a030;">Demo Only</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🔍 Start Inspection for GB-DEMO-001", use_container_width=True):
            st.session_state["goto_inspection"] = True
            st.rerun()

    with right:
        st.markdown("### 📅 Recent Activity")
        recent = db.get_recent_records(5)
        if recent:
            for rec in recent:
                badge = status_badge(rec["status"])
                st.markdown(
                    f'<div class="spark-card" style="padding:12px 16px;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;">'
                    f'<span style="font-size:0.85rem;color:#c8d8e8;">#{rec["record_id"]} — {rec["gearbox_case"]}</span>'
                    f'{badge}</div>'
                    f'<div style="font-size:0.72rem;color:#5a8faa;margin-top:3px;">'
                    f'{rec["technician_name"]} · {rec["inspection_date"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No inspection records yet. Start an inspection to create the first record.")

    # ── Sample images preview ────────────────────────────────────────────────
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("### 🖼 Sample Gearbox Schematics")
    st.caption(
        "These are programmatically generated illustrative schematics. "
        "They are NOT photographs of real industrial gearboxes."
    )
    ic1, ic2 = st.columns(2)
    with ic1:
        if REFERENCE_IMG.exists():
            st.image(str(REFERENCE_IMG), caption="Reference State (GB-DEMO-001)", use_container_width=True)
    with ic2:
        if CURRENT_IMG.exists():
            st.image(str(CURRENT_IMG), caption="Current State (GB-DEMO-001)", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GEARBOX INSPECTION
# ═══════════════════════════════════════════════════════════════════════════════
elif "Inspection" in page or ss.get("goto_inspection"):
    ss["goto_inspection"] = False
    ensure_sample_images()

    st.markdown(
        '<div class="page-header">'
        '<div class="page-header-icon">🔍</div>'
        '<div><div class="page-header-title">Gearbox Inspection</div>'
        '<div class="page-header-sub">Compare reference and current images to identify visual differences</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Gearbox selector ─────────────────────────────────────────────────────
    gearbox_case = st.selectbox(
        "Gearbox Case",
        options=["GB-DEMO-001 — Industrial Spur Gearbox (Demo)"],
        help="Select the gearbox case to inspect",
    )

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # ── Image upload / demo loader ───────────────────────────────────────────
    col_upload, col_demo = st.columns([3, 1])
    with col_demo:
        st.markdown("**Quick Load**")
        if st.button("📁 Load Demo Images", use_container_width=True):
            ss["ref_tmp_path"] = str(REFERENCE_IMG)
            ss["cur_tmp_path"] = str(CURRENT_IMG)
            ss["comparison_done"] = False
            ss["highlighted_img"] = None
            st.success("Demo images loaded. Click **Compare Images** to proceed.")

    with col_upload:
        st.markdown("**Upload Custom Images** (optional)")
        upload_c1, upload_c2 = st.columns(2)
        with upload_c1:
            ref_upload = st.file_uploader(
                "Reference Image",
                type=["png", "jpg", "jpeg", "bmp", "tiff"],
                key="ref_uploader",
            )
        with upload_c2:
            cur_upload = st.file_uploader(
                "Current Inspection Image",
                type=["png", "jpg", "jpeg", "bmp", "tiff"],
                key="cur_uploader",
            )
        if ref_upload:
            ss["ref_tmp_path"] = _save_temp(ref_upload)
        if cur_upload:
            ss["cur_tmp_path"] = _save_temp(cur_upload)

    # ── Preview row ──────────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    prev_c1, prev_c2 = st.columns(2)
    with prev_c1:
        st.markdown("##### Reference Image")
        _image_panel(ss["ref_tmp_path"], "Reference (baseline) schematic")
    with prev_c2:
        st.markdown("##### Current Inspection Image")
        _image_panel(ss["cur_tmp_path"], "Current state schematic")

    # ── Compare button ───────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    btn_col, _ = st.columns([1, 2])
    with btn_col:
        compare_clicked = st.button("⚡ Compare Images", use_container_width=True)

    if compare_clicked:
        if not ss["ref_tmp_path"] or not ss["cur_tmp_path"]:
            st.error("Please load the demo images or upload both images before comparing.")
        else:
            with st.spinner("Running pixel-level comparison…"):
                try:
                    result = compare_images(ss["ref_tmp_path"], ss["cur_tmp_path"])
                    ss["highlighted_img"] = result["highlighted_image"]
                    ss["change_percent"] = result["change_percent"]
                    ss["comparison_summary"] = result["summary"]
                    ss["comparison_done"] = True
                except (FileNotFoundError, ValueError) as exc:
                    st.error(f"Comparison error: {exc}")
                    ss["comparison_done"] = False

    # ── Results section ───────────────────────────────────────────────────────
    if ss["comparison_done"] and ss["highlighted_img"] is not None:
        st.markdown("### 📊 Comparison Results")

        res_c1, res_c2, res_c3 = st.columns(3)
        with res_c1:
            st.markdown("##### Reference")
            _image_panel(ss["ref_tmp_path"], "Reference (baseline)")
        with res_c2:
            st.markdown("##### Current")
            _image_panel(ss["cur_tmp_path"], "Current inspection")
        with res_c3:
            st.markdown("##### Highlighted Differences")
            st.image(ss["highlighted_img"], use_container_width=True)
            st.markdown('<p class="img-caption">Red pixels = visual difference detected</p>', unsafe_allow_html=True)

        # Metric + summary
        m1, m2 = st.columns([1, 2])
        with m1:
            st.metric(
                "Visual Change %",
                f"{ss['change_percent']:.2f}%",
                help="Percentage of pixels exceeding the difference threshold",
            )
            # Progress bar capped at 100%
            st.progress(min(ss["change_percent"] / 100.0, 1.0))
        with m2:
            st.markdown("**Comparison Summary**")
            st.info(ss["comparison_summary"])

        st.warning(
            "⚠ **Important:** The visual change percentage is a pixel-comparison metric, "
            "NOT a probability of gearbox fault or mechanical damage. "
            "All findings must be reviewed by a qualified maintenance engineer."
        )

        # Explanation of red regions
        with st.expander("📖 What do the red-highlighted regions mean?"):
            st.markdown(
                """
                **Red-highlighted pixels** indicate areas where the pixel colour values 
                in the current image differ from the reference image by more than the 
                configured sensitivity threshold (30 out of 255 per colour channel).

                This can be caused by:
                - Actual changes to the gearbox surface or components
                - Differences in lighting or camera position between inspections
                - Image quality or compression differences
                - Marks, labels, or stickers added since the reference was taken

                **The highlight does NOT:**
                - Identify the cause of any difference
                - Diagnose a mechanical fault
                - Indicate whether any action is required
                - Replace professional engineering assessment
                """
            )

        # ── Save temp highlighted for PDF ─────────────────────────────────
        hl_tmp = DATA_DIR / "highlighted_tmp.png"
        ss["highlighted_img"].save(str(hl_tmp))
        ss["highlighted_tmp_path"] = str(hl_tmp)

        # Download button
        dl_col, _ = st.columns([1, 3])
        with dl_col:
            img_bytes = pil_to_bytes(ss["highlighted_img"])
            st.download_button(
                "⬇ Download Highlighted Image",
                data=img_bytes,
                file_name="spark_highlighted_diff.png",
                mime="image/png",
                use_container_width=True,
            )

        # ── Quick-save form ───────────────────────────────────────────────
        st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
        st.markdown("### 💾 Save Inspection Record")
        st.caption("Fill in your observations and save to the local database.")

        with st.form("quick_save_form"):
            tech_name = st.text_input("Technician Name", placeholder="Your name")
            insp_date = st.date_input("Inspection Date", value=date.today())
            observations = st.text_area(
                "Observations",
                placeholder="Describe what you observed in the highlighted image…",
                height=120,
            )
            repair_actions = st.text_area(
                "Repair Action Notes",
                placeholder="Note any actions taken or recommended (no prescriptive repairs)…",
                height=80,
            )
            status = st.selectbox(
                "Initial Status",
                ["Pending Review", "In Progress", "Completed"],
            )
            submitted = st.form_submit_button("💾 Save Record", use_container_width=True)

        if submitted:
            if not tech_name.strip():
                st.error("Please enter a technician name.")
            else:
                record_id = db.save_record(
                    gearbox_case="GB-DEMO-001",
                    technician_name=tech_name.strip(),
                    inspection_date=str(insp_date),
                    change_percent=ss["change_percent"],
                    comparison_summary=ss["comparison_summary"],
                    observations=observations,
                    repair_actions=repair_actions,
                    status=status,
                )
                # Persist images
                db.save_images_for_record(
                    record_id=record_id,
                    reference_path=ss.get("ref_tmp_path", ""),
                    current_path=ss.get("cur_tmp_path", ""),
                    highlighted_path=ss.get("highlighted_tmp_path", ""),
                )
                ss["record_saved_id"] = record_id
                st.success(f"✅ Record #{record_id} saved successfully!")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: REPAIR GUIDANCE
# ═══════════════════════════════════════════════════════════════════════════════
elif "Guidance" in page:
    st.markdown(
        '<div class="page-header">'
        '<div class="page-header-icon">📋</div>'
        '<div><div class="page-header-title">Repair Guidance</div>'
        '<div class="page-header-sub">Inspection checklist and technician observational guidelines</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.error(
        "🔒 **Safety Notice — Read Before Proceeding:** "
        "Real industrial maintenance requires qualified personnel following all applicable "
        "safety procedures, including lockout/tagout (LOTO) protocols. This checklist is "
        "a general observational guide for demonstration purposes only. "
        "Do NOT perform any physical maintenance based solely on this software."
    )

    st.markdown("### Inspection Checklist")
    st.caption(
        "This checklist provides general observational guidance. "
        "It does NOT diagnose faults, identify root causes, or prescribe specific repair actions."
    )

    checklist = [
        ("⚡", "Isolation & Safety", "Verify that the equipment is fully isolated from power and motion sources. Confirm lockout/tagout procedures are in place before approaching the gearbox."),
        ("🖼", "Review Reference Images", "Open the Gearbox Inspection page and load the reference image for the selected case. Familiarise yourself with the baseline state of the equipment."),
        ("📷", "Capture or Load Current Image", "Upload the current inspection image or use the demo image. Ensure the image is taken from the same position and lighting as the reference where possible."),
        ("⚡", "Run Image Comparison", "Use the Compare Images function to generate the highlighted difference image. Note the visual change percentage and review the highlighted regions."),
        ("👁", "Examine Housing Surfaces", "Visually inspect accessible gearbox housing surfaces for cracks, corrosion, oil leaks, or surface damage as permitted by your site procedures."),
        ("🔩", "Inspect Accessible Components", "Where authorised, inspect visible seals, mounting hardware, and accessible external components. Do not disassemble equipment without proper authority."),
        ("📝", "Record Observed Differences", "Document all observed differences between the reference and current state. Be factual and descriptive — avoid speculating about root causes."),
        ("🔺", "Escalate Uncertain Findings", "If any observed difference is unclear, unexpected, or potentially safety-relevant, escalate to a qualified maintenance engineer immediately. Do not attempt diagnosis independently."),
        ("✅", "Record Final Technician Notes", "Save your observations and action notes in the Repair Records section. Set an appropriate review status."),
        ("📄", "Generate Report (Optional)", "Export a PDF inspection report from the Reports page for record-keeping purposes. Label it clearly as a demonstration report."),
    ]

    for i, (icon, title, detail) in enumerate(checklist, 1):
        with st.expander(f"{icon}  Step {i}: {title}", expanded=(i == 1)):
            st.markdown(detail)

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("### 📌 General Observational Guidance")

    guidance_items = [
        ("Document, don't diagnose", "Record exactly what you observe. Do not speculate about root causes or equipment condition without professional engineering assessment."),
        ("Lighting and positioning matter", "Visual image comparison is sensitive to camera angle, zoom level, and lighting. Account for these when interpreting highlighted regions."),
        ("Multiple images improve reliability", "A single comparison image pair may not capture all relevant differences. Multiple viewpoints improve inspection thoroughness."),
        ("Software comparison supplements — not replaces — human inspection", "Automated pixel comparison is a visual aid. It cannot detect vibration, temperature, noise, or other sensory indicators of equipment condition."),
        ("Follow site procedures", "Always comply with your organisation's maintenance management procedures, work orders, and safety systems."),
    ]

    for title, detail in guidance_items:
        st.markdown(
            f'<div class="spark-card">'
            f'<div style="font-weight:600;color:#00c8c8;margin-bottom:4px;">▸ {title}</div>'
            f'<div style="font-size:0.88rem;color:#8ab8cc;">{detail}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: REPAIR RECORDS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Records" in page:
    st.markdown(
        '<div class="page-header">'
        '<div class="page-header-icon">📁</div>'
        '<div><div class="page-header-title">Repair Records</div>'
        '<div class="page-header-sub">Browse, filter, and manage stored inspection records</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Filter ───────────────────────────────────────────────────────────────
    f_col1, f_col2 = st.columns([1, 3])
    with f_col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending Review", "In Progress", "Completed"],
        )

    records = db.get_all_records(status_filter)

    if not records:
        st.info("No inspection records found. Complete an inspection on the Gearbox Inspection page to create records.")
    else:
        st.markdown(f"**{len(records)} record(s) found**")

        for rec in records:
            badge = status_badge(rec["status"])
            with st.expander(
                f"#{rec['record_id']} — {rec['gearbox_case']}  |  {rec['technician_name']}  |  {rec['inspection_date']}",
                expanded=False,
            ):
                detail_c1, detail_c2 = st.columns(2)
                with detail_c1:
                    st.markdown(f"**Record ID:** {rec['record_id']}")
                    st.markdown(f"**Gearbox Case:** {rec['gearbox_case']}")
                    st.markdown(f"**Technician:** {rec['technician_name']}")
                    st.markdown(f"**Inspection Date:** {rec['inspection_date']}")
                    st.markdown(f"**Status:** ", unsafe_allow_html=False)
                    st.markdown(badge, unsafe_allow_html=True)
                    st.markdown(f"**Created:** {rec['created_at']}")

                with detail_c2:
                    st.markdown(f"**Visual Change %:** `{rec['change_percent']:.2f}%`")
                    st.caption("⚠ This is a pixel metric, not fault probability")
                    st.markdown(f"**Comparison Summary:**")
                    st.info(rec["comparison_summary"] or "—")

                st.markdown("**Observations:**")
                st.markdown(
                    f'<div style="background:#0f2035;padding:10px;border-radius:8px;'
                    f'border:1px solid #1e3a5a;font-size:0.88rem;color:#c8d8e8;">'
                    f'{rec["observations"] or "No observations recorded."}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown("**Repair Action Notes:**")
                st.markdown(
                    f'<div style="background:#0f2035;padding:10px;border-radius:8px;'
                    f'border:1px solid #1e3a5a;font-size:0.88rem;color:#c8d8e8;">'
                    f'{rec["repair_actions"] or "No actions recorded."}</div>',
                    unsafe_allow_html=True,
                )

                # Status update
                new_status = st.selectbox(
                    "Update Status",
                    ["Pending Review", "In Progress", "Completed"],
                    index=["Pending Review", "In Progress", "Completed"].index(rec["status"]),
                    key=f"status_sel_{rec['record_id']}",
                )
                if st.button("Update Status", key=f"upd_{rec['record_id']}"):
                    db.update_status(rec["record_id"], new_status)
                    st.success(f"Status updated to '{new_status}'")
                    st.rerun()

                # Images
                imgs = db.get_images_for_record(rec["record_id"])
                if any(imgs.values()):
                    st.markdown("**Stored Images:**")
                    img_c1, img_c2, img_c3 = st.columns(3)
                    with img_c1:
                        _image_panel(imgs["reference_path"], "Reference")
                    with img_c2:
                        _image_panel(imgs["current_path"], "Current")
                    with img_c3:
                        _image_panel(imgs["highlighted_path"], "Highlighted Diff")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: REPORTS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Reports" in page:
    st.markdown(
        '<div class="page-header">'
        '<div class="page-header-icon">📄</div>'
        '<div><div class="page-header-title">PDF Reports</div>'
        '<div class="page-header-sub">Generate and download demonstration inspection reports</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.warning(
        "📄 Reports generated here are DEMONSTRATION DOCUMENTS produced by a software prototype. "
        "They are NOT certified inspection reports. Do not use them for any real maintenance decision."
    )

    all_records = db.get_all_records()

    if not all_records:
        st.info("No inspection records found. Create a record on the Gearbox Inspection page first.")
    else:
        # Pick a record
        record_options = {
            f"#{r['record_id']} — {r['gearbox_case']} | {r['technician_name']} | {r['inspection_date']}": r["record_id"]
            for r in all_records
        }
        selected_label = st.selectbox("Select Record", list(record_options.keys()))
        selected_id = record_options[selected_label]

        record = db.get_record_by_id(selected_id)
        images = db.get_images_for_record(selected_id)

        if record:
            # Preview
            with st.expander("Record Preview", expanded=True):
                pc1, pc2 = st.columns(2)
                with pc1:
                    st.markdown(f"**Record ID:** {record['record_id']}")
                    st.markdown(f"**Gearbox Case:** {record['gearbox_case']}")
                    st.markdown(f"**Technician:** {record['technician_name']}")
                    st.markdown(f"**Date:** {record['inspection_date']}")
                    st.markdown(f"**Status:** {record['status']}")
                with pc2:
                    st.markdown(f"**Visual Change:** `{record['change_percent']:.2f}%` (pixel metric)")
                    st.markdown(f"**Observations:** {record['observations'] or '—'}")

            # Generate PDF
            gen_col, _ = st.columns([1, 2])
            with gen_col:
                if st.button("⚙ Generate PDF Report", use_container_width=True):
                    pdf_path = REPORTS_DIR / f"SPARK_Report_REC{selected_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    with st.spinner("Generating PDF…"):
                        try:
                            out_path = reports.generate_report(
                                record=record,
                                images=images,
                                output_path=str(pdf_path),
                            )
                            with open(out_path, "rb") as f:
                                pdf_bytes = f.read()
                            st.success("PDF generated successfully!")
                            st.download_button(
                                "⬇ Download PDF Report",
                                data=pdf_bytes,
                                file_name=Path(out_path).name,
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        except Exception as exc:
                            st.error(f"PDF generation failed: {exc}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT SPARK
# ═══════════════════════════════════════════════════════════════════════════════
elif "About" in page:
    st.markdown(
        '<div class="page-header">'
        '<div class="page-header-icon">ℹ</div>'
        '<div><div class="page-header-title">About SPARK</div>'
        '<div class="page-header-sub">Project overview, implemented features, and future vision</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#0a1f35,#0f2840);border:1px solid #1e3a5a;
                    border-radius:12px;padding:24px 28px;margin-bottom:20px;">
            <div style="font-size:1.6rem;font-weight:800;color:#00c8c8;margin-bottom:6px;">⚙ SPARK</div>
            <div style="font-size:1rem;color:#4ab8d8;margin-bottom:10px;">Spatial AI Repair Knowledge Platform</div>
            <div style="font-size:0.88rem;color:#8899aa;line-height:1.7;">
                SPARK is a B.Tech final-year project exploring how software-based tooling can support 
                industrial gearbox inspection workflows. This prototype demonstrates structured digital 
                record-keeping, basic image comparison, technician guidance, and report generation 
                without requiring any industrial hardware or AI models.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_impl, col_future = st.columns(2)

    with col_impl:
        st.markdown("### ✅ Implemented in This Prototype")
        implemented = [
            ("🖥", "Industrial-style web dashboard", "Dark-themed Streamlit interface with professional card layout and navigation"),
            ("🖼", "Illustrative gearbox schematics", "Programmatically generated reference and current images using Pillow"),
            ("🔍", "Pixel-level image comparison", "Basic Pillow ImageChops differencing with configurable threshold and red highlights"),
            ("📋", "Technician inspection checklist", "10-step guided observational checklist with safety notices"),
            ("💾", "Local repair record management", "SQLite-backed CRUD with status tracking and image persistence"),
            ("📄", "PDF report export", "ReportLab-based professional report with images and disclaimers"),
        ]
        for icon, title, detail in implemented:
            st.markdown(
                f'<div class="spark-card" style="padding:14px 18px;">'
                f'<div style="display:flex;gap:10px;align-items:flex-start;">'
                f'<span style="font-size:1.2rem;">{icon}</span>'
                f'<div><div style="font-weight:600;color:#30e070;font-size:0.88rem;">{title}</div>'
                f'<div style="font-size:0.8rem;color:#6a8fa8;margin-top:2px;">{detail}</div></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    with col_future:
        st.markdown("### 🚀 Future Planned Capabilities")
        st.caption("⚠ These capabilities are NOT implemented in this prototype.")
        future = [
            ("📷", "Real gearbox camera inspection", "Live camera integration for actual industrial gearbox imaging"),
            ("🔧", "Hardware & sensor integration", "Connection to industrial sensors, PLCs, and IoT devices"),
            ("🧠", "Advanced image registration", "Sub-pixel alignment of images across inspection sessions"),
            ("🤖", "Validated defect detection models", "Machine learning models trained and validated on real industrial data"),
            ("🗺", "Spatial mapping / SLAM research", "3D spatial mapping of gearbox surfaces using camera or LiDAR"),
            ("🥽", "AR-assisted technician workflows", "Augmented reality overlays to guide on-site technicians"),
            ("🏭", "Industrial CMMS integration", "Integration with industrial maintenance management systems"),
        ]
        for icon, title, detail in future:
            st.markdown(
                f'<div class="spark-card" style="padding:14px 18px;border-color:#1a3050;">'
                f'<div style="display:flex;gap:10px;align-items:flex-start;">'
                f'<span style="font-size:1.2rem;">{icon}</span>'
                f'<div><div style="font-weight:600;color:#4ab8d8;font-size:0.88rem;">{title}</div>'
                f'<div style="font-size:0.8rem;color:#4a6a8a;margin-top:2px;">{detail}</div></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("### 🛠 Technology Stack")

    tech = [
        ("Python 3.11+", "Core programming language"),
        ("Streamlit", "Web dashboard framework"),
        ("Pillow (PIL)", "Image loading, processing, and schematic generation"),
        ("SQLite", "Local relational database for persistent record storage"),
        ("ReportLab", "PDF report generation"),
    ]
    tc1, tc2 = st.columns(2)
    for i, (tech_name, tech_detail) in enumerate(tech):
        col = tc1 if i % 2 == 0 else tc2
        with col:
            st.markdown(
                f'<div class="spark-card" style="padding:12px 16px;">'
                f'<div style="font-weight:700;color:#00c8c8;font-family:monospace;">{tech_name}</div>'
                f'<div style="font-size:0.8rem;color:#6a8fa8;">{tech_detail}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#2a5a7a;font-size:0.78rem;padding:10px;">'
        'SPARK Prototype — B.Tech Final Year Project — 2026 — For Academic Demonstration Only'
        '</div>',
        unsafe_allow_html=True,
    )
