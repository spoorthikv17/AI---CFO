import sqlite3
import pandas as pd

from financial_analysis import (
    calculate_financial_summary,
    calculate_profit_margin,
    calculate_cash_flow,
    calculate_expense_by_category,
    identify_largest_expense,
    calculate_expense_ratio,
    calculate_financial_trend,
    generate_financial_insights,
    generate_financial_alerts,
    detect_large_expenses,
    calculate_transaction_risk,
    summarize_financial_risk
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
expense_by_category = calculate_expense_by_category(
    database_transactions
)

largest_expense = identify_largest_expense(
    expense_by_category
)

print("\n===== Largest Expense =====")
print(f"Category : {largest_expense['category']}")
print(f"Amount   : ₹{largest_expense['amount']:,.2f}")
expense_ratio = calculate_expense_ratio(
    summary["total_income"],
    summary["total_expenses"]
)

print("\n===== Financial Health =====")
print(f"Expense Ratio : {expense_ratio:.2f}%")
financial_trend = calculate_financial_trend(
    database_transactions
)

print("\n===== Financial Trend =====")
print(financial_trend)
insights = generate_financial_insights(
    summary,
    profit_margin,
    expense_ratio,
    largest_expense
)

print("\n===== AI CFO Insights =====")

for insight in insights:
    print(f"• {insight}")

alerts = generate_financial_alerts(
    profit_margin,
    expense_ratio,
    largest_expense
)

print("\n===== Financial Alerts =====")

for alert in alerts:
    print(f"⚠️ {alert}")

    large_expenses = detect_large_expenses(
        database_transactions
    )

    print("\n===== Large Expense Anomalies =====")

    if large_expenses.empty:
        print("No unusually large expenses detected.")
    else:
        print(large_expenses[
            ["date", "description", "category", "amount"]
        ])

    risk_analysis = calculate_transaction_risk(
        database_transactions
    )

    print("\n===== Transaction Risk Analysis =====")

    if risk_analysis.empty:
        print("No expense transactions available.")
    else:
        print(
            risk_analysis[
                [
                    "date",
                    "description",
                    "category",
                    "amount",
                    "risk_level"
                ]
            ]
        )

        risk_summary = summarize_financial_risk(
        risk_analysis
    )

    print("\n===== Overall Financial Risk =====")
    print(f"High Risk Transactions   : {risk_summary['high']}")
    print(f"Medium Risk Transactions : {risk_summary['medium']}")
    print(f"Low Risk Transactions    : {risk_summary['low']}")
    print(f"Overall Risk Level       : {risk_summary['overall_risk']}")