import pandas as pd
import numpy as np


def get_dashboard_data(df, filename, file_size):
    rows, cols = df.shape

    # Memory size
    mem_bytes = df.memory_usage(deep=True).sum()
    if mem_bytes < 1024:
        mem_str = f"{mem_bytes} B"
    elif mem_bytes < 1024 * 1024:
        mem_str = f"{mem_bytes / 1024:.1f} KB"
    else:
        mem_str = f"{mem_bytes / (1024 * 1024):.1f} MB"

    # Null stats
    total_cells = rows * cols
    total_nulls = df.isnull().sum().sum()
    null_pct = round((total_nulls / total_cells) * 100, 1) if total_cells > 0 else 0.0

    # Duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    # Health status
    if null_pct == 0 and duplicate_rows == 0:
        health_status = "ok"
    elif null_pct > 30 or duplicate_rows > rows * 0.1:
        health_status = "bad"
    else:
        health_status = "warn"

    # Issues list
    issues = []
    col_null_pcts = (df.isnull().sum() / rows * 100).round(1)
    for col, pct in col_null_pcts.items():
        if pct > 0:
            issues.append({
                "type": "warn" if pct > 5 else "ok",
                "message": f"{col} has {pct}% null values"
            })
    if duplicate_rows > 0:
        issues.append({"type": "warn", "message": f"{duplicate_rows} duplicate rows found"})
    else:
        issues.append({"type": "ok", "message": "No duplicate rows found"})

    # Column overview
    overview = []
    for i, col in enumerate(df.columns):
        dtype = str(df[col].dtype)
        if 'int' in dtype:
            col_type = 'int'
        elif 'float' in dtype:
            col_type = 'float'
        elif 'datetime' in dtype:
            col_type = 'datetime'
        else:
            col_type = 'object'

        count = int(df[col].count())
        null_col_pct = round(df[col].isnull().sum() / rows * 100, 1)
        unique = int(df[col].nunique())

        if col_type in ('int', 'float'):
            mean_val = f"{df[col].mean():.2f}" if not df[col].isnull().all() else "—"
            min_val  = f"{df[col].min()}"      if not df[col].isnull().all() else "—"
            max_val  = f"{df[col].max()}"      if not df[col].isnull().all() else "—"
        else:
            mean_val = "—"
            min_val  = "—"
            max_val  = "—"

        overview.append({
            "name":     col,
            "type":     col_type,
            "count":    count,
            "null_pct": null_col_pct,
            "unique":   unique,
            "mean":     mean_val,
            "min":      min_val,
            "max":      max_val,
        })

    return {
        "file_name":       filename,
        "rows":            rows,
        "columns":         cols,
        "file_size":       file_size,
        "memory_size":     mem_str,
        "null_pct":        null_pct,
        "duplicate_rows":  duplicate_rows,
        "health_status":   health_status,
        "issues":          issues,
        "overview":        overview,
    }