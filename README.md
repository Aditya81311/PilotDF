# PilotDF — No-Code Data Analysis Platform

> A session-based, low-code/no-code data analysis web application built with Flask and Pandas. Upload a CSV or Excel file and instantly clean, transform, visualize, and export your data — no coding required.

---

## Features

- **Upload** — CSV and Excel (.xlsx, .xls) file support, up to 50MB
- **Dashboard** — File info, data health card, column overview, quick actions
- **View Data** — Paginated table with right-click context menu for quick navigation
- **Clean** — Fill nulls, drop rows/columns, rename, change types, find & replace, trim, case change, reorder, remove duplicates — with full undo support
- **Transform** — Create new columns, normalize, encode categorical, bin numeric, extract datetime, apply math operations — with full undo support
- **Visualize** — Bar, Line, Scatter, Histogram, Pie, Box charts powered by Plotly — multiple charts on one canvas, draggable and resizable
- **Report** — Auto-generated data report with key insights, column stats, operations log — export as PDF or HTML
- **Download** — Download current (cleaned/transformed) data as CSV at any point

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Backend | Flask, Pandas, NumPy, OpenPyXL, Flask-Session |
| File Handling | Werkzeug, UUID temp folders, os/shutil |
| Data Operations | Pandas, NumPy, Scikit-learn |
| Visualization | Plotly |
| Export | WeasyPrint (PDF), BytesIO (CSV) |
| Frontend | Bootstrap 5, Custom CSS, Vanilla JS, Fetch API |
| Charts | Plotly.js (cdnjs) |

---

## Project Structure

```
PilotDF/
├── app.py                      ← Entry point, registers blueprints, session config
├── config.py                   ← App config (upload folder, secret key, file size limit)
├── requirements.txt
│
├── backend/                    ← Pure Python logic, no Flask
│   ├── file_handler.py         ← Upload, pickle, session folders, ops log, undo
│   ├── analyzer.py             ← Dashboard stats, health card, column overview
│   ├── clean_data.py           ← All cleaning functions
│   ├── transform_data.py       ← All transformation functions
│   ├── view_data.py            ← Paginated data fetch
│   ├── visualize_data.py       ← Plotly chart generation
│   └── report_data.py          ← Report data collection + HTML generation
│
├── blueprints/                 ← Flask blueprints, one per feature
│   ├── upload.py               ← File upload, reset, landing page
│   ├── dashboard.py            ← Dashboard route
│   ├── view.py                 ← View data route
│   ├── clean.py                ← All clean routes + undo
│   ├── transform.py            ← All transform routes + undo
│   ├── visualize.py            ← Chart generation route
│   └── report.py               ← Report + PDF/HTML download routes
│
├── static/
│   ├── css/                    ← Per-page CSS files
│   └── js/                     ← Per-page JS files
│
└── templates/                  ← Jinja2 HTML templates
    ├── index.html              ← Upload / landing page
    ├── dashboard.html
    ├── view_data.html
    ├── clean.html
    ├── transform.html
    ├── visualize.html
    └── report.html
```

---

## Data Handling

PilotDF uses a **no-database architecture** for data operations. Each user session gets a UUID-named temporary folder:

```
uploads/
└── uuid-session-id/
    ├── original.csv      ← Never touched — used for full reset
    ├── working.pkl       ← Current state — all operations applied here
    └── ops_log.json      ← Operation history for staged undo
```

**Undo system** — re-applies all operations except the last one from `original.csv` using `ops_log.json`. Zero extra disk space — no snapshots.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Aditya81311/PilotDF.git
cd PilotDF

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .key file with secret key
echo SECRET_KEY=your-secret-key-here > .key

# Run
python app.py
```

Visit `http://localhost:5000`

---

## Generating a Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output into your `.key` file:
```
SECRET_KEY=paste-generated-key-here
```

---

## Requirements

```
flask
flask-session
pandas
numpy
openpyxl
werkzeug
python-dotenv
fpdf2
weasyprint
scikit-learn
plotly
```

---

## Clean Tab — Supported Operations

| Operation | Description |
|-----------|-------------|
| Fill Nulls | Mean / Median / Mode / Custom value |
| Drop Rows | By scope: this column / any null / all null |
| Drop Column | Permanently removes a column |
| Rename Column | Rename with duplicate check |
| Change Data Type | int / float / str / datetime |
| Find & Replace | Exact or partial match |
| Trim Whitespace | String columns only |
| Change Case | UPPER / lower / Title |
| Reorder Columns | Drag and drop |
| Remove Duplicates | Keep first or last |

---

## Transform Tab — Supported Operations

| Operation | Description |
|-----------|-------------|
| New Column | Formula-based (e.g. `price * quantity`) |
| Normalize | Min-Max (0–1) or Z-Score |
| Encode | Label Encoding or One-Hot Encoding |
| Bin Numeric | Custom bins with optional labels |
| Extract Datetime | Year / Month / Day / Weekday / Hour |
| Apply Math | Log / Sqrt / Abs / Square / Round |

---

## Visualize Tab — Supported Charts

- Bar Chart
- Line Chart
- Scatter Plot
- Histogram
- Pie Chart
- Box Plot

Multiple charts can be added to the same canvas. Charts are draggable and the canvas can be downloaded as a single image.

Note:
 Visualize Tab is under development, Basic Visualizations are possible in current version.

---

## Flow

```
Upload CSV/Excel
      ↓
Session created → UUID temp folder
      ↓
original.csv + working.pkl saved
      ↓
Dashboard → View → Clean → Transform → Visualize → Report
      ↓
Download cleaned CSV or full Report (PDF/HTML)
      ↓
Session ends → temp folder cleaned up
```

---

## Known Limitations (v1 — Session Based)

- No user accounts — data is lost when session ends
- No persistent storage — all operations are in-memory/temp
- Visualize tab requires cdnjs access for Plotly.js
- WeasyPrint required for PDF export (may need system dependencies)
- No collaborative features

---

## Roadmap (v2 — React + Node)

- React frontend with proper state management
- User authentication and persistent storage
- Better chart rendering and interactivity
- Deployment on cloud with persistent sessions
- API-first architecture

---

## Author

**Aditya Gangurde**
- GitHub: [github.com/Aditya81311](https://github.com/Aditya81311)
- LinkedIn: [linkedin.com/in/aditya-gangurde-9a0346320](https://linkedin.com/in/aditya-gangurde-9a0346320)
- Email: aditya81311@gmail.com

---

## License

MIT License — feel free to use, modify and distribute.
