import os
import datetime
import pandas as pd
import yfinance as yf

# Core 8 SGX Blue-Chip Stocks
CORE_8_STOCKS = [
    {"ticker": "D05.SI", "name": "DBS Group Holdings", "sector": "Banking"},
    {"ticker": "O39.SI", "name": "OCBC Bank", "sector": "Banking"},
    {"ticker": "U11.SI", "name": "UOB", "sector": "Banking"},
    {"ticker": "Z74.SI", "name": "Singtel", "sector": "Telecommunications"},
    {"ticker": "S68.SI", "name": "Singapore Exchange", "sector": "Financial Services"},
    {"ticker": "C38U.SI", "name": "CapitaLand Integrated Comm Trust", "sector": "REIT"},
    {"ticker": "A17U.SI", "name": "CapitaLand Ascendas REIT", "sector": "REIT"},
    {"ticker": "C6L.SI", "name": "Singapore Airlines", "sector": "Aviation"}
]

def format_number(val, is_currency=False, is_percent=False):
    if val is None or pd.isna(val) or val == "N/A":
        return "N/A"
    try:
        num = float(val)
        if is_percent:
            return f"{num * 100:.2f}%" if num < 1 else f"{num:.2f}%"
        if is_currency:
            return f"${num:.2f}"
        return f"{num:.2f}"
    except (ValueError, TypeError):
        return "N/A"

def format_market_cap(val):
    if not val or val == "N/A":
        return "N/A"
    try:
        cap = float(val)
        if cap >= 1e9:
            return f"${cap / 1e9:.2f}B"
        elif cap >= 1e6:
            return f"${cap / 1e6:.2f}M"
        return f"${cap:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

def fetch_stock_data(item):
    symbol = item["ticker"]
    name = item["name"]
    sector = item["sector"]

    price, change, p_change = "N/A", 0.0, 0.0
    mkt_cap, pe_ratio, div_yield, range_52 = "N/A", "N/A", "N/A", "N/A"

    try:
        stock = yf.Ticker(symbol)
        
        # Price and Change metrics
        if hasattr(stock, 'fast_info'):
            last_price = stock.fast_info.get('lastPrice') or stock.fast_info.get('previousClose')
            prev_close = stock.fast_info.get('previousClose')
            if last_price and prev_close:
                price = float(last_price)
                change = price - float(prev_close)
                p_change = (change / float(prev_close)) * 100

        # Detailed fundamentals
        info = stock.info if hasattr(stock, 'info') and isinstance(stock.info, dict) else {}
        
        if price == "N/A":
            price = info.get('regularMarketPrice') or info.get('currentPrice') or "N/A"
        
        mkt_cap = format_market_cap(info.get('marketCap'))
        pe_ratio = format_number(info.get('trailingPE') or info.get('forwardPE'))
        div_yield = format_number(info.get('dividendYield'), is_percent=True)
        
        low_52 = info.get('fiftyTwoWeekLow')
        high_52 = info.get('fiftyTwoWeekHigh')
        if low_52 and high_52:
            range_52 = f"${low_52:.2f} - ${high_52:.2f}"

    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

    # Format change display badge
    if change > 0:
        change_html = f'<span class="badge pos">+${change:.2f} (+{p_change:.2f}%)</span>'
    elif change < 0:
        change_html = f'<span class="badge neg">-${abs(change):.2f} ({p_change:.2f}%)</span>'
    else:
        change_html = '<span class="badge neu">$0.00 (0.00%)</span>'

    formatted_price = f"${price:.2f}" if isinstance(price, (int, float)) else "N/A"

    return f"""
    <tr>
        <td><strong>{symbol}</strong></td>
        <td>{name}<br><small class="text-muted">{sector}</small></td>
        <td><strong>{formatted_price}</strong></td>
        <td>{change_html}</td>
        <td>{div_yield}</td>
        <td>{pe_ratio}</td>
        <td>{mkt_cap}</td>
        <td><small>{range_52}</small></td>
    </tr>
    """

def generate_dashboard():
    print("Generating enhanced SGX Core 8 Dashboard...")
    
    rows_html = "".join([fetch_stock_data(item) for item in CORE_8_STOCKS])
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>SGX Core 8 Financial Dashboard</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 24px; background: #0f172a; color: #f8fafc; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
        h1 {{ font-size: 1.75rem; font-weight: 700; margin: 0; color: #38bdf8; }}
        .timestamp {{ font-size: 0.85rem; color: #94a3b8; }}
        .table-card {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow-x: auto; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.95rem; }}
        th {{ background: #0f172a; padding: 14px 16px; color: #cbd5e1; font-weight: 600; border-bottom: 1px solid #334155; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; }}
        td {{ padding: 14px 16px; border-bottom: 1px solid #334155; vertical-align: middle; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #26354a; }}
        .text-muted {{ color: #94a3b8; font-size: 0.8rem; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; }}
        .pos {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }}
        .neg {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .neu {{ background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>SGX Core 8 Dashboard</h1>
                <div class="text-muted">Real-time tracking of Singapore's core market pillars</div>
            </div>
            <div class="timestamp">Last updated: {timestamp}</div>
        </div>
        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Company</th>
                        <th>Price (SGD)</th>
                        <th>Day Change</th>
                        <th>Div Yield</th>
                        <th>P/E Ratio</th>
                        <th>Market Cap</th>
                        <th>52-Wk Range</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("Successfully built index.html!")

if __name__ == "__main__":
    generate_dashboard()
