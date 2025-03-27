import os
import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

if not os.path.exists('Stocks'):
    os.makedirs('Stocks')


fortune500_df = pd.read_csv('AllTickers.csv')
issuer_codes = fortune500_df['Ticker'].tolist()


end_date = datetime.today()
start_date_default = end_date - timedelta(days=365 * 10)


start_time = time.time()

# Loop through each issuer code
for issuer in issuer_codes:

    file_path = f'Stocks/{issuer}.csv'

    # Check if the file exists
    if os.path.exists(file_path):
        # Read existing data
        existing_data = pd.read_csv(file_path, parse_dates=['Date'])
        last_date = existing_data['Date'].max()
        print(f"Existing data found for {issuer}. Last date: {last_date}")
    else:
        # No existing data, fetch the last 10 years
        last_date = start_date_default
        existing_data = pd.DataFrame()
        print(f"No existing data found for {issuer}. Fetching data from {last_date} to {end_date}.")

    # Fetch missing data from last_date to end_date
    if last_date < end_date:
        print(f"Fetching missing data for {issuer} from {last_date} to {end_date}...")
        new_data = yf.download(issuer, start=last_date + timedelta(days=1), end=end_date)

        # After fetching and combining the data, save it without the redundant row
        if not new_data.empty:

            combined_data = pd.concat([existing_data, new_data.reset_index()], ignore_index=True)

            combined_data.to_csv(file_path, index=False, float_format='%.2f')
            print(f"Data for {issuer} saved to {file_path}")
        else:
            print(f"No new data available for {issuer}")

    else:
        print(f"No new data needed for {issuer}. Data is up to date.")


end_time = time.time()

elapsed_time = end_time - start_time
print(f"Total time taken to populate the folder: {elapsed_time:.2f} seconds")
