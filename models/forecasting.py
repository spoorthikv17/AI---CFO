import pandas as pd

from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def prepare_forecasting_data(file_path):
    """Prepare historical financial data for forecasting."""

    data = pd.read_csv(file_path)

    data["month"] = pd.to_datetime(data["month"])

    data["year"] = data["month"].dt.year
    data["month_number"] = data["month"].dt.month

    data["profit"] = data["income"] - data["expenses"]

    # Previous month's values
    data["income_lag_1"] = data["income"].shift(1)
    data["expenses_lag_1"] = data["expenses"].shift(1)
    data["profit_lag_1"] = data["profit"].shift(1)

    # Remove first row because lag values are unavailable
    data = data.dropna().reset_index(drop=True)

    return data


def train_forecast_model(data, target):
    """Train an XGBoost model for income or expense forecasting."""

    features = [
        "year",
        "month_number",
        "income_lag_1",
        "expenses_lag_1",
        "profit_lag_1"
    ]

    X = data[features]
    y = data[target]

    model = XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        objective="reg:squarederror",
        random_state=42
    )

    model.fit(X, y)

    return model


def predict_next_month(model, data):
    """Predict the next month's financial value."""

    latest = data.iloc[-1]

    next_month = latest["month"] + pd.DateOffset(months=1)

    features = pd.DataFrame([{
        "year": next_month.year,
        "month_number": next_month.month,
        "income_lag_1": latest["income"],
        "expenses_lag_1": latest["expenses"],
        "profit_lag_1": latest["profit"]
    }])

    prediction = model.predict(features)[0]

    return prediction


def evaluate_model_with_time_split(data, target):
    """Evaluate the model using chronological train/test data."""

    features = [
        "year",
        "month_number",
        "income_lag_1",
        "expenses_lag_1",
        "profit_lag_1"
    ]

    split_index = int(len(data) * 0.7)

    train_data = data.iloc[:split_index]
    test_data = data.iloc[split_index:]

    X_train = train_data[features]
    y_train = train_data[target]

    X_test = test_data[features]
    y_test = test_data[target]

    model = XGBRegressor(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        objective="reg:squarederror",
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    return model, predictions, mae, rmse, r2


if __name__ == "__main__":

    file_path = "data/historical_monthly_financials.csv"

    forecasting_data = prepare_forecasting_data(file_path)

    print("\n===== Forecasting Dataset =====")
    print(forecasting_data)

    print("\n===== Dataset Shape =====")
    print(forecasting_data.shape)

    # --------------------------------------------------
    # INCOME FORECASTING
    # --------------------------------------------------

    income_test_model, income_predictions, income_mae, income_rmse, income_r2 = (
        evaluate_model_with_time_split(
            forecasting_data,
            "income"
        )
    )

    print("\n===== Income Model Evaluation =====")
    print(f"MAE  : ₹{income_mae:,.2f}")
    print(f"RMSE : ₹{income_rmse:,.2f}")
    print(f"R²   : {income_r2:.4f}")

    income_model = train_forecast_model(
        forecasting_data,
        "income"
    )

    predicted_income = predict_next_month(
        income_model,
        forecasting_data
    )

    print("\n===== Income Forecast =====")
    print(
        f"Predicted Income for January 2026: "
        f"₹{predicted_income:,.2f}"
    )

    # --------------------------------------------------
    # EXPENSE FORECASTING
    # --------------------------------------------------

    expense_test_model, expense_predictions, expense_mae, expense_rmse, expense_r2 = (
        evaluate_model_with_time_split(
            forecasting_data,
            "expenses"
        )
    )

    print("\n===== Expense Model Evaluation =====")
    print(f"MAE  : ₹{expense_mae:,.2f}")
    print(f"RMSE : ₹{expense_rmse:,.2f}")
    print(f"R²   : {expense_r2:.4f}")

    expense_model = train_forecast_model(
        forecasting_data,
        "expenses"
    )

    predicted_expenses = predict_next_month(
        expense_model,
        forecasting_data
    )

    print("\n===== Expense Forecast =====")
    print(
        f"Predicted Expenses for January 2026: "
        f"₹{predicted_expenses:,.2f}"
    )

    # --------------------------------------------------
    # PREDICTED PROFIT
    # --------------------------------------------------

    predicted_profit = predicted_income - predicted_expenses

    print("\n===== Predicted Financial Summary =====")
    print(f"Predicted Income   : ₹{predicted_income:,.2f}")
    print(f"Predicted Expenses : ₹{predicted_expenses:,.2f}")
    print(f"Predicted Profit   : ₹{predicted_profit:,.2f}")