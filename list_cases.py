import pandas as pd
from tools.sql_tools import run_sql_query

# Show full DataFrame without truncation
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

print(run_sql_query(
    "SELECT trans_num FROM transactions WHERE is_fraud = 0 LIMIT 5;",
    allow_is_fraud=True
))