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

rows = []

start = time.perf_counter()
for symbol in symbols:
    params = {
        "symbol": symbol,
        "interval": "1h",
        "limit": 1000,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    records = response.json()
    
    
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

end = time.perf_counter()
print(f"Execution time: {end - start:.2f} seconds")

output_path = Path("data/clean/records.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {output_path}")
