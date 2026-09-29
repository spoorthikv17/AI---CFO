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
def generate_financial_recommendations(
    summary,
    profit_margin,
    expense_ratio,
    largest_expense,
    risk_summary
):
    """Generate CFO-style financial recommendations."""

    recommendations = []

    if profit_margin < 20:
        recommendations.append(
            "Consider improving the profit margin by increasing revenue "
            "or reducing unnecessary expenses."
        )

    if expense_ratio > 70:
        recommendations.append(
            "Expenses are high compared to income. "
            "Review major spending categories."
        )

    if largest_expense:
        recommendations.append(
            f"Monitor {largest_expense['category']} expenses, "
            f"which currently total ₹{largest_expense['amount']:,.2f}."
        )

    if risk_summary["high"] > 0:
        recommendations.append(
            "Review high-risk transactions to identify unusual or "
            "potentially avoidable spending."
        )

    if risk_summary["medium"] > 0:
        recommendations.append(
            "Monitor medium-risk transactions and check whether "
            "they are recurring or necessary."
        )
    if summary["total_income"] > 0 and summary["profit"] > 0:
        recommendations.append(
            f"Current operations generated a profit of "
            f"₹{summary['profit']:,.2f}. "
            f"Continue tracking revenue and expenses to maintain this performance."
        )

    if largest_expense:
        if largest_expense["amount"] > 25000:
            recommendations.append(
                f"{largest_expense['category']} is a major expense category. "
                f"Review whether this cost can be optimized without affecting "
                f"business operations."
            )

    if not recommendations:
        recommendations.append(
            "Financial indicators are currently stable. "
            "Continue monitoring income, expenses, and cash flow."
        )

    return recommendations

def create_ai_financial_context(
    summary,
    profit_margin,
    expense_ratio,
    largest_expense,
    risk_summary,
    recommendations
):
    """Create structured financial context for the AI layer."""

    return {
        "total_income": summary["total_income"],
        "total_expenses": summary["total_expenses"],
        "profit": summary["profit"],
        "profit_margin": profit_margin,
        "expense_ratio": expense_ratio,
        "largest_expense_category": (
            largest_expense["category"]
            if largest_expense
            else None
        ),
        "largest_expense_amount": (
            largest_expense["amount"]
            if largest_expense
            else 0
        ),
        "high_risk_transactions": risk_summary["high"],
        "medium_risk_transactions": risk_summary["medium"],
        "low_risk_transactions": risk_summary["low"],
        "recommendations": recommendations
    }
def format_ai_financial_context(ai_context):
    """Convert financial context into readable AI input."""

    context = f"""
AI CFO Financial Context

Total Income: ₹{ai_context['total_income']:,.2f}
Total Expenses: ₹{ai_context['total_expenses']:,.2f}
Profit: ₹{ai_context['profit']:,.2f}
Profit Margin: {ai_context['profit_margin']:.2f}%
Expense Ratio: {ai_context['expense_ratio']:.2f}%

Largest Expense Category:
{ai_context['largest_expense_category']} - ₹{ai_context['largest_expense_amount']:,.2f}

Risk Summary:
High Risk Transactions: {ai_context['high_risk_transactions']}
Medium Risk Transactions: {ai_context['medium_risk_transactions']}
Low Risk Transactions: {ai_context['low_risk_transactions']}

Current Recommendations:
"""

    for recommendation in ai_context["recommendations"]:
        context += f"- {recommendation}\n"

    return context

def create_cfo_prompt(formatted_context, user_question):
    """Create a concise prompt for the AI CFO."""

    prompt = f"""
You are an AI CFO assistant.

Use the financial data below to answer the user's question.

Rules:
- Use only the provided financial data.
- Do not invent numbers.
- Explain your reasoning simply.
- Mention relevant numbers.
- Give practical suggestions when appropriate.
- If the data is insufficient, say so.

FINANCIAL DATA:
{formatted_context}

USER QUESTION:
{user_question}

Answer clearly and concisely.
"""

    return prompt