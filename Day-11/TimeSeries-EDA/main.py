import os
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import zscore
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

warnings.filterwarnings("ignore")

# ==========================================================
# CONFIG
# ==========================================================

DATA_PATH = "data/sakshi_ppg_20260611T074737_len148s.csv"
OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================================
# LOAD DATA
# ==========================================================

print("\n" + "="*60)
print("LOADING DATA")
print("="*60)

df = pd.read_csv(DATA_PATH)

print("\nDataset Shape:", df.shape)
print("\nColumns:")
print(df.columns.tolist())

# ==========================================================
# BASIC INFO
# ==========================================================

print("\n" + "="*60)
print("DATASET OVERVIEW")
print("="*60)

print(df.info())

# ==========================================================
# MISSING VALUES
# ==========================================================

print("\n" + "="*60)
print("MISSING VALUE ANALYSIS")
print("="*60)

missing = df.isnull().sum()

missing_df = pd.DataFrame({
    "Missing Count": missing,
    "Missing %": (missing / len(df)) * 100
})

print(missing_df)

# ==========================================================
# TIMESTAMP ANALYSIS
# ==========================================================

print("\n" + "="*60)
print("TIMESTAMP CONTINUITY CHECK")
print("="*60)

df["timestamp_diff"] = df["timestamp_ms"].diff()

print(df["timestamp_diff"].describe())

expected_interval = df["timestamp_diff"].median()

gaps = df[df["timestamp_diff"] > expected_interval * 2]

print(f"\nExpected Interval : {expected_interval:.2f} ms")
print(f"Potential Gaps    : {len(gaps)}")

# ==========================================================
# STATISTICAL SUMMARY
# ==========================================================

print("\n" + "="*60)
print("STATISTICAL SUMMARY")
print("="*60)

signals = [
    "red",
    "ir",
    "red_corrected",
    "ir_corrected"
]

for col in signals:

    print(f"\n------ {col} ------")

    print("Mean   :", df[col].mean())
    print("Median :", df[col].median())
    print("Mode   :", df[col].mode()[0])
    print("Std    :", df[col].std())
    print("Min    :", df[col].min())
    print("Max    :", df[col].max())

# ==========================================================
# FEATURE ENGINEERING
# ==========================================================

print("\n" + "="*60)
print("FEATURE ENGINEERING")
print("="*60)

target = "ir_corrected"

df["lag_1"] = df[target].shift(1)
df["lag_5"] = df[target].shift(5)
df["lag_10"] = df[target].shift(10)

df["rolling_mean_5"] = df[target].rolling(5).mean()
df["rolling_std_5"] = df[target].rolling(5).std()

df["rolling_mean_20"] = df[target].rolling(20).mean()
df["rolling_std_20"] = df[target].rolling(20).std()

df["signal_diff"] = df[target].diff()

print("Feature Engineering Completed")

# ==========================================================
# TIME SERIES PLOT
# ==========================================================

print("\nGenerating Time Series Plot...")

plt.figure(figsize=(14,5))
plt.plot(df["timestamp_ms"], df["ir_corrected"])
plt.title("IR Corrected Signal")
plt.xlabel("Timestamp (ms)")
plt.ylabel("Signal")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/time_series_plot.png")
plt.close()

# ==========================================================
# TREND + SEASONALITY
# ==========================================================

print("\nGenerating Decomposition Plot...")

series = df["ir_corrected"]

decomposition = seasonal_decompose(
    series,
    period=50,
    model="additive"
)

fig = decomposition.plot()
fig.set_size_inches(12,8)
plt.savefig(f"{OUTPUT_DIR}/decomposition_plot.png")
plt.close()

# ==========================================================
# OUTLIER DETECTION
# ==========================================================

print("\n" + "="*60)
print("OUTLIER ANALYSIS")
print("="*60)

z_scores = np.abs(zscore(df[target]))

outliers = df[z_scores > 3]

print("Outlier Count :", len(outliers))

plt.figure(figsize=(14,5))
plt.plot(df[target], label="Signal")

plt.scatter(
    outliers.index,
    outliers[target],
    s=20
)

plt.title("Outlier Detection")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/outlier_plot.png")
plt.close()

# ==========================================================
# BOXPLOT
# ==========================================================

plt.figure(figsize=(8,5))
sns.boxplot(y=df[target])

plt.title("Signal Boxplot")
plt.tight_layout()

plt.savefig(f"{OUTPUT_DIR}/boxplot.png")
plt.close()

# ==========================================================
# STATIONARITY TEST
# ==========================================================

print("\n" + "="*60)
print("ADF STATIONARITY TEST")
print("="*60)

adf_result = adfuller(df[target])

print("ADF Statistic :", adf_result[0])
print("P-Value       :", adf_result[1])

if adf_result[1] < 0.05:
    print("Result        : Stationary")
else:
    print("Result        : Non-Stationary")

# ==========================================================
# ACF
# ==========================================================

print("\nGenerating ACF Plot...")

fig, ax = plt.subplots(figsize=(12,5))
plot_acf(df[target].dropna(), lags=50, ax=ax)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/acf_plot.png")
plt.close()

# ==========================================================
# PACF
# ==========================================================

print("\nGenerating PACF Plot...")

fig, ax = plt.subplots(figsize=(12,5))
plot_pacf(df[target].dropna(), lags=50, ax=ax)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/pacf_plot.png")
plt.close()

# ==========================================================
# FINAL SUMMARY
# ==========================================================

print("\n" + "="*60)
print("FINAL CONCLUSION")
print("="*60)

print("""
1. Dataset loaded successfully.

2. Missing values checked.

3. Timestamp continuity analyzed.

4. Statistical summary generated.

5. Feature engineering completed.

6. Trend and seasonality analyzed.

7. Outliers identified.

8. Stationarity tested using ADF.

9. ACF and PACF generated.

10. All plots saved inside outputs folder.
""")