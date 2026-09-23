import pandas as pd

# Load financial transaction data
file_path = "data/transactions.csv"
transactions = pd.read_csv(file_path)

# Calculate total income
total_income = transactions.loc[
    transactions["type"] == "Income", "amount"
].sum()

# Calculate total expenses
total_expenses = transactions.loc[
    transactions["type"] == "Expense", "amount"
].sum()

# Calculate profit
profit = total_income - total_expenses

# Display results
print("\n===== AI CFO Financial Summary =====")
print(f"Total Income   : ₹{total_income:,.2f}")
print(f"Total Expenses : ₹{total_expenses:,.2f}")
print(f"Profit         : ₹{profit:,.2f}")