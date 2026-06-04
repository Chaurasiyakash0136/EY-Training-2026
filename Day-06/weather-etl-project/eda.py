import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("weather_data.csv")

print("\nFirst 5 Rows:")
print(df.head())

print("\nDataset Info:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())

# Handle missing values
df = df.ffill()

# Normalize temperature
df["normalized_temperature"] = (
    (df["temperature"] - df["temperature"].min()) /
    (df["temperature"].max() - df["temperature"].min())
)

print("\nNormalized Temperature Added")

# Basic statistics
print("\nStatistical Summary:")
print(df.describe())

# Plot temperature trend
plt.figure(figsize=(12, 6))

plt.plot(df.index, df["temperature"])

plt.title("Pune Weather Temperature Trend (Last 6 Months)")

plt.xlabel("Days")

plt.ylabel("Temperature (°C)")

plt.grid(True)

plt.show()

print("\nEDA Completed Successfully!")