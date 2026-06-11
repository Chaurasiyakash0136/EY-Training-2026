This project implements an automated time-series EDA pipeline for PPG sensor data and generates all required analytical artifacts including trend, seasonality, outlier detection, stationarity testing, and ACF/PACF analysis.

# Time Series EDA on PPG Sensor Data

## Project Overview

This project performs Exploratory Data Analysis (EDA) on Photoplethysmography (PPG) sensor data collected over approximately 148 seconds.

The objective is to analyze the time series data and identify:

* Timestamp continuity
* Missing values
* Statistical properties
* Trend
* Seasonality
* Outliers
* Stationarity
* Temporal correlations

---

## Dataset Information

**Dataset Name:** sakshi_ppg_20260611T074737_len148s.csv

**Total Records:** 7423

**Columns:**

* seq
* timestamp_ms
* red
* ir
* red_corrected
* ir_corrected

---

## Analysis Performed

### 1. Timestamp Continuity Check

* Sampling interval analyzed using timestamp differences.
* Expected sampling interval observed around 20 ms.
* Potential timestamp gaps identified and reported.

### 2. Missing Value Analysis

* Checked all columns for missing values.
* Missing percentage calculated.
* No imputation required as no missing values were found.

### 3. Statistical Summary

Calculated for all signal columns:

* Mean
* Median
* Mode
* Standard Deviation
* Minimum
* Maximum

### 4. Feature Engineering

Generated features:

* lag_1
* lag_5
* lag_10
* rolling_mean_5
* rolling_std_5
* rolling_mean_20
* rolling_std_20
* signal_diff

### 5. Time Series Visualization

Generated signal plots to visualize temporal behavior.

### 6. Trend and Seasonality Analysis

Seasonal decomposition was performed to extract:

* Trend component
* Seasonal component
* Residual component

### 7. Outlier Detection

Outliers were identified using Z-score analysis.

### 8. Stationarity Test

Augmented Dickey-Fuller (ADF) test was used to determine stationarity.

### 9. ACF and PACF Analysis

Generated:

* Autocorrelation Function (ACF)
* Partial Autocorrelation Function (PACF)

These plots help understand temporal dependencies in the signal.

---

## Results Summary

| Metric                     | Value      |
| -------------------------- | ---------- |
| Records                    | 7423       |
| Missing Values             | 0          |
| Expected Sampling Interval | 20 ms      |
| Potential Timestamp Gaps   | 22         |
| Outliers Detected          | 191        |
| Outlier Percentage         | 2.57%      |
| ADF p-value                | 0.0222     |
| Stationarity               | Stationary |

---

## Output Files

The following files are generated automatically:

* time_series_plot.png
* decomposition_plot.png
* outlier_plot.png
* boxplot.png
* acf_plot.png
* pacf_plot.png

All files are saved inside the outputs directory.

---

## Technologies Used

* Python
* Pandas
* NumPy
* Matplotlib
* Seaborn
* SciPy
* Statsmodels

---

## How to Run

Install dependencies:

pip install -r requirements.txt

Run the project:

python main.py

---

## Conclusion

The dataset was successfully analyzed using a complete time series EDA pipeline. The signal showed periodic behavior, contained a small percentage of outliers, and was determined to be stationary according to the ADF test. Generated visualizations and statistical reports provide insights into the temporal characteristics of the PPG sensor data.