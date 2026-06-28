import csv
from pathlib import Path

import requests


url = "https://data-api.binance.vision/api/v3/klines"
params = {
    "symbol": "BTCUSDT",
    "interval": "1h",
    "limit": 1000,
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

records = response.json()
rows = []
for record in records:   
    row = {
        "symbol": "BTCUSDT",
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
    }
    rows.append(row)

output_path = Path("data/clean/records.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {output_path}")
