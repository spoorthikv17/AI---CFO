import sqlite3
import pandas as pd


def connect_to_database(db_path):
    """Create a connection to the SQLite database."""
    return sqlite3.connect(db_path)


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