# SPARK — Faculty Demonstration Script

> **Duration: ~3 minutes | Format: Live browser demo | Audience: B.Tech faculty**

---

## Before You Begin

1. Open PowerShell in the SPARK folder:
   ```
   cd "C:\Users\singh\OneDrive\Desktop\SPARK"
   .venv\Scripts\activate
   python -m streamlit run app.py
   ```
2. The browser will open at `http://localhost:8501`.
3. Keep this script open on a second screen or printed.

---

## 3-Minute Live Demonstration Script

### Minute 1 — Overview and Image Comparison

**[CLICK: 🏠 Overview in sidebar]**

> "This is SPARK — a Spatial AI Repair Knowledge Platform prototype. The dashboard shows the overall system. This panel here reflects real data from the SQLite database — currently zero or a few records depending on what we've saved."

Point to the demo gearbox card:
> "We have one illustrative gearbox case set up. The images below are programmatically generated schematics — not real photographs — which is important: this is a software prototype for academic demonstration."

**[CLICK: 🔍 Gearbox Inspection in sidebar]**

**[CLICK: 📁 Load Demo Images]**

> "We load the reference schematic — the baseline state of the gearbox — and the current inspection schematic, which has an obvious marked region added to it."

**[CLICK: ⚡ Compare Images]**

> "The system runs a pixel-level comparison using the Pillow library. Red pixels appear wherever the current image differs significantly from the reference, above a configurable sensitivity threshold."

Point to the visual change percentage:
> "This number — say 8% — means approximately 8% of pixels exceeded our difference threshold. **This is a visual comparison metric, not a probability of fault.** The system makes no claim about what caused the difference or whether any repair is needed."

---

### Minute 2 — Records and Guidance

**[IN THE FORM BELOW COMPARISON RESULTS]**

Fill in:
- Technician Name: `Demo Engineer`
- Observations: `Orange marked region visible on upper-left of drive gear area. Refer to qualified engineer.`
- Status: `Pending Review`

**[CLICK: 💾 Save Record]**

> "The record is saved to a local SQLite database. It persists between restarts — if I close and reopen the app, this record will still be here."

**[CLICK: 📋 Repair Guidance in sidebar]**

> "The guidance page provides a 10-step observational checklist. Notice it starts with safety — verifying equipment isolation and lockout/tagout. The system explicitly does not diagnose faults or recommend specific repairs. It guides a technician to document observations and escalate to a qualified engineer."

---

### Minute 3 — Records, Reports, and About

**[CLICK: 📁 Repair Records in sidebar]**

> "All saved records appear here. You can filter by status, expand a record to view its details and stored images, and update the review status as the inspection progresses."

**[CLICK: 📄 Reports in sidebar]**

> "Select the record we just saved and click Generate PDF Report."

**[CLICK: ⚙ Generate PDF Report]**

> "ReportLab generates a professional PDF containing the record details, all three images, the change percentage, technician observations, and an explicit disclaimer that this is a demonstration document — not a certified inspection report."

**[CLICK: ⬇ Download PDF Report]**  — open it to show the faculty.

**[CLICK: ℹ About SPARK in sidebar]**

> "The About page clearly separates what is implemented in this prototype from what is planned in the full future vision — spatial mapping, hardware integration, AI defect detection, and AR workflows. None of those are claimed to be present here."

---

## Explaining the Highlighted Image to Faculty

*"The red pixels show regions where the colour values in the current image differ from the reference by more than 30 out of 255 per channel. This is purely a visual comparison — like a digital spot-the-difference. It tells a technician where to look, not what the problem is. A qualified maintenance engineer must assess whether any difference is mechanically significant."*

---

## Why the Visual Change % Is Not a Fault Probability

*"A fault probability would require a validated machine learning model trained on thousands of real gearbox failure images with confirmed ground-truth labels. We have none of that here. Our percentage simply counts how many pixels changed. Lighting angle, camera position, or even a fingerprint on the lens would increase the percentage without any mechanical fault existing."*

---

## Current Prototype Limitations

| Limitation | Explanation |
|---|---|
| No real images | Schematics are generated with Pillow — no camera hardware |
| Basic pixel diff | No image registration, alignment, or sub-pixel accuracy |
| No AI / ML | No trained models — rule-based threshold only |
| No hardware | No sensor, PLC, or IoT integration |
| Single-user local | No networking, cloud, or multi-user support |
| Demo records only | Not real industrial service history |

---

## Future Development Roadmap

1. **Phase 1** — Real camera integration for actual gearbox photography
2. **Phase 2** — Advanced image registration for consistent alignment across sessions
3. **Phase 3** — Machine learning defect detection (requires real training data)
4. **Phase 4** — Spatial mapping and SLAM research for 3D surface understanding
5. **Phase 5** — AR overlay for on-site technician guidance
6. **Phase 6** — CMMS integration for enterprise maintenance management

---

## Five Likely Faculty Questions — with Accurate Answers

---

**Q1: "How is this different from just Photoshop's difference blend mode?"**

> "Functionally the core idea is the same — compute absolute pixel differences between two images. SPARK adds a structured workflow around that operation: a technician dashboard, guided checklist, SQLite record management, and PDF reporting. The value is in the workflow, not just the image math. A real system would add image registration, camera calibration, and validated defect models on top."

---

**Q2: "Why doesn't the system tell us what the fault is?"**

> "Diagnosing a mechanical fault from a photograph requires validated ground-truth training data, domain-expert labels, and rigorous model evaluation — none of which exist for this prototype. Making unvalidated fault claims would be technically dishonest and potentially unsafe. The system correctly limits itself to flagging visual differences and directing a qualified engineer."

---

**Q3: "What would you need to make this production-ready?"**

> "At minimum: a calibrated inspection camera with consistent mounting, a dataset of real gearbox images with expert-annotated faults, a trained and validated computer vision model, image registration to handle camera position variation, and integration with an existing CMMS. The software architecture here could scale to support all of those — the database schema and module structure are designed with that in mind."

---

**Q4: "Why Streamlit and not a native desktop app or a mobile app?"**

> "Streamlit allowed rapid, reliable prototyping with a professional-looking result using only Python. For this academic prototype, development velocity and reliability were more important than deployment target. A production version could use the same Python backend with a React or Flutter frontend, or integrate directly into an existing industrial HMI system."

---

**Q5: "Is the 15% visual change number you demonstrated meaningful?"**

> "In the context of this prototype, it means 15% of pixels differed by more than our threshold between the two images. Whether that is meaningful for a real gearbox depends on: how consistently the images were taken, what components are in the highlighted region, and what a qualified engineer determines about those components. The number itself has no inherent meaning without that context — which is exactly why the system labels it explicitly as a visual comparison metric."

---

*End of demonstration script.*
