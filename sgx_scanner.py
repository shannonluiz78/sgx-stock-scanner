import json
import time
import pandas as pd
import yfinance as yf

# SGX Stock Tickers
SGX_TICKERS = [
    "D05.SI",  # DBS Group
    "O39.SI",  # OCBC
    "U11.SI",  # UOB
    "Z74.SI",  # Singtel
    "C6L.SI",  # Singapore Airlines
    "C38U.SI", # CapitaLand Integrated Commercial Trust
    "A17U.SI", # CapitaLand Ascendas REIT
    "N2IU.SI", # Mapletree Pan Asia Commercial Trust
    "ME8U.SI", # Mapletree Industrial Trust
    "F34.SI",  # Wilmar International
    "Y92.SI",  # Thai Beverage
    "U96.SI",  # Sembcorp Industries
    "S63.SI",  # ST Engineering
    "G13.SI",  # Genting Singapore
    "BN4.SI",  # Keppel Ltd
    "S68.SI",  # Singapore Exchange
    "H78.SI",  # Hongkong Land
    "C09.SI",  # City Developments
    "U14.SI",  # UOL Group
    "BS6.SI",  # Yangzijiang Shipbuilding
]

BATCH_SIZE = 5      # Small batch size to prevent IP blocking
DELAY_SECONDS = 3   # Delay between batch requests

def fetch_stock_data():
    results = []
    total_tickers = len(SGX_TICKERS)
    print(f"Starting scan for {total_tickers} stocks...")

    for i in range(0, total_tickers, BATCH_SIZE):
        batch = SGX_TICKERS[i:i + BATCH_SIZE]
        print(f"Processing batch {(i // BATCH_SIZE) + 1}/{(total_tickers + BATCH_SIZE - 1) // BATCH_SIZE}: {batch}")

        for ticker_symbol in batch:
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="5d")

                if hist.empty or len(hist) < 2:
                    print(f"  ⚠️ Skipping {ticker_symbol} (Insufficient history)")
                    continue

                latest_close = float(hist["Close"].iloc[-1])
                prev_close = float(hist["Close"].iloc[-2])
                price_change = latest_close - prev_close
                pct_change = (price_change / prev_close) * 100
                volume = int(hist["Volume"].iloc[-1])

                info = {}
                try:
                    info = ticker.info or {}
                except Exception:
                    pass

                stock_info = {
                    "symbol": ticker_symbol,
                    "name": info.get("shortName") or info.get("longName") or ticker_symbol,
                    "price": round(latest_close, 3),
                    "change": round(price_change, 3),
                    "change_pct": round(pct_change, 2),
                    "volume": volume,
                    "pe_ratio": round(info.get("trailingPE"), 2) if info.get("trailingPE") else "N/A",
                    "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else "N/A",
                }

                results.append(stock_info)
                print(f"  ✓ {ticker_symbol}: ${latest_close:.3f} ({pct_change:+.2f}%)")

            except Exception as e:
                print(f"  ❌ Error fetching {ticker_symbol}: {e}")

        time.sleep(DELAY_SECONDS)

    return results

def main():
    stock_data = fetch_stock_data()

    # Save as a raw JSON array [...] so website JavaScript can map over it immediately
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(stock_data, f, indent=2)

    print(f"\n🎉 Successfully saved {len(stock_data)} stocks to data.json!")

if __name__ == "__main__":
    main()
