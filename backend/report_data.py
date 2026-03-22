import pandas as pd
import numpy as np
from datetime import datetime


def get_report_data(df, filename, file_size, ops_log):
    """Collects all data needed for the report."""

    rows, cols = df.shape

    # memory size
    mem_bytes = df.memory_usage(deep=True).sum()
    if mem_bytes < 1024:
        mem_str = f"{mem_bytes} B"
    elif mem_bytes < 1024 * 1024:
        mem_str = f"{mem_bytes / 1024:.1f} KB"
    else:
        mem_str = f"{mem_bytes / (1024 * 1024):.1f} MB"

    # null stats
    total_cells  = rows * cols
    total_nulls  = int(df.isnull().sum().sum())
    null_pct     = round((total_nulls / total_cells) * 100, 1) if total_cells > 0 else 0.0
    dup_rows     = int(df.duplicated().sum())

    # health status
    if null_pct == 0 and dup_rows == 0:
        health = "Healthy"
        health_color = "#0F6E56"
    elif null_pct > 30 or dup_rows > rows * 0.1:
        health = "Critical"
        health_color = "#E24B4A"
    else:
        health = "Needs Attention"
        health_color = "#BA7517"

    # per column stats
    columns = []
    for col in df.columns:
        dtype    = str(df[col].dtype)
        if 'int'      in dtype: col_type = 'int'
        elif 'float'  in dtype: col_type = 'float'
        elif 'datetime' in dtype: col_type = 'datetime'
        else: col_type = 'object'

        count      = int(df[col].count())
        null_count = int(df[col].isnull().sum())
        null_c_pct = round(null_count / rows * 100, 1) if rows > 0 else 0.0
        unique     = int(df[col].nunique())

        if col_type in ('int', 'float'):
            mean_val = f"{df[col].mean():.2f}" if not df[col].isnull().all() else "—"
            min_val  = f"{df[col].min()}"      if not df[col].isnull().all() else "—"
            max_val  = f"{df[col].max()}"      if not df[col].isnull().all() else "—"
            std_val  = f"{df[col].std():.2f}"  if not df[col].isnull().all() else "—"
        else:
            mean_val = "—"
            min_val  = "—"
            max_val  = "—"
            std_val  = "—"

        columns.append({
            "name":       col,
            "type":       col_type,
            "count":      count,
            "null_count": null_count,
            "null_pct":   null_c_pct,
            "unique":     unique,
            "mean":       mean_val,
            "min":        min_val,
            "max":        max_val,
            "std":        std_val,
        })

    # key insights
    insights = []
    num_cols  = sum(1 for c in columns if c["type"] in ('int', 'float'))
    cat_cols  = sum(1 for c in columns if c["type"] == 'object')
    dt_cols   = sum(1 for c in columns if c["type"] == 'datetime')

    insights.append(f"Dataset has {num_cols} numeric, {cat_cols} categorical, {dt_cols} datetime columns.")

    if dup_rows > 0:
        insights.append(f"{dup_rows} duplicate rows found — consider removing them.")
    else:
        insights.append("No duplicate rows found.")

    if null_pct == 0:
        insights.append("No null values found in the dataset.")
    else:
        insights.append(f"Overall null rate is {null_pct}% across all columns.")

    for c in columns:
        if c["null_pct"] > 50:
            insights.append(f'"{c["name"]}" has {c["null_pct"]}% null values — consider dropping this column.')
        elif c["null_pct"] > 10:
            insights.append(f'"{c["name"]}" has {c["null_pct"]}% null values — consider filling or dropping.')

    for c in columns:
        if c["type"] == 'object' and c["unique"] == rows:
            insights.append(f'"{c["name"]}" has all unique values — likely an ID column.')
        if c["type"] in ('int', 'float') and c["unique"] <= 5:
            insights.append(f'"{c["name"]}" has only {c["unique"]} unique values — might be categorical.')

    return {
        "filename":    filename,
        "file_size":   file_size,
        "rows":        rows,
        "columns":     cols,
        "memory":      mem_str,
        "null_pct":    null_pct,
        "dup_rows":    dup_rows,
        "health":      health,
        "health_color": health_color,
        "col_stats":   columns,
        "insights":    insights,
        "ops_log":     ops_log,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def generate_report_html(data):
    """Generates a complete standalone HTML report."""

    # ── COLUMN STATS ROWS ────────────────────────
    col_rows = ""
    for i, c in enumerate(data["col_stats"]):
        null_color = "#E24B4A" if c["null_pct"] > 10 else ("#BA7517" if c["null_pct"] > 0 else "#0F6E56")
        type_colors = {
            "int":      ("E6F1FB", "185FA5"),
            "float":    ("EAF3DE", "3B6D11"),
            "object":   ("EEEDFE", "3C3489"),
            "datetime": ("FAEEDA", "BA7517"),
        }
        bg, fg = type_colors.get(c["type"], ("F1F0FA", "6B6889"))
        col_rows += f"""
        <tr>
            <td>{i + 1}</td>
            <td><strong>{c['name']}</strong></td>
            <td><span style="background:#{bg};color:#{fg};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600;">{c['type']}</span></td>
            <td>{c['count']:,}</td>
            <td style="color:{null_color};font-weight:{'600' if c['null_pct'] > 0 else '400'};">{c['null_pct']}%</td>
            <td>{c['unique']:,}</td>
            <td>{c['mean']}</td>
            <td>{c['min']}</td>
            <td>{c['max']}</td>
            <td>{c['std']}</td>
        </tr>"""

    # ── INSIGHTS ─────────────────────────────────
    insight_items = "".join(f"<li>{i}</li>" for i in data["insights"])

    # ── OPS LOG ──────────────────────────────────
    if data["ops_log"]:
        ops_rows = ""
        for i, op in enumerate(data["ops_log"]):
            action  = op.get("action", "—")
            column  = op.get("column", op.get("new_col_name", "—"))
            details = ", ".join(f"{k}: {v}" for k, v in op.items() if k not in ("action", "column", "new_col_name", "timestamp"))
            ts      = op.get("timestamp", "—")
            ops_rows += f"""
            <tr>
                <td>{i + 1}</td>
                <td><code>{action}</code></td>
                <td>{column}</td>
                <td>{details}</td>
                <td>{ts}</td>
            </tr>"""
        ops_section = f"""
        <div class="section">
            <h2>Operations Log</h2>
            <table>
                <thead><tr><th>#</th><th>Action</th><th>Column</th><th>Details</th><th>Timestamp</th></tr></thead>
                <tbody>{ops_rows}</tbody>
            </table>
        </div>"""
    else:
        ops_section = """
        <div class="section">
            <h2>Operations Log</h2>
            <p class="muted">No operations performed on this dataset.</p>
        </div>"""

    # ── FULL HTML ─────────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>PilotDF Report — {data['filename']}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #F7F7FB; color: #1A1830; font-size: 14px; line-height: 1.6; }}
    .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem 2rem 4rem; }}
    .header {{ background: #534AB7; color: white; padding: 2rem 2.5rem; border-radius: 12px; margin-bottom: 2rem; }}
    .header h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 4px; }}
    .header .meta {{ font-size: 13px; opacity: 0.8; }}
    .section {{ background: white; border: 1px solid #E2E1F0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
    .section h2 {{ font-size: 16px; font-weight: 600; color: #534AB7; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #E2E1F0; }}
    .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; margin-bottom: 1rem; }}
    .stat-card {{ background: #F1F0FA; border-radius: 8px; padding: 1rem; }}
    .stat-label {{ font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; color: #A09DBF; }}
    .stat-value {{ font-size: 20px; font-weight: 700; color: #1A1830; font-family: 'Courier New', monospace; }}
    .health-badge {{ display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; color: white; background: {data['health_color']}; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    thead th {{ padding: 10px 12px; text-align: left; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: #A09DBF; background: #F1F0FA; border-bottom: 1px solid #E2E1F0; white-space: nowrap; }}
    tbody tr {{ border-bottom: 1px solid #E2E1F0; }}
    tbody tr:last-child {{ border-bottom: none; }}
    tbody tr:hover {{ background: #F7F7FB; }}
    tbody td {{ padding: 9px 12px; color: #1A1830; }}
    code {{ font-family: 'Courier New', monospace; background: #EEEDFE; color: #534AB7; padding: 2px 6px; border-radius: 4px; font-size: 12px; }}
    ul.insights {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
    ul.insights li {{ display: flex; align-items: flex-start; gap: 8px; font-size: 13px; }}
    ul.insights li::before {{ content: '→'; color: #534AB7; font-weight: 700; flex-shrink: 0; }}
    .muted {{ color: #A09DBF; font-size: 13px; }}
    .footer {{ text-align: center; color: #A09DBF; font-size: 12px; margin-top: 2rem; }}
    @media print {{ body {{ background: white; }} .section {{ break-inside: avoid; }} }}
  </style>
</head>
<body>
  <div class="container">

    <!-- HEADER -->
    <div class="header">
      <h1>📊 PilotDF Data Report</h1>
      <div class="meta">File: {data['filename']} &nbsp;|&nbsp; Generated: {data['generated_at']}</div>
    </div>

    <!-- DATASET OVERVIEW -->
    <div class="section">
      <h2>Dataset Overview</h2>
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-label">Rows</div><div class="stat-value">{data['rows']:,}</div></div>
        <div class="stat-card"><div class="stat-label">Columns</div><div class="stat-value">{data['columns']}</div></div>
        <div class="stat-card"><div class="stat-label">File Size</div><div class="stat-value">{data['file_size']}</div></div>
        <div class="stat-card"><div class="stat-label">Memory</div><div class="stat-value">{data['memory']}</div></div>
        <div class="stat-card"><div class="stat-label">Null %</div><div class="stat-value" style="color:{'#E24B4A' if data['null_pct'] > 10 else '#0F6E56'};">{data['null_pct']}%</div></div>
        <div class="stat-card"><div class="stat-label">Duplicates</div><div class="stat-value" style="color:{'#E24B4A' if data['dup_rows'] > 0 else '#0F6E56'};">{data['dup_rows']}</div></div>
      </div>
      <div>Health Status: <span class="health-badge">{data['health']}</span></div>
    </div>

    <!-- KEY INSIGHTS -->
    <div class="section">
      <h2>Key Insights</h2>
      <ul class="insights">{insight_items}</ul>
    </div>

    <!-- COLUMN STATS -->
    <div class="section">
      <h2>Column Statistics</h2>
      <div style="overflow-x:auto;">
        <table>
          <thead>
            <tr>
              <th>#</th><th>Column</th><th>Type</th><th>Count</th>
              <th>Null %</th><th>Unique</th><th>Mean</th><th>Min</th><th>Max</th><th>Std</th>
            </tr>
          </thead>
          <tbody>{col_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- OPS LOG -->
    {ops_section}

    <div class="footer">Generated by PilotDF &nbsp;|&nbsp; {data['generated_at']}</div>
  </div>
</body>
</html>"""

    return html