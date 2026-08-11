import yfinance as yf
import pandas as pd
import numpy as np
import json
import os

# ==========================================
# 1. DEFINITION OF THE 8 AGREED SGX STOCKS
# ==========================================
STOCKS = [
    {"ticker": "D05.SI",  "name": "DBS Group Holdings Ltd",                "sector": "Financial Services"},
    {"ticker": "O39.SI",  "name": "Oversea-Chinese Banking Corp (OCBC)",  "sector": "Financial Services"},
    {"ticker": "U11.SI",  "name": "United Overseas Bank Ltd (UOB)",         "sector": "Financial Services"},
    {"ticker": "Z74.SI",  "name": "Singapore Telecommunications (Singtel)", "sector": "Communication Services"},
    {"ticker": "BN4.SI",  "name": "Keppel Ltd",                            "sector": "Industrials"},
    {"ticker": "F34.SI",  "name": "Wilmar International Ltd",              "sector": "Consumer Staples"},
    {"ticker": "C38U.SI", "name": "CapitaLand Integrated Commercial Trust",  "sector": "Real Estate (REIT)"},
    {"ticker": "A17U.SI", "name": "CapitaLand Ascendas REIT",              "sector": "Real Estate (REIT)"}
]


# ==========================================
# 2. SAFE DATA EXTRACTION HELPERS
# ==========================================
def get_safe_financial_row(df, keywords):
    """Searches a yfinance DataFrame for rows matching keyword lists to avoid KeyError."""
    if df is None or df.empty:
        return None
    for idx in df.index:
        idx_str = str(idx).lower()
        if any(kw.lower() in idx_str for kw in keywords):
            return df.loc[idx]
    return None

def fetch_stock_details(item):
    """Fetches key financial metrics, 5y price history, and 5y financials safely."""
    ticker_symbol = item["ticker"]
    print(f"Fetching data for: {ticker_symbol} ({item['name']})...")
    
    t = yf.Ticker(ticker_symbol)
    
    # --- Fetch Info ---
    try:
        info = t.info or {}
    except Exception as e:
        print(f"  [Warning] Info fetch failed for {ticker_symbol}: {e}")
        info = {}

    # Extract Key Metrics safely
    price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose') or 0.0
    pe_ratio = info.get('trailingPE')
    pb_ratio = info.get('priceToBook')
    
    div_yield = info.get('dividendYield')
    if div_yield is not None:
        if div_yield < 1.0:
            div_yield = round(div_yield * 100, 2)
        else:
            div_yield = round(div_yield, 2)
    else:
        div_yield = "N/A"

    # --- Fetch 5-Year Price History ---
    hist_dates = []
    hist_prices = []
    try:
        hist = t.history(period="5y")
        if not hist.empty:
            # Resample weekly to keep HTML payload lightweight
            hist_weekly = hist['Close'].resample('W').last().dropna()
            hist_dates = [d.strftime('%Y-%m-%d') for d in hist_weekly.index]
            hist_prices = [round(p, 3) for p in hist_weekly.values]
    except Exception as e:
        print(f"  [Warning] Price history fetch failed for {ticker_symbol}: {e}")

    # --- Fetch 5-Year Financial Statements ---
    fin_years = []
    fin_revenue = []
    fin_net_income = []
    try:
        financials = t.financials
        if financials is not None and not financials.empty:
            rev_row = get_safe_financial_row(financials, ['total revenue', 'operating revenue', 'revenue'])
            net_row = get_safe_financial_row(financials, ['net income', 'net income common stockholders'])

            if rev_row is not None:
                # Sort dates chronologically
                sorted_dates = sorted(rev_row.index)
                for date_col in sorted_dates:
                    year_label = str(date_col)[:4] if hasattr(date_col, 'year') else str(date_col)
                    rev_val = rev_row[date_col]
                    net_val = net_row[date_col] if (net_row is not None and date_col in net_row) else 0

                    if not pd.isna(rev_val):
                        fin_years.append(year_label)
                        fin_revenue.append(round(float(rev_val) / 1e9, 2)) # in SGD Billions
                        fin_net_income.append(round(float(net_val) / 1e9, 2) if not pd.isna(net_val) else 0.0)
    except Exception as e:
        print(f"  [Warning] Financials fetch failed for {ticker_symbol}: {e}")

    return {
        "ticker": ticker_symbol,
        "name": item["name"],
        "sector": item["sector"],
        "price": f"SGD {price:.2f}" if isinstance(price, (int, float)) and price > 0 else "N/A",
        "pe": f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A",
        "pb": f"{pb_ratio:.2f}" if isinstance(pb_ratio, (int, float)) else "N/A",
        "div_yield": f"{div_yield}%" if div_yield != "N/A" else "N/A",
        "hist_dates": hist_dates,
        "hist_prices": hist_prices,
        "fin_years": fin_years,
        "fin_revenue": fin_revenue,
        "fin_net_income": fin_net_income
    }


# ==========================================
# 3. HTML DASHBOARD GENERATOR
# ==========================================
def generate_html_dashboard(data_list):
    """Generates a standalone, responsive HTML dashboard featuring all 8 stocks."""
    
    # Format table rows
    table_rows_html = ""
    for idx, d in enumerate(data_list, 1):
        table_rows_html += f"""
        <tr>
            <td><strong>{idx}</strong></td>
            <td><strong>{d['ticker']}</strong></td>
            <td>{d['name']}</td>
            <td><span class="badge">{d['sector']}</span></td>
            <td class="num">{d['price']}</td>
            <td class="num">{d['pe']}</td>
            <td class="num">{d['pb']}</td>
            <td class="num highlight">{d['div_yield']}</td>
        </tr>
        """

    # Convert data list to JSON for embedded Plotly JS rendering
    data_json = json.dumps(data_list)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGX Core 8 Portfolio Scanner</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #38bdf8;
            --border-color: #334155;
            --green: #4ade80;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        header {{
            margin-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 16px;
        }}
        h1 {{
            margin: 0 0 8px 0;
            font-size: 1.8rem;
            color: var(--accent-color);
        }}
        p.subtitle {{
            margin: 0;
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th, td {{
            padding: 12px 14px;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background-color: rgba(255, 255, 255, 0.03);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
        }}
        tr:hover {{
            background-color: rgba(255, 255, 255, 0.02);
        }}
        .num {{
            text-align: right;
            font-family: "SFMono-Regular", Consolas, monospace;
        }}
        .highlight {{
            color: var(--green);
            font-weight: 600;
        }}
        .badge {{
            background: #0284c7;
            color: #fff;
            font-size: 0.75rem;
            padding: 3px 8px;
            border-radius: 12px;
        }}
        .controls {{
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        select {{
            background: var(--card-bg);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 1rem;
            outline: none;
            cursor: pointer;
        }}
        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        @media (max-width: 900px) {{
            .chart-grid {{ grid-template-columns: 1fr; }}
            table {{ font-size: 0.85rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SGX Core 8 Portfolio Scanner</h1>
            <p class="subtitle">Live market overview and 5-year historical analysis for Singapore's core blue-chip stocks.</p>
        </header>

        <div class="card">
            <h2 style="margin-top:0; font-size:1.2rem; color:var(--text-primary);">Portfolio Overview (All 8 Stocks)</h2>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Ticker</th>
                            <th>Company Name</th>
                            <th>Sector</th>
                            <th class="num">Price</th>
                            <th class="num">P/E</th>
                            <th class="num">P/B</th>
