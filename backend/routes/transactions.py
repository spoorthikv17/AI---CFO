from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from backend.database import get_db
from backend.models import Transaction
from backend.schemas import TransactionCreate, TransactionResponse


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get("/", response_model=list[TransactionResponse])
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.date.desc()).all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id)
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
):
    if transaction_data.type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Income or Expense",
        )

    if transaction_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Amount must be greater than zero",
        )

    transaction = Transaction(
        date=transaction_data.date,
        description=transaction_data.description,
        category=transaction_data.category,
        type=transaction_data.type,
        amount=transaction_data.amount,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@router.post("/from-receipt", response_model=TransactionResponse)
def create_transaction_from_receipt(
    receipt_data: dict,
    db: Session = Depends(get_db),
):
    """
    Save a user-confirmed Gemini receipt analysis
    as an Expense transaction.
    """

    required_fields = ["date", "category", "total"]

    for field in required_fields:
        if receipt_data.get(field) is None:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}",
            )

    try:
        amount = float(receipt_data["total"])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Receipt total must be a valid number.",
        )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Receipt total must be greater than zero.",
        )

    transaction_date = date.fromisoformat(receipt_data["date"])

    transaction = Transaction(
    date=transaction_date,
    description=receipt_data.get("vendor") or "Receipt Expense",
    category=receipt_data["category"],
    type="Expense",
    amount=amount,
)

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction