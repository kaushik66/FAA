import os
import glob
import sqlite3
from typing import List, Optional
import pandas as pd
from datetime import datetime
from config import DB_PATH, DATA_DIR

TRANSACTION_HINT_COLUMNS = {"amount", "is_fraud", "timestamp", "trans_date", "merchant", "customer_id", "merchant_id"}


def _read_csv_safe(path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(path, sep="|", on_bad_lines="skip", low_memory=False)
    except Exception:
        return None


def build_sqlite_from_csvs() -> str:
    paths = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
    if not paths:
        raise FileNotFoundError(f"No CSVs found in {DATA_DIR}")

    dfs: List[pd.DataFrame] = []
    for p in paths:
        df = _read_csv_safe(p)
        if df is None or df.empty:
            continue
        df.columns = [c.strip().lower() for c in df.columns]

        # Remove duplicate columns within the same file
        df = df.loc[:, ~df.columns.duplicated()]

        cols = set(df.columns)
        if len(cols.intersection(TRANSACTION_HINT_COLUMNS)) >= 2:
            # Normalize common columns
            if "amount" not in df.columns:
                for alt in ("amt", "transaction_amount"):
                    if alt in df.columns:
                        df.rename(columns={alt: "amount"}, inplace=True)
                        break
            if "timestamp" not in df.columns:
                for alt in ("trans_time", "trans_date", "transaction_time", "time", "datetime"):
                    if alt in df.columns:
                        df.rename(columns={alt: "timestamp"}, inplace=True)
                        break
            if "is_fraud" not in df.columns:
                for alt in ("fraud", "label", "is_fraudulent"):
                    if alt in df.columns:
                        df.rename(columns={alt: "is_fraud"}, inplace=True)
                        break
            dfs.append(df)

    if not dfs:
        raise RuntimeError("No transaction-like CSVs detected. Check your data directory.")

    # Merge and drop duplicate columns across all files
    big = pd.concat(dfs, ignore_index=True, sort=False)
    big = big.loc[:, ~big.columns.duplicated()]

    big = pd.concat(dfs, ignore_index=True, sort=False)

    # Clean column names
    big.columns = [c.strip() for c in big.columns]

    # Drop unwanted columns like .1 or containing commas
    drop_cols = [c for c in big.columns if c.endswith('.1') or ',' in c]
    big.drop(columns=drop_cols, inplace=True, errors='ignore')

    # Remove duplicate columns again after cleanup
    big = big.loc[:, ~big.columns.duplicated()]

    # Fill required columns if missing
    for col, default in ("is_fraud", 0), ("amount", 0.0), ("merchant", ""), ("merchant_id", -1), ("customer_id", -1):
        if col not in big.columns:
            big[col] = default

    if "merchant" in big.columns:
        big["merchant"] = big["merchant"].astype(str).str.replace(r"^fraud_", "", regex=True)

    # Timestamp parsing (best‑effort)
    if "timestamp" in big.columns:
        def _parse_ts(x):
            s = str(x)
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S", "%m-%d-%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S",
                        "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    pass
            return pd.NaT
        big["timestamp"] = big["timestamp"].apply(_parse_ts)

    conn = sqlite3.connect(DB_PATH)
    big.to_sql("transactions", conn, if_exists="replace", index=False)
    conn.close()
    return DB_PATH


def run_sql_query(sql, params=None, allow_is_fraud: bool = False):
    # Prevent access to restricted columns like is_fraud
    if not allow_is_fraud and "is_fraud" in str(sql).lower():
        raise ValueError("Access to is_fraud column is not allowed during investigation.")
    conn = sqlite3.connect(DB_PATH)
    try:
        if params is None:
            return pd.read_sql_query(sql, conn)
        else:
            return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()


def get_columns(table: str = "transactions") -> list:
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(f"PRAGMA table_info({table})", conn)["name"].tolist()
    finally:
        conn.close()