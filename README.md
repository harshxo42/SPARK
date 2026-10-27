# SPARK — Spatial AI Repair Knowledge Platform

> **B.Tech Final-Year Project · Software Prototype · 2026**

SPARK is a local desktop web application that demonstrates a structured gearbox inspection workflow — image comparison, technician guidance, digital record management, and PDF report generation — without requiring any industrial hardware, API keys, or internet connection.

---

## ✅ Implemented Features

| Feature | Description |
|---|---|
| Industrial Dashboard | Dark-themed Streamlit interface with cards, metrics, and navigation |
| Demo Gearbox Case | One sample case (GB-DEMO-001) with illustrative schematics |
| Image Comparison | Pixel-level difference highlighting with red-marked changed regions |
| Technician Checklist | 10-step guided observational inspection checklist |
| Repair Records | SQLite-backed CRUD with status tracking and image persistence |
| PDF Report Export | ReportLab professional report with images and disclaimers |

---

## 🛠 Technology Stack

| Library | Purpose |
|---|---|
| Python 3.11+ | Core language |
| Streamlit ≥ 1.32 | Web dashboard |
| Pillow ≥ 10.2 | Image processing and schematic generation |
| SQLite (built-in) | Local persistent database |
| ReportLab ≥ 4.1 | PDF report generation |

---

## 📁 Folder Structure

```
SPARK/
├── app.py                  # Main Streamlit application
├── vision.py               # Image comparison module
├── database.py             # SQLite database module
├── reports.py              # PDF report generator
├── sample_generator.py     # Illustrative schematic generator
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── DEMO_SCRIPT.md          # Faculty demonstration guide
├── assets/
│   ├── reference.png       # Reference gearbox schematic
│   └── current.png         # Current state schematic (with marked area)
├── data/
│   ├── spark.db            # SQLite database (created on first run)
│   ├── inspection_images/  # Persisted inspection images
│   └── reports/            # Generated PDF reports
└── tests/
    └── test_vision.py      # Unit tests
```

---

## 💻 Windows Installation Instructions

### Step 1 — Check Python version

Open PowerShell or Command Prompt and run:

```powershell
python --version
```

You need Python 3.11 or later. Download from [python.org](https://www.python.org/downloads/) if needed.

---

### Step 2 — Navigate to the project folder

```powershell
cd "C:\Users\singh\OneDrive\Desktop\SPARK"
```

---

### Step 3 — Create a virtual environment

```powershell
python -m venv .venv
```

---

### Step 4 — Activate the virtual environment

```powershell
.venv\Scripts\activate
```

You will see `(.venv)` at the start of your prompt when it is active.

---

### Step 5 — Install dependencies

```powershell
pip install -r requirements.txt
```

This installs Streamlit, Pillow, and ReportLab.

---

### Step 6 — Generate sample images

```powershell
python sample_generator.py
```

This creates `assets/reference.png` and `assets/current.png`.

---

### Step 7 — Start the application

```powershell
python -m streamlit run app.py
```

Streamlit will open a browser tab at `http://localhost:8501` automatically.

---

## 🚀 How to Use

### Load the Sample Gearbox Case

1. Open the app in your browser.
2. Click **🔍 Gearbox Inspection** in the left sidebar.
3. Click **📁 Load Demo Images** — the reference and current schematics will load.

### Compare Images

1. On the Gearbox Inspection page, click **⚡ Compare Images**.
2. The highlighted difference image will appear with red regions.
3. The **Visual Change %** metric will be displayed.
4. Read the plain-language **Comparison Summary**.

> ⚠ The visual change percentage is a pixel-comparison metric, **not** a probability of gearbox fault.

### Save a Repair Record

1. After comparing images, fill in the **Save Inspection Record** form below the results.
2. Enter your name, date, observations, and action notes.
3. Click **💾 Save Record**.
4. The record is stored in `data/spark.db`.

### View Repair Records

1. Click **📁 Repair Records** in the sidebar.
2. Filter by status using the dropdown.
3. Expand any record to view details, images, and update its status.

### Export a PDF Report

1. Click **📄 Reports** in the sidebar.
2. Select a saved record from the dropdown.
3. Click **⚙ Generate PDF Report**.
4. Click **⬇ Download PDF Report** to save the file.

### Run Tests

```powershell
python tests/test_vision.py
```

Or with pytest installed:

```powershell
python -m pytest tests/ -v
```

---

## ⚠ Prototype Limitations

- Images are simple programmatically generated schematics, not real industrial photographs.
- Image comparison uses basic pixel differencing — it is sensitive to lighting, camera position, and image quality.
- The visual change percentage is **not** a validated fault indicator.
- No real gearbox hardware, cameras, sensors, or AI models are used.
- Reports are demonstration documents — **not** certified inspection records.
- The application runs locally on one machine. There is no networking or multi-user support.

---

## 🔭 Future Hardware and AI Integration (Not Implemented)

The long-term SPARK vision includes:
- Real gearbox camera integration
- Hardware and sensor connectivity
- Advanced sub-pixel image registration
- Validated machine learning defect detection models
- Spatial mapping (SLAM research)
- AR-assisted technician workflows
- Integration with industrial CMMS platforms

**None of these are implemented in this prototype.**

---

## 📞 Quick Reference

| Task | Command |
|---|---|
| Activate environment | `.venv\Scripts\activate` |
| Start application | `python -m streamlit run app.py` |
| Regenerate demo images | `python sample_generator.py` |
| Run tests | `python tests/test_vision.py` |
| Deactivate environment | `deactivate` |
