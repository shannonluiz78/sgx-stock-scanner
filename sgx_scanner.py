import os
import datetime
import pandas as pd

def fetch_stock(ticker):
    """Fetches stock info safely without throwing uncaught exceptions."""
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        
        # Fast info is more reliable than stock.info in headless cloud runners
        price = None
        if hasattr(stock, 'fast_info'):
            price = stock.fast_info.get('lastPrice') or stock.fast_info.get('previousClose')
        
        if not price and hasattr(stock, 'info') and isinstance(stock.info, dict):
            price = stock.info.get('regularMarketPrice') or stock.info.get('currentPrice')
            
        if price:
            return {"Ticker": ticker, "Status": "Active", "Price (SGD)": f"${float(price):.2f}"}
    except Exception as err:
        print(f"Warning: Failed to fetch {ticker} -> {err}")

    return {"Ticker": ticker, "Status": "Data Pending", "Price (SGD)": "N/A"}

def generate_dashboard():
    print("Starting SGX Core 8 Scanner...")
    
    tickers = ["D05.SI", "O39.SI", "U11.SI", "Z74.SI", "C6L.SI", "C38U.SI", "A17U.SI", "Y92.SI"]
    results = [fetch_stock(t) for t in tickers]
    
    df = pd.DataFrame(results)
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
        
    print("Successfully generated index.html!")

if __name__ == "__main__":
    generate_dashboard()
