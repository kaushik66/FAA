import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from config import ARTIFACT_DIR
from tools.sql_tools import run_sql_query

os.makedirs(ARTIFACT_DIR, exist_ok=True)


def plot_time_series(df: pd.DataFrame, title: str = "Transaction Amounts Over Time") -> str:
    if "trans_date" not in df.columns or "amount" not in df.columns:
        raise ValueError("trans_date and amount columns required for plotting")
    d = df.dropna(subset=["trans_date"]).sort_values("trans_date")
    if d.empty:
        raise ValueError("no timestamped rows to plot")

    plt.figure()
    plt.plot(d["trans_date"], d["amount"])  # no explicit colors/styles (keeps it simple)
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Amount")
    fname = os.path.join(ARTIFACT_DIR, f"timeseries_{int(datetime.now().timestamp())}.png")
    plt.savefig(fname, bbox_inches="tight")
    plt.close()
    return fname


def plot_transaction_timeline(identifier: str) -> str:
    if identifier.isdigit() and len(identifier) > 12:
        query = """
            SELECT trans_date, amount 
            FROM transactions 
            WHERE cc_num = ?
            ORDER BY trans_date;
        """
        params = (identifier,)
    else:
        query = """
            SELECT trans_date, amount 
            FROM transactions 
            WHERE cc_num = (
                SELECT cc_num FROM transactions WHERE trans_num = ?
            )
            ORDER BY trans_date;
        """
        params = (identifier,)

    df = run_sql_query(query, params=params)
    df["trans_date"] = pd.to_datetime(df["trans_date"], errors="coerce")
    return plot_time_series(df, title=f"Timeline for TX {identifier}")