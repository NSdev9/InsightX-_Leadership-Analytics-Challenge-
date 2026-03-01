import pandas as pd
import duckdb
import re

con = None


def init_db():
    global con

    # Load CSV
    df = pd.read_csv("upi_transactions_2024.csv")

    # ----------------------------
    # Clean Column Names Properly
    # ----------------------------
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("\n", "", regex=False)
        .str.replace(" ", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # Extra safety: remove any remaining special characters
    df.columns = [re.sub(r'[^a-z0-9_]', '', col) for col in df.columns]

    # Now your columns will look like:
    # transaction_id
    # timestamp
    # transaction_type
    # merchant_category
    # amount_inr
    # fraud_flag
    # hour_of_day
    # etc.

    # ----------------------------
    # Create In-Memory DuckDB
    # ----------------------------
    con = duckdb.connect(database=":memory:")

    # Register dataframe temporarily
    con.register("df_temp", df)

    # Create actual table
    con.execute("""
        CREATE OR REPLACE TABLE upi_transactions AS
        SELECT * FROM df_temp
    """)

    print("✅ Database initialized successfully with cleaned columns.")


def run_query(sql):
    global con

    try:
        result = con.execute(sql).fetchdf()
        return result

    except Exception as e:
        print("DB Error:", e)
        return None