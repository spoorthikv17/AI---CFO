from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.transactions import router as transactions_router
from backend.routes.analytics import router as analytics_router
from backend.routes.receipts import router as receipts_router
app = FastAPI(
    title="MoneyFlow API",
    description="Backend API for the MoneyFlow financial application",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(receipts_router)

@app.get("/")
def root():
    return {
        "app": "MoneyFlow",
        "message": "MoneyFlow API is running",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MoneyFlow Backend",
    }