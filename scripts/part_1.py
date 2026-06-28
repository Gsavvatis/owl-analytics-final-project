import csv
from pathlib import Path

import requests
import time


url = "https://data-api.binance.vision/api/v3/klines"

symbols = ["BTCUSDT",
           "ETHUSDT",
           "BNBUSDT",
           "SOLUSDT",
           "XRPUSDT",
           "ADAUSDT",
           "DOGEUSDT",
           "AVAXUSDT",
           "LINKUSDT",
           "DOTUSDT"
        ]



def fetch_data(symbol):
    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 1000,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    records = response.json()
    
    rows = []
    for record in records:   
        row = {
            "symbol": symbol,
            "interval": "1h",
            "open_time": record[0],
            "open": record[1],
            "high": record[2],
            "low": record[3],
            "close": record[4],
            "volume": record[5],
            "close_time": record[6],
            "quote_volume": record[7],
            "trade_count": record[8],
            "taker_buy_base_volume": record[9],
            "taker_buy_quote_volume": record[10]
        }
        rows.append(row)

    return rows

def download_data_serial(symbols):
    start = time.perf_counter()
    rows = []
    for symbol in symbols:
        rows.extend(fetch_data(symbol))

   
    end = time.perf_counter()
    print(f"Execution time: {end - start:.2f} seconds")
    return rows, end - start

rows, Serial_time = download_data_serial(symbols)

output_path = Path("data/clean/records.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {output_path}")
print(f"Serial execution time: {Serial_time:.2f} seconds")
