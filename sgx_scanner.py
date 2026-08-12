import os
import datetime
import pandas as pd
import yfinance as yf

# Complete list of Core 8 SGX Stocks
CORE_8_STOCKS = [
    {"ticker": "D05.SI", "name": "DBS Group Holdings"},
    {"ticker": "O39.SI", "name": "OCBC Bank"},
    {"ticker": "U11.SI", "name": "UOB"},
    {"ticker": "Z74.SI", "name": "Singtel"},
    {"ticker": "S68.SI", "name": "Singapore Exchange (SGX)"},
    {"ticker": "C38U.SI", "name": "CapitaLand Integrated Commercial Trust"},
    {"ticker": "A17U.SI", "name": "CapitaLand Ascendas REIT"},
    {"ticker": "C6L.SI", "name": "Singapore Airlines"}
]

def fetch_stock_data(item):
    ticker_symbol = item["ticker"]
    company_name = item["name"]
    price_display = "Data Pending"
    status = "Active"

    try:
        stock = yf.Ticker(ticker_symbol)
        price = None
        
        if hasattr(stock, 'fast_info'):
            price = stock.fast_info.get('lastPrice') or stock.fast_info.get('previousClose')
        
        if price is None and hasattr(stock, 'info') and isinstance(stock.info, dict):
            price = stock.info.get('regularMarketPrice') or stock.info.get('currentPrice')

        if price is not None and float(price) > 0:
            price_display = f"${float(price):.2f}"
        else:
            status = "Price Unavailable"
    except Exception as e:
        print(f"Warning fetching {ticker_symbol}: {e}")
        status = "Fetch Error"

    return {
        "Ticker": ticker_symbol,
        "Company": company_name,
        "Price (SGD)": price_display,
        "Status": status
    }

def generate_dashboard():
    print("Fetching data for all 8 SGX Core stocks...")
    results = [fetch_stock_data(item) for item in CORE_8_STOCKS]
    
    df = pd.DataFrame(results)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>SGX Core 8 Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px; background: #f8f9fa; color: #212529; }}
        h1 {{ color: #0d6efd; border-bottom: 2px solid #0d6efd; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #0d6efd; color: #fff; }}
        tr:hover {{ background: #f1f3f5; }}
        .timestamp {{ font-size: 0.85em; color: #6c757d; }}
    </style>
</head>
<body>
    <h1>SGX Core 8 Dashboard</h1>
    <p class="timestamp">Last Updated: {timestamp}</p>
    {df.to_html(index=False, classes='table')}
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Successfully generated index.html with all {len(results)} stocks!")

if __name__ == "__main__":
    generate_dashboard()
