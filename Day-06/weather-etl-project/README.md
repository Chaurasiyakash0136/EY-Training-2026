# Weather ETL Pipeline Project

## Objective

Build an ETL pipeline using OpenWeather API and perform weather forecasting using Python and Machine Learning.

---

## Steps Performed

1. Extracted weather data using OpenWeather API
2. Stored extracted data into CSV format
3. Performed Exploratory Data Analysis (EDA)
4. Handled missing values and applied normalization
5. Built forecasting model using Machine Learning
6. Predicted future temperature trends for the next 30 days

---

## Technologies Used

* Python
* Pandas
* Requests
* Matplotlib
* Scikit-learn
* NumPy
* OpenWeather API

---

## ETL Workflow

OpenWeather API → Data Extraction → CSV Storage → EDA & Cleaning → Forecasting Model → Visualization

---

## Machine Learning Model Used

The forecasting model was implemented using the **Linear Regression** algorithm from Scikit-learn.

### Why Linear Regression?

* Simple and efficient for time-series trend prediction
* Suitable for beginner-level forecasting projects
* Helps identify future temperature trends based on historical weather data

### Library Used

```python
from sklearn.linear_model import LinearRegression
```

---

## Cron Job Automation

Example Cron Syntax:

```bash
0 9 * * * python extract.py
```

This automatically runs the ETL extraction pipeline daily at 9 AM.

---

## Azure Usage

Azure services such as Azure Blob Storage, Azure Data Factory, and Azure Machine Learning can be integrated for cloud deployment and orchestration.

---

## Output Files

* weather_data.csv
* Temperature Trend Graph
* Forecast Prediction Graph

---

## Conclusion

This project demonstrates a complete Weather ETL Pipeline including API-based data extraction, preprocessing, analysis, visualization, and machine learning-based forecasting.
