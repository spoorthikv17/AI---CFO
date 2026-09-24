import sqlite3
import pandas as pd

from financial_analysis import (
    calculate_financial_summary,
    calculate_profit_margin,
     calculate_cash_flow
)

def connect_to_database(db_path):
    """Create a connection to the SQLite database."""
    return sqlite3.connect(db_path)

def load_transactions_from_database(db_path):
    """Load transactions from the SQLite database."""

    conn = connect_to_database(db_path)

    transactions = pd.read_sql_query(
        "SELECT * FROM transactions",
        conn
    )

    conn.close()

    transactions["date"] = pd.to_datetime(transactions["date"])

    return transactions

def save_transactions(transactions, db_path):
    """Save transaction data into the SQLite database."""

    conn = connect_to_database(db_path)

    existing_count = conn.execute(
        "SELECT COUNT(*) FROM transactions"
    ).fetchone()[0]

    if existing_count == 0:
        transactions.to_sql(
            "transactions",
            conn,
            if_exists="append",
            index=False
        )

        print("Transactions saved to database successfully.")

    else:
        print("Transactions already exist in database. No duplicate data inserted.")

    conn.close()


if __name__ == "__main__":
    file_path = "data/transactions.csv"
    db_path = "data/ai_cfo.db"

    transactions = pd.read_csv(file_path)

    save_transactions(transactions, db_path)

    database_transactions = load_transactions_from_database(db_path)

    print("\n===== Transactions Loaded From Database =====")
    print(database_transactions.head())

summary = calculate_financial_summary(database_transactions)

profit_margin = calculate_profit_margin(
    summary["total_income"],
    summary["profit"]
)

print("\n===== Financial Analysis From Database =====")
print(f"Total Income   : ₹{summary['total_income']:,.2f}")
print(f"Total Expenses : ₹{summary['total_expenses']:,.2f}")
print(f"Profit         : ₹{summary['profit']:,.2f}")
print(f"Profit Margin  : {profit_margin:.2f}%")

cash_flow = calculate_cash_flow(database_transactions)

print("\n===== Cash Flow Analysis =====")
print(cash_flow)