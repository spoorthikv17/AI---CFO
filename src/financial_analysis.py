def calculate_financial_summary(transactions):
    """Calculate key financial metrics."""

    total_income = transactions.loc[
        transactions["type"] == "Income", "amount"
    ].sum()

    total_expenses = transactions.loc[
        transactions["type"] == "Expense", "amount"
    ].sum()

    profit = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "profit": profit,
    }
def calculate_monthly_summary(transactions):
    """Calculate monthly income, expenses, and profit."""

    monthly = (
        transactions
        .assign(month=transactions["date"].dt.to_period("M"))
        .groupby(["month", "type"])["amount"]
        .sum()
        .unstack(fill_value=0)
    )

    monthly["Profit"] = (
        monthly.get("Income", 0) -
        monthly.get("Expense", 0)
    )

    return monthly
def calculate_expense_by_category(transactions):
    """Calculate expenses and their percentage by category."""

    expenses = transactions[
        transactions["type"] == "Expense"
    ]

    category_summary = (
        expenses.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    total_expenses = category_summary.sum()

    category_percentage = (
        category_summary / total_expenses * 100
    )

    result = category_summary.to_frame(name="amount")
    result["percentage"] = category_percentage.round(2)

    return result