from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models import Transaction

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def financial_summary(db: Session = Depends(get_db)):

    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.type == "Income")
        .scalar()
    )

    expenses = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.type == "Expense")
        .scalar()
    )

    profit = income - expenses

    profit_margin = (
        (profit / income) * 100
        if income > 0
        else 0
    )

    expense_ratio = (
        (expenses / income) * 100
        if income > 0
        else 0
    )

    return {
        "total_income": round(income, 2),
        "total_expenses": round(expenses, 2),
        "profit": round(profit, 2),
        "profit_margin": round(profit_margin, 2),
        "expense_ratio": round(expense_ratio, 2),
    }


@router.get("/expenses-by-category")
def expenses_by_category(db: Session = Depends(get_db)):

    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("amount"),
        )
        .filter(Transaction.type == "Expense")
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    return [
        {
            "category": category,
            "amount": round(amount, 2),
        }
        for category, amount in results
    ]


@router.get("/monthly")
def monthly_financials(db: Session = Depends(get_db)):

    transactions = (
        db.query(Transaction)
        .order_by(Transaction.date)
        .all()
    )

    monthly = {}

    for transaction in transactions:

        month = transaction.date.strftime("%Y-%m")

        if month not in monthly:
            monthly[month] = {
                "income": 0,
                "expenses": 0,
            }

        if transaction.type == "Income":
            monthly[month]["income"] += transaction.amount

        elif transaction.type == "Expense":
            monthly[month]["expenses"] += transaction.amount

    response = []

    for month, values in monthly.items():

        income = values["income"]
        expenses = values["expenses"]

        response.append(
            {
                "month": month,
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "profit": round(income - expenses, 2),
            }
        )

    return response