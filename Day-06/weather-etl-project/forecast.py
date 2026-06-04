import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.linear_model import LinearRegression

# Load dataset
df = pd.read_csv("weather_data.csv")

# Features and labels
X = np.array(df.index).reshape(-1, 1)

y = df["temperature"]

# Train model
model = LinearRegression()

model.fit(X, y)

# Predict next 30 days
future_days = np.array(
    range(len(df), len(df) + 30)
).reshape(-1, 1)

forecast = model.predict(future_days)

# Plot
plt.figure(figsize=(12, 6))

plt.plot(
    df.index,
    y,
    label="Historical Temperature (Pune)"
)

plt.plot(
    range(len(df), len(df) + 30),
    forecast,
    label="Forecasted Temperature (Next 30 Days)"
)

plt.title("Pune Temperature Forecast for Next 30 Days")

plt.xlabel("Days")

plt.ylabel("Temperature (°C)")

plt.legend()

plt.grid(True)

plt.show()

print("\nForecast Completed Successfully!")