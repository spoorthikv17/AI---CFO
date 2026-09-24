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
def calculate_profit_margin(total_income, profit):
    """Calculate profit margin as a percentage."""

    if total_income == 0:
        return 0

    return (profit / total_income) * 100

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
if __name__ == "__main__":
    total_income = 223000
    profit = 148000

    profit_margin = calculate_profit_margin(
        total_income,
        profit
    )

    print(f"Profit Margin: {profit_margin:.2f}%")

def calculate_cash_flow(transactions):
    """Calculate cash inflow, outflow, and net cash flow."""

    cash_flow = (
        transactions
        .assign(month=transactions["date"].dt.to_period("M"))
        .groupby(["month", "type"])["amount"]
        .sum()
        .unstack(fill_value=0)
    )

    cash_flow["Net Cash Flow"] = (
        cash_flow.get("Income", 0)
        - cash_flow.get("Expense", 0)
    )

    return cash_flow
def identify_largest_expense(expense_by_category):
    """Identify the category with the highest expense."""

    if expense_by_category.empty:
        return None

    largest_category = expense_by_category["amount"].idxmax()
    largest_amount = expense_by_category.loc[
        largest_category, "amount"
    ]

    return {
        "category": largest_category,
        "amount": largest_amount
    }
def calculate_expense_ratio(total_income, total_expenses):
    """Calculate expenses as a percentage of income."""

    if total_income == 0:
        return 0

    return (total_expenses / total_income) * 100
def calculate_financial_trend(transactions):
    """Calculate monthly income, expenses, profit, and profit margin."""

    monthly = (
        transactions
        .assign(month=transactions["date"].dt.to_period("M"))
        .groupby(["month", "type"])["amount"]
        .sum()
        .unstack(fill_value=0)
    )

    monthly["Profit"] = (
        monthly.get("Income", 0)
        - monthly.get("Expense", 0)
    )

    monthly["Profit Margin"] = (
        monthly["Profit"]
        / monthly.get("Income", 0)
        * 100
    )

    monthly["Profit Margin"] = monthly["Profit Margin"].fillna(0).round(2)

    return monthly
def generate_financial_insights(
    summary,
    profit_margin,
    expense_ratio,
    largest_expense
):
    """Generate basic CFO-style financial insights."""

    insights = []

    insights.append(
        f"Total income is ₹{summary['total_income']:,.2f}."
    )

    insights.append(
        f"Total expenses are ₹{summary['total_expenses']:,.2f}."
    )

    insights.append(
        f"Current profit is ₹{summary['profit']:,.2f}."
    )

    insights.append(
        f"Profit margin is {profit_margin:.2f}%."
    )

    insights.append(
        f"Expenses represent {expense_ratio:.2f}% of total income."
    )

    insights.append(
        f"Largest expense category is "
        f"{largest_expense['category']} "
        f"at ₹{largest_expense['amount']:,.2f}."
    )

    return insights
def generate_financial_alerts(
    profit_margin,
    expense_ratio,
    largest_expense
):
    """Generate basic financial alerts."""

    alerts = []

    if profit_margin < 10:
        alerts.append(
            "Profit margin is low. Review expenses and pricing."
        )

    if expense_ratio > 80:
        alerts.append(
            "Expenses are high compared to income. "
            "Review major spending categories."
        )

    if largest_expense["amount"] > 0:
        alerts.append(
            f"{ largest_expense['category']} expenses, "
            f" currently at ₹{largest_expense['amount']:,.2f}."
        )

    if not alerts:
        alerts.append(
            "No immediate financial alerts detected."
        )

    return alerts
def detect_large_expenses(transactions):
    """Detect unusually large expense transactions."""

    expenses = transactions[
        transactions["type"] == "Expense"
    ].copy()

    if expenses.empty:
        return expenses

    threshold = expenses["amount"].mean() + (
        2 * expenses["amount"].std()
    )

    large_expenses = expenses[
        expenses["amount"] > threshold
    ]

    return large_expenses
def calculate_transaction_risk(transactions):
    """Assign a risk level to expense transactions."""

    expenses = transactions[
        transactions["type"] == "Expense"
    ].copy()

    if expenses.empty:
        return expenses

    mean_expense = expenses["amount"].mean()
    std_expense = expenses["amount"].std()

    medium_threshold = mean_expense + std_expense
    high_threshold = mean_expense + (2 * std_expense)

    def assign_risk(amount):
        if amount > high_threshold:
            return "High"
        elif amount > medium_threshold:
            return "Medium"
        else:
            return "Low"

    expenses["risk_level"] = expenses["amount"].apply(
        assign_risk
    )

    return expenses
def summarize_financial_risk(risk_analysis):
    """Summarize transaction risk levels."""

    if risk_analysis.empty:
        return {
            "high": 0,
            "medium": 0,
            "low": 0,
            "overall_risk": "Low"
        }

    risk_counts = risk_analysis["risk_level"].value_counts()

    high = risk_counts.get("High", 0)
    medium = risk_counts.get("Medium", 0)
    low = risk_counts.get("Low", 0)

    if high >= 2:
        overall_risk = "High"
    elif high == 1 or medium >= 2:
        overall_risk = "Medium"
    else:
        overall_risk = "Low"

    return {
        "high": high,
        "medium": medium,
        "low": low,
        "overall_risk": overall_risk
    }