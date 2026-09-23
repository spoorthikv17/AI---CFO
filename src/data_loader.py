import pandas as pd
from financial_analysis import (
    calculate_financial_summary,
    calculate_monthly_summary
)

# Load financial transaction data
file_path = "data/transactions.csv"
transactions = pd.read_csv(file_path)
transactions["date"] = pd.to_datetime(transactions["date"])

# Validate transaction types
valid_types = ["Income", "Expense"]

if not transactions["type"].isin(valid_types).all():
    raise ValueError("Invalid transaction type found.")

# Validate transaction amounts
if (transactions["amount"] < 0).any():
    raise ValueError("Negative transaction amount found.")

# Validate required fields
required_columns = ["date", "description", "category", "type", "amount"]

if transactions[required_columns].isnull().any().any():
    raise ValueError("Missing values found in required fields.")

print("\nData validation passed successfully.")

# Calculate financial summary
summary = calculate_financial_summary(transactions)

total_income = summary["total_income"]
total_expenses = summary["total_expenses"]
profit = summary["profit"]

# Display results
print("\n===== AI CFO Financial Summary =====")
print(f"Total Income   : ₹{total_income:,.2f}")
print(f"Total Expenses : ₹{total_expenses:,.2f}")
print(f"Profit         : ₹{profit:,.2f}")

print("\n===== Data Information =====")
print(transactions.info())

print("\n===== Missing Values =====")
print(transactions.isnull().sum())
# Calculate monthly financial summary
monthly_summary = calculate_monthly_summary(transactions)

print("\n===== Monthly Financial Summary =====")
print(monthly_summary)