import joblib
import os
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load dataset
df = pd.read_csv("../data/raw/fleet_history.csv")

# Features
X = df[
    [
        "distance_km",
        "load_weight_kg",
        "fuel_efficiency_kmpl",
        "average_speed_kmh"
    ]
]

# Target
y = df["fuel_used_liters"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Create Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)
os.makedirs("backend/app/ml/models", exist_ok=True)

joblib.dump(
    model,
    "backend/app/ml/models/fuel_model.pkl"
)

print("Model saved successfully!")

# Predict
y_pred = model.predict(X_test)

# Evaluation
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5
r2 = r2_score(y_test, y_pred)

print("Random Forest Fuel Consumption Model")
print("------------------------------------")
print(f"MAE  : {mae:.2f} liters")
print(f"RMSE : {rmse:.2f} liters")
print(f"R²   : {r2:.4f}")