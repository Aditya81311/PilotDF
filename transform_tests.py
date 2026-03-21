import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.transform_data import (
    new_column, normalize, encode,
    bin_numaric, extract_datetime, apply_maths
)

# ── HELPERS ──────────────────────────────────────
passed = 0
failed = 0

def test(name, condition, details=""):
    global passed, failed
    if condition:
        print(f"  ✅ PASS — {name}")
        passed += 1
    else:
        print(f"  ❌ FAIL — {name} {details}")
        failed += 1

def safe_test(name, fn):
    try:
        condition, details = fn()
        test(name, condition, details)
    except Exception as e:
        test(name, False, f"[Exception: {e}]")

def section(name):
    print(f"\n── {name} {'─' * (50 - len(name))}")

def make_df():
    return pd.DataFrame({
        "price":    [10.0, 20.0, 30.0, 40.0, 50.0],
        "quantity": [1, 2, 3, 4, 5],
        "category": ["a", "b", "a", "c", "b"],
        "score":    [-5.0, -2.0, 0.0, 3.0, 8.0],
        "date":     ["2021-01-01", "2021-06-15", "2022-03-10", "2023-07-20", "2024-12-31"],
    })

# ── NEW COLUMN ───────────────────────────────────
section("new_column")

safe_test("create column from formula", lambda: (
    "total" in new_column(make_df(), "total", "price * quantity").columns, ""))

safe_test("formula result is correct", lambda: (
    new_column(make_df(), "total", "price * quantity")["total"].iloc[0] == 10.0, ""))

safe_test("returns dataframe", lambda: (
    isinstance(new_column(make_df(), "total", "price * quantity"), pd.DataFrame), ""))

safe_test("invalid formula returns df", lambda: (
    isinstance(new_column(make_df(), "bad", "price $$$ quantity"), pd.DataFrame), ""))

safe_test("simple addition formula", lambda: (
    new_column(make_df(), "sum_col", "price + quantity")["sum_col"].iloc[0] == 11.0, ""))

# ── NORMALIZE ────────────────────────────────────
section("normalize")

safe_test("minmax — min is 0", lambda: (
    normalize(make_df(), "price", "minmax")["price"].min() == 0.0, ""))

safe_test("minmax — max is 1", lambda: (
    normalize(make_df(), "price", "minmax")["price"].max() == 1.0, ""))

safe_test("zscore — mean is ~0", lambda: (
    abs(normalize(make_df(), "price", "zscore")["price"].mean()) < 1e-10, ""))

safe_test("zscore — returns dataframe", lambda: (
    isinstance(normalize(make_df(), "price", "zscore"), pd.DataFrame), ""))

safe_test("minmax — returns dataframe", lambda: (
    isinstance(normalize(make_df(), "price", "minmax"), pd.DataFrame), ""))

safe_test("invalid method returns df", lambda: (
    isinstance(normalize(make_df(), "price", "invalid"), pd.DataFrame), ""))

# ── ENCODE ───────────────────────────────────────
section("encode")

safe_test("label encode — returns dataframe", lambda: (
    isinstance(encode(make_df(), "category", "label", "false"), pd.DataFrame), ""))

safe_test("label encode — column is numeric", lambda: (
    encode(make_df(), "category", "label", "false")["category"].dtype in [np.int32, np.int64, int], ""))

safe_test("onehot encode — original column dropped", lambda: (
    "category" not in encode(make_df(), "category", "onehot", "false").columns, ""))

safe_test("onehot encode — new columns created", lambda: (
    len(encode(make_df(), "category", "onehot", "false").columns) > len(make_df().columns), ""))

safe_test("onehot drop_first=true — one less column", lambda: (
    len(encode(make_df(), "category", "onehot", "true").columns) <
    len(encode(make_df(), "category", "onehot", "false").columns), ""))

safe_test("onehot returns dataframe", lambda: (
    isinstance(encode(make_df(), "category", "onehot", "false"), pd.DataFrame), ""))

# ── BIN NUMERIC ──────────────────────────────────
section("bin_numaric")

safe_test("bin with int bins — returns dataframe", lambda: (
    isinstance(bin_numaric(make_df(), "price", "4", ""), pd.DataFrame), ""))

safe_test("bin with labels — labels applied", lambda: (
    bin_numaric(make_df(), "price", "2", "low,high")["price"].dtype.name == "category", ""))

safe_test("bin label count mismatch — returns df unchanged", lambda: (
    list(bin_numaric(make_df(), "price", "4", "low,high").columns) == list(make_df().columns), ""))

safe_test("bin without labels — uses interval labels", lambda: (
    bin_numaric(make_df(), "price", "3", "")["price"].dtype.name == "category", ""))

safe_test("bin with 2 bins — returns dataframe", lambda: (
    isinstance(bin_numaric(make_df(), "price", "2", ""), pd.DataFrame), ""))

# ── EXTRACT DATETIME ─────────────────────────────
section("extract_datetime")

safe_test("extract year — new column created", lambda: (
    "year" in extract_datetime(make_df(), "date", "year").columns, ""))

safe_test("extract year — correct values", lambda: (
    extract_datetime(make_df(), "date", "year")["year"].iloc[0] == 2021, ""))

safe_test("extract month — new column created", lambda: (
    "month" in extract_datetime(make_df(), "date", "month").columns, ""))

safe_test("extract month — correct values", lambda: (
    extract_datetime(make_df(), "date", "month")["month"].iloc[0] == 1, ""))

safe_test("extract day — correct values", lambda: (
    extract_datetime(make_df(), "date", "day")["day"].iloc[0] == 1, ""))

safe_test("extract weekday — returns dataframe", lambda: (
    isinstance(extract_datetime(make_df(), "date", "weekday"), pd.DataFrame), ""))

safe_test("extract hour — returns dataframe", lambda: (
    isinstance(extract_datetime(make_df(), "date", "hour"), pd.DataFrame), ""))

# ── APPLY MATHS ──────────────────────────────────
section("apply_maths")

safe_test("abs — no negative values", lambda: (
    apply_maths(make_df(), "score", "abs")["score"].min() >= 0, ""))

safe_test("square — values squared", lambda: (
    apply_maths(make_df(), "price", "square")["price"].iloc[0] == 100.0, ""))

safe_test("round — returns dataframe", lambda: (
    isinstance(apply_maths(make_df(), "price", "round"), pd.DataFrame), ""))

safe_test("sqrt on positive col — returns dataframe", lambda: (
    isinstance(apply_maths(make_df(), "price", "sqrt"), pd.DataFrame), ""))

safe_test("log on positive col — returns dataframe", lambda: (
    isinstance(apply_maths(make_df(), "price", "log"), pd.DataFrame), ""))

safe_test("invalid operation returns None or df", lambda: (
    apply_maths(make_df(), "price", "invalid") is None or
    isinstance(apply_maths(make_df(), "price", "invalid"), pd.DataFrame), ""))

safe_test("sqrt result correct", lambda: (
    abs(apply_maths(make_df(), "price", "sqrt")["price"].iloc[0] - np.sqrt(10.0)) < 1e-10, ""))

# ── SUMMARY ──────────────────────────────────────
total = passed + failed
print(f"\n{'=' * 52}")
print(f"  Results: {passed}/{total} passed  |  {failed} failed")
print(f"{'=' * 52}")
if failed == 0:
    print("  All tests passed!")
else:
    print("  Fix the failing tests before proceeding.")