import csv

import requests
from bs4 import BeautifulSoup


def extract_sp500_tickers(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})

    if table is None:
        print("Could not find the table with S&P 500 constituents.")
        return None

    tickers = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if cells:
            ticker = cells[0].text.strip()
            tickers.append(ticker)

    return tickers

def save_to_csv(tickers, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Ticker'])  # Write header
        for ticker in tickers:
            writer.writerow([ticker])

if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tickers = extract_sp500_tickers(url)

    if tickers:
        save_to_csv(tickers, 'AllTickers.csv')
        print(f"Ticker symbols saved to 'AllTickers.csv'")
    else:
        print("Could not extract ticker symbols.")

