import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
import time
from datetime import datetime, timezone

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

NUM_SYMBOLS = len(symbols)
log_lock = threading.Lock()
rate_limiter = threading.Semaphore(100)

Path("results").mkdir(exist_ok=True)
Path("data/clean").mkdir(parents=True, exist_ok=True)

def convert_ms_to_timestamp(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')


def write_log(message):
    timestamp = datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with log_lock:
        with open("results/api_download.log", "a", encoding="utf-8") as file:
            file.write(f"{timestamp} | {message}\n")

def save_benchmark(serial_time, multithreaded_time):
    with open("results/benchmark.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), serial_time, multithreaded_time])

def fetch_data(symbol):
    with rate_limiter:
    
        write_log(f"START request for symbol = {symbol} interval = 1h")
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
                "open_time": convert_ms_to_timestamp(record[0]),
                "open": record[1],
                "high": record[2],
                "low": record[3],
                "close": record[4],
                "volume": record[5],
                "close_time": convert_ms_to_timestamp(record[6])   ,
                "quote_volume": record[7],
                "trade_count": record[8],
                "taker_buy_base_volume": record[9],
                "taker_buy_quote_volume": record[10]
            }
            rows.append(row)
        write_log(f"END request for symbol = {symbol} records = {len(rows)}")
        return rows

def download_data_serial(symbols):
    start = time.perf_counter()
    rows = []
    for symbol in symbols:
        rows.extend(fetch_data(symbol))

   
    end = time.perf_counter()
   # print(f"Execution time: {end - start:.2f} seconds")
    return rows, end - start

serial_rows, serial_time = download_data_serial(symbols)



def download_data_multithreaded(symbols): 
    
    start = time.perf_counter()
    rows = []
    with ThreadPoolExecutor(max_workers=NUM_SYMBOLS) as executor:
        results = executor.map(fetch_data, symbols)
        for result in results:
            rows.extend(result)

    end = time.perf_counter()
   # print(f"Execution time: {end - start:.2f} seconds")
    return rows, end - start

mt_rows, multithreaded_time = download_data_multithreaded(symbols)



output_path = Path("data/clean/records.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=mt_rows[0].keys())
    writer.writeheader()
    writer.writerows(mt_rows)







write_log(f"Serial execution time: {serial_time:.2f} seconds")
write_log(f"Serial records: {len(serial_rows)}")
write_log(f"Multithreaded records: {len(mt_rows)}")
write_log(f"Multithreaded execution time: {multithreaded_time:.2f} seconds")
write_log(f"Saved {output_path}")

print(f"Serial execution time: {serial_time:.2f} seconds")
print(f"Serial records: {len(serial_rows)}")
print(f"Multithreaded records: {len(mt_rows)}")
print(f"Multithreaded execution time: {multithreaded_time:.2f} seconds")
print(f"Saved {output_path}")