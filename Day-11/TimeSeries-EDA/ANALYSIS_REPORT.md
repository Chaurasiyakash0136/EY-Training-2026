# Time Series EDA Analysis Report

## Step 1: Data Profile

### Objective

Understand dataset structure and identify target signals.

### Approach

Reviewed dataset columns, data types and record count.

### Result

* Total Records: 7423
* Columns:

  * seq
  * timestamp_ms
  * red
  * ir
  * red_corrected
  * ir_corrected

### Interpretation

The dataset contains PPG sensor readings collected over approximately 148 seconds.

---

## Step 2: Timestamp Continuity Check

### Objective

Verify whether timestamps are continuous.

### Approach

Calculated timestamp differences between consecutive observations.

### Result

* Expected Interval: 20 ms
* Potential Gaps: 22

### Interpretation

Minor timestamp irregularities were observed, but overall continuity is preserved.

---

## Step 3: Missing Value Analysis

### Objective

Determine whether missing-value treatment is required.

### Approach

Calculated missing-value count and percentage for every column.

### Result

* Missing Values: 0
* Missing Percentage: 0%

### Interpretation

No imputation strategy was required.

---

## Step 4: Feature Engineering

### Generated Features

* lag_1
* lag_5
* lag_10
* rolling_mean_5
* rolling_std_5
* rolling_mean_20
* rolling_std_20
* signal_diff

### Interpretation

These features capture temporal dependencies and local signal behavior.

---

## Step 5: Time Series Analysis

### Trend

#### Objective

Identify long-term movement in the signal.

#### Result

No strong increasing or decreasing trend observed.

#### Interpretation

The signal remains relatively stable throughout the recording period.

---

### Seasonality

#### Objective

Detect repeating patterns.

#### Result

Periodic waveform patterns observed.

#### Interpretation

Behavior is consistent with expected PPG signal characteristics.

---

### Outlier Detection

#### Objective

Detect abnormal observations.

#### Method

Z-score based detection.

#### Result

* Outliers Detected: 191
* Outlier Percentage: 2.57%

#### Interpretation

Outliers may correspond to sensor noise or motion artifacts.

---

## Step 6: Stationarity Check

### Objective

Determine whether the signal is stationary.

### Method

Augmented Dickey-Fuller (ADF) Test

### Hypotheses

H0: Signal is non-stationary.

H1: Signal is stationary.

### Result

* ADF Statistic: -3.1629
* P-Value: 0.0222

### Interpretation

Since p-value < 0.05, H0 is rejected.

The signal is stationary.

---

## Step 7: ACF and PACF

### Objective

Analyze temporal dependencies.

### Result

ACF and PACF plots generated successfully.

### Interpretation

The signal demonstrates temporal correlation and lag relationships useful for future forecasting tasks.

---

## Bonus Task

### Objective

Compare RED and IR signals on the same scale.

### Method

StandardScaler normalization.

### Result

Generated:

* normalized_red_ir_superimposed.png

### Interpretation

Normalization allows comparison of waveform shape and peak alignment without being affected by differing signal magnitudes.

---

## Conclusion

A complete automated Time Series EDA pipeline was implemented for the PPG dataset. The dataset contains no missing values, maintains overall timestamp continuity, exhibits periodic behavior, contains a small percentage of outliers, and was found to be stationary according to the ADF test. All required analytical artifacts and visualizations were generated successfully.
