import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# ======================================
# ENTER YOUR OPENWEATHER API KEY
# ======================================
API_KEY = "a3198f6bcaaa073e9d50491ccac68e27"

CITY = "Pune"

records = []

print(f"\nStarting Weather ETL Extraction for {CITY}...\n")

for i in range(180):

    current_date = datetime.now() - timedelta(days=i)

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:

            data = response.json()

            records.append({
                "city": CITY,
                "date": current_date.strftime("%Y-%m-%d"),
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather_condition": data["weather"][0]["main"]
            })

            print(f"Fetched record {i+1}/180")

        else:
            print(f"API Error: {response.status_code}")

    except Exception as e:
        print(f"Error occurred: {e}")

    time.sleep(1)

df = pd.DataFrame(records)

df.to_csv("weather_data.csv", index=False)

print("\n=====================================")
print("Weather Data Extraction Successful!")
print("=====================================\n")

print(df.head())