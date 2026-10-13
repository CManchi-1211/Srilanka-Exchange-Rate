import datetime
import gspread
import numpy as np
import pandas as pd
import yfinance as yf
from google.oauth2.service_account import Credentials

# 1. Define Google Sheets and Drive API scopes
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# 2. Setup Google Authentication using your GCP Service Account Key from GitHub Secrets
# Note: In GitHub Actions, ensure you add GCP_SA_KEY to your repository secrets.
import json
import os

gcp_key = os.environ.get("GCP_SA_KEY")
service_account_info = json.loads(gcp_key)
creds = Credentials.from_service_account_info(
    service_account_info, scopes=scopes
)
gc = gspread.authorize(creds)

# 3. Fetch past daily USD/LKR exchange rate data from Yahoo Finance (from 2019 to today)
print("Fetching historical exchange rate data...")
ticker = "USDLKR=X"
start_date = "2019-01-01"
end_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Download data
data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

# Clean and format the dataframe
df_historical = data[["Close"]].reset_index()
# Convert Date to string format (YYYY-MM-DD)
df_historical["Date"] = pd.to_datetime(df_historical["Date"]).dt.strftime(
    "%Y-%m-%d"
)
df_historical.columns = ["Date", "USD_LKR_Rate"]
# Drop any missing rows
df_historical = df_historical.dropna().reset_index(drop=True)

print(f"Successfully fetched {len(df_historical)} rows of historical data.")

# 4. Open or Create the Google Sheet with a meaningful name
spreadsheet_name = "Sri_Lanka_Exchange_Rate_Predictor"
try:
  sh = gc.open(spreadsheet_name)
  print(f"Opened existing Google Sheet: {spreadsheet_name}")
except gspread.exceptions.SpreadsheetNotFound:
  sh = gc.create(spreadsheet_name)
  print(f"Created new Google Sheet: {spreadsheet_name}")

# 5. Setup the worksheet for historical data
try:
  hist_worksheet = sh.worksheet("Historical_Data")
except gspread.exceptions.WorksheetNotFound:
  hist_worksheet = sh.add_worksheet(
      title="Historical_Data", rows="3000", cols="5"
  )

# 6. Clear old data and update worksheet with the new historical dataset
hist_worksheet.clear()
header = df_historical.columns.values.tolist()
rows = df_historical.values.tolist()
hist_worksheet.update([header] + rows)

print(
    "✅ Historical data successfully uploaded to the 'Historical_Data' tab!"
)
