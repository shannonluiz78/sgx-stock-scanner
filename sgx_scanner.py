import yfinance as yf
import pandas as pd
import numpy as np
import json
import time

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
# 2. BULLETPROOF DATA EXTRACTION HELPERS
# ==========================================
def get_safe_financial_row(df, keywords):
    """Searches a yfinance DataFrame for rows matching keywords safely, ensuring a 1D Series even if index labels duplicate."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return None
    for idx in df.index:
        idx_str = str(idx).lower()
        if any(kw.lower() in idx_str for kw in keywords):
            res = df.loc[idx]
            if isinstance(res, pd.DataFrame):
                res = res.iloc[0]
            return res
    return None

def extract_scalar(val):
    """Converts any pandas/numpy scalar or single-element Series/array to float cleanly."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (pd.Series, np.ndarray, list)):
        if len(val) == 0:
            return None
        val = val.iloc[0] if hasattr(val, 'iloc') else val[0]
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def fetch_stock_details(item):
    """Fetches stock data, 5y price history, and 5y financials safely with robust fallbacks."""
    ticker_symbol = item["ticker"]
    print(f"Processing: {ticker_symbol} ({item['name']})...")
    
    record = {
        "ticker": ticker_symbol,
        "name": item["name"],
        "sector": item["sector"],
        "price": "N/A",
        "pe": "N/A",
        "pb": "N/A",
        "div_yield": "N/A",
        "hist_dates": [],
        "hist_prices": [],
        "fin_years": [],
        "fin_revenue": [],
        "fin_net_income": []
    }
    
    try:
        t = yf.Ticker(ticker_symbol)
        
        # 1. Fetch Info
        info = {}
        try:
            info = t.info or {}
        except Exception as e:
            print(f"  [Warning] Info fetch failed for {ticker_symbol}: {e}")

        raw_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose') or info.get('navPrice')
        raw_pe = info.get('trailingPE')
        raw_pb = info.get('priceToBook')
        raw_div = info.get('dividendYield')

        if raw_price is not None:
            record["price"] = f"SGD {float(raw_price):.2f}"
        if raw_pe is not None:
            record["pe"] = f"{float(raw_pe):.2f}"
        if raw_pb is not None:
            record["pb"] = f"{float(raw_pb):.2f}"
        
        if raw_div is not None:
            div_val = float(raw_div)
            if div_val < 1.0:
                div_val *= 100
            record["div_yield"] = f"{div_val:.2f}%"

        # 2. Fetch 5-Year Weekly Historical Price
        try:
            hist = t.history(period="5y")
            if not hist.empty and 'Close' in hist.columns:
                close_series = hist['Close']
                if isinstance(close_series, pd.DataFrame):
                    close_series = close_series.iloc[:, 0]
                
                weekly = close_series.resample('W').last().dropna()
                record["hist_dates"] = [d.strftime('%Y-%m-%d') for d in weekly.index]
                record["hist_prices"] = [round(float(p), 3) for p in weekly.values]
        except Exception as e:
            print(f"  [Warning] History fetch failed for {ticker_symbol}: {e}")

        # 3. Fetch Financial Statements
        try:
            financials = t.financials
            if financials is not None and not financials.empty:
                rev_row = get_safe_financial_row(financials, ['total revenue', 'operating revenue', 'revenue'])
                net_row = get_safe_financial_row(financials, ['net income', 'net income common stockholders'])

                if rev_row is not None:
                    sorted_dates = sorted(rev_row.index)
                    for date_col in sorted_dates:
                        year_label = str(date_col)[:4] if hasattr(date_col, 'year') else str(date_col)
                        
                        rev_val = extract_scalar(rev_row[date_col])
                        net_val = extract_scalar(net_row[date_col]) if (net_row is not None and date_col in net_row) else 0.0

                        if rev_val is not None:
                            record["fin_years"].append(year_label)
                            record["fin_revenue"].append(round(rev_val / 1e9, 2))
                            record["fin_net_income"].append(round(net_val / 1e9, 2) if net_val is not None else 0.0)
        except Exception as e:
            print(f"  [Warning] Financials fetch failed for {ticker_symbol}: {e}")

    except Exception as main_err:
        print(f"  [Error] Unhandled error processing {ticker_symbol}: {main_err}")

    # Prevent Yahoo Finance rate limiting
    time.sleep(1.2)
    return record


# ==========================================
# 3. HTML DASHBOARD GENERATOR
# ==========================================
def generate_html_dashboard(data_list):
    """Generates a standalone, responsive HTML dashboard featuring all 8 stocks."""
    
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
                            <th class="num">Div Yield</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="controls">
                <label for="stockSelect"><strong>Select Stock for 5-Year Deep Dive:</strong></label>
                <select id="stockSelect" onchange="renderCharts()"></select>
            </div>
            
            <div class="chart-grid">
                <div id="priceChart" style="height:380px;"></div>
                <div id="financialsChart" style="height:380px;"></div>
            </div>
        </div>
    </div>

    <script>
        const stocksData = {data_json};

        const selectEl = document.getElementById('stockSelect');
        stocksData.forEach((s, idx) => {{
            const opt = document.createElement('option');
            opt.value = idx;
            opt.textContent = `${{s.ticker}} - ${{s.name}}`;
            selectEl.appendChild(opt);
        }});

        function renderCharts() {{
            const selectedIdx = selectEl.value;
            const stock = stocksData[selectedIdx];

            // 1. Price Chart
            const priceTrace = {{
                x: stock.hist_dates,
                y: stock.hist_prices,
                type: 'scatter',
                mode: 'lines',
                line: {{ color: '#38bdf8', width: 2 }},
                name: 'Price (SGD)'
            }};
            
            const priceLayout = {{
                title: {{ text: `${{stock.ticker}} - 5-Year Weekly Price Trend`, font: {{ color: '#f8fafc', size: 14 }} }},
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                xaxis: {{ gridcolor: '#334155', color: '#94a3b8' }},
                yaxis: {{ gridcolor: '#334155', color: '#94a3b8', title: 'Price (SGD)' }},
                margin: {{ t: 40, b: 40, l: 50, r: 20 }}
            }};

            Plotly.newPlot('priceChart', [priceTrace], priceLayout, {{responsive: true}});

            // 2. Financials Chart
            const revTrace = {{
                x: stock.fin_years,
                y: stock.fin_revenue,
                name: 'Revenue (Billion SGD)',
                type: 'bar',
                marker: {{ color: '#0
