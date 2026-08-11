import datetime
import os
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. STOCK METADATA DICTIONARY
# ==========================================
STOCK_METADATA = {
    "G13.SI": {
        "name": "Genting Singapore",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "horizon_grp": "MID",
        "badge_cls": "badge-mid",
        "score": 10,
        "summary": "Value Recovery. Trading near low valuation levels with a strong net-cash balance sheet. RWS 2.0 expansion and resilient tourism volume provide multi-month upside backed by a high dividend yield floor.",
        "catalyst": "RWS 2.0 expansion phases kicking in alongside strong Asian tourism recovery.",
        "fundamentals": "Robust net cash position with stable operating cash flow and high dividend payout capability.",
        "technicals": "Consolidating near major support with bullish divergence on momentum indicators.",
        "risks": "Regional gaming competition and macro discretionary spending slowdown.",
        "buy_mult": (0.95, 1.00),
        "target_mult": 1.25,
        "stop_mult": 0.90,
    },
    "OU8.SI": {
        "name": "Centurion Corp",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "horizon_grp": "MID",
        "badge_cls": "badge-mid",
        "score": 10,
        "summary": "Growth & Supply Shortage. Specialized worker and foreign student accommodation operator benefiting from severe supply shortages across Singapore and the UK. RSI is in the ideal zone for continuation.",
        "catalyst": "High occupancy rates and rental rate revisions across PBWA/PBSA assets.",
        "fundamentals": "Strong earnings growth momentum with high dividend coverage.",
        "technicals": "Healthy upward channel with steady accumulation volume.",
        "risks": "Regulatory changes in foreign worker/student quota policies.",
        "buy_mult": (0.95, 0.98),
        "target_mult": 1.24,
        "stop_mult": 0.88,
    },
    "BS6.SI": {
        "name": "Yangzijiang Shipbuilding",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "horizon_grp": "MID",
        "badge_cls": "badge-mid",
        "score": 8,
        "summary": "Record Order Book. Multi-year earnings visibility supported by record high shipbuilding order backlog and strong margin execution.",
        "catalyst": "Delivery of higher-margin clean energy vessel contracts.",
        "fundamentals": "Strong balance sheet with record revenue execution capability.",
        "technicals": "Strong momentum trend trading above key moving averages.",
        "risks": "Steel cost fluctuations and USD/RMB exchange rate volatility.",
        "buy_mult": (0.94, 0.98),
        "target_mult": 1.20,
        "stop_mult": 0.90,
    },
    "U11.SI": {
        "name": "UOB Bank",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "horizon_grp": "MID",
        "badge_cls": "badge-mid",
        "score": 8,
        "summary": "Resilient Yield & Capital Returns. High dividend yield backed by strong regional wealth management expansion and capital optimization.",
        "catalyst": "Integration synergies from Citi ASEAN acquisition and non-interest income growth.",
        "fundamentals": "Solid CET1 ratio supporting sustained dividend payouts and buybacks.",
        "technicals": "Pullback towards support zone creating favorable risk/reward entry.",
        "risks": "Net interest margin compression during interest rate cut cycles.",
        "buy_mult": (0.96, 0.99),
        "target_mult": 1.15,
        "stop_mult": 0.92,
    },
    "C52.SI": {
        "name": "ComfortDelGro",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "horizon_grp": "MID",
        "badge_cls": "badge-mid",
        "score": 7,
        "summary": "Public Transport Margin Recovery. Earnings tailwinds from overseas contract wins and taxi commission adjustments.",
        "catalyst": "UK and Australian public bus tender repricing.",
        "fundamentals": "Improving operating margins and cash flow stability.",
        "technicals": "RSI forming a steady base with volume support on dips.",
        "risks": "Higher driver costs and competition from ride-hailing platforms.",
        "buy_mult": (0.95, 0.99),
        "target_mult": 1.18,
        "stop_mult": 0.91,
    }
}

# ✅ UPDATED (Add as many SGX tickers as you want):
TICKERS = [
    "G13.SI", "OU8.SI", "BS6.SI", "U11.SI", "C52.SI",
    "D05.SI", "O39.SI", "Z74.SI", "A17U.SI", "C38N.SI",
    "N2IU.SI", "ME8U.SI", "S68.SI", "F34.SI", "S58.SI",
    "U96.SI", "BN4.SI", "V03.SI", "S10.SI", "H78.SI",
    "Y92.SI", "J36.SI", "C6L.SI", "S63.SI", "D01.SI",
    "AW4.SI", "M44U.SI", "Q04.SI", "S41.SI", "A17.SI"
]

DEFAULT_META = {
    "horizon": "📈 MID-TERM (1–3 YRS)",
    "horizon_grp": "MID",
    "badge_cls": "badge-mid",
    "score": 7,
    "summary": "Technical trend alignment supported by positive institutional volume.",
    "catalyst": "Technical trend alignment supported by positive institutional trading volume.",
    "fundamentals": "Stable market capitalization with consistent historical dividend payouts.",
    "technicals": "Moving average convergence indicates a potential trend expansion phase.",
    "risks": "General SGX market volatility and sector-specific headwinds.",
    "buy_mult": (0.96, 0.99),
    "target_mult": 1.18,
    "stop_mult": 0.90,
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_stock_data(ticker):
    meta = STOCK_METADATA.get(ticker, DEFAULT_META)
    company_name = meta.get("name", ticker)
    
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6m")
        info = t.info or {}
        
        if df.empty or len(df) < 15:
            raise ValueError(f"Insufficient historical price data for {ticker}")
            
        latest_price = float(df['Close'].iloc[-1])
        avg_vol_20 = df['Volume'].tail(20).mean()
        latest_vol = df['Volume'].iloc[-1]
        vol_surge = (latest_vol / avg_vol_20) if avg_vol_20 > 0 else 1.0
        
        rsi_series = calculate_rsi(df['Close'])
        rsi = float(rsi_series.iloc[-1]) if not np.isnan(rsi_series.iloc[-1]) else 50.0
        
        raw_yield = info.get('dividendYield', 0.0) or 0.0
        yield_pct = raw_yield * 100 if raw_yield <= 1.0 else raw_yield
        if yield_pct == 0 and ticker in ["G13.SI", "OU8.SI", "BS6.SI", "U11.SI", "C52.SI"]:
            fallback_yields = {"G13.SI": 6.45, "OU8.SI": 2.47, "BS6.SI": 4.76, "U11.SI": 4.06, "C52.SI": 6.39}
            yield_pct = fallback_yields.get(ticker, 4.0)

    except Exception as e:
        print(f"Warning: yfinance fetch failed for {ticker}: {e}. Using baseline defaults.")
        default_prices = {"G13.SI": 0.63, "OU8.SI": 1.69, "BS6.SI": 4.64, "U11.SI": 42.05, "C52.SI": 1.35}
        default_yields = {"G13.SI": 6.45, "OU8.SI": 2.47, "BS6.SI": 4.76, "U11.SI": 4.06, "C52.SI": 6.39}
        default_rsi = {"G13.SI": 58.3, "OU8.SI": 60.6, "BS6.SI": 84.2, "U11.SI": 43.6, "C52.SI": 63.6}
        default_vol = {"G13.SI": 2.08, "OU8.SI": 2.55, "BS6.SI": 2.92, "U11.SI": 2.12, "C52.SI": 0.47}
        
        latest_price = default_prices.get(ticker, 1.0)
        yield_pct = default_yields.get(ticker, 4.0)
        rsi = default_rsi.get(ticker, 50.0)
        vol_surge = default_vol.get(ticker, 1.0)

    buy_low = latest_price * meta["buy_mult"][0]
    buy_high = latest_price * meta["buy_mult"][1]
    target_sell = latest_price * meta["target_mult"]
    stop_loss = latest_price * meta["stop_mult"]

    return {
        "ticker": ticker,
        "name": company_name,
        "price": latest_price,
        "yield": yield_pct,
        "vol_surge": vol_surge,
        "rsi": rsi,
        "score": meta.get("score", 8),
        "horizon": meta.get("horizon", "📈 MID-TERM (1–3 YRS)"),
        "summary": meta.get("summary", ""),
        "buy_range": f"S${buy_low:.2f} – S${buy_high:.2f}",
        "target_sell": f"S${target_sell:.2f}",
        "stop_loss": f"S${stop_loss:.2f}"
    }

# ==========================================
# 3. HTML GENERATION
# ==========================================
def generate_html(data_list):
    now_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p SGT")
    
    rows_html = ""
    cards_html = ""
    
    for item in data_list:
        rows_html += f"""
        <tr>
            <td class="ticker">{item['ticker']}</td>
            <td>{item['name']}</td>
            <td>S${item['price']:.2f}</td>
            <td><span class="badge badge-green">{item['yield']:.2f}%</span></td>
            <td><span class="badge badge-blue">{item['vol_surge']:.2f}x</span></td>
            <td>{item['rsi']:.1f}</td>
            <td><span class="badge badge-score">{item['score']} / 10</span></td>
        </tr>
        """
        
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <h3>{item['ticker']} • <span class="comp-name">{item['name']}</span></h3>
                <div>
                    <span class="badge badge-mid">{item['horizon']}</span>
                    <span class="badge badge-score">SCORE: {item['score']}/10</span>
                </div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-label">CURRENT PRICE</div>
                    <div class="metric-val">S${item['price']:.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">DIVIDEND YIELD</div>
                    <div class="metric-val">{item['yield']:.2f}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">VOL SURGE</div>
                    <div class="metric-val">{item['vol_surge']:.2f}x</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">RSI (14)</div>
                    <div class="metric-val">{item['rsi']:.1f}</div>
                </div>
            </div>
            
            <div class="targets-bar">
                <div><strong>Target Buy:</strong> {item['buy_range']}</div>
                <div><strong>Target Sell:</strong> {item['target_sell']}</div>
                <div><strong>Stop Loss:</strong> {item['stop_loss']}</div>
            </div>
            
            <div class="summary-box">
                {item['summary']}
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGX Stock Scanner Dashboard</title>
    <style>
        :root {{
            --bg-dark: #0f172a;
            --card-bg: #1e293b;
            --card-border: #334155;
            --accent-blue: #38bdf8;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --green: #22c55e;
            --red: #ef4444;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            margin: 0;
            padding: 24px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        h1, h2 {{
            text-align: center;
            color: var(--accent-blue);
        }}
        .timestamp {{
            text-align: center;
            color: var(--text-sub);
            font-size: 0.9rem;
            margin-bottom: 24px;
        }}
        .table-container {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 32px;
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th, td {{
            padding: 12px;
            border-bottom: 1px solid var(--card-border);
        }}
        th {{
            color: var(--accent-blue);
            font-size: 0.85rem;
            text-transform: uppercase;
        }}
        .ticker {{
            color: #fbbf24;
            font-weight: bold;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .badge-green {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; }}
        .badge-blue {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; }}
        .badge-score {{ background: rgba(225, 29, 72, 0.2); color: #fda4af; }}
        .badge-mid {{ background: rgba(14, 165, 233, 0.2); color: #38bdf8; }}
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}
        .card-header h3 {{
            margin: 0;
            color: #fbbf24;
        }}
        .comp-name {{
            color: var(--text-sub);
            font-weight: normal;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }}
        .metric-box {{
            background: rgba(15, 23, 42, 0.6);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 0.75rem;
            color: var(--text-sub);
            margin-bottom: 4px;
        }}
        .metric-val {{
            font-size: 1.1rem;
            font-weight: bold;
        }}
        .targets-bar {{
            display: flex;
            justify-content: space-between;
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            margin-bottom: 16px;
        }}
        .summary-box {{
            border-left: 4px solid var(--accent-blue);
            padding-left: 12px;
            font-size: 0.95rem;
            color: #cbd5e1;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🇸🇬 SGX Top 5 High-Conviction Picks</h1>
        <div class="timestamp">Last Updated: {now_str} | Target Execution: Monday Market Open</div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Company Name</th>
                        <th>Price</th>
                        <th>Yield</th>
                        <th>Vol Surge</th>
                        <th>RSI (14)</th>
                        <th>Rank Score</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        
        <h2>🇸🇬 SGX Stock Scanner Dashboard</h2>
        <div class="timestamp">Last Scanned: {now_str}</div>
        
        {cards_html}
    </div>
</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully generated index.html")

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    results = []
    for ticker in TICKERS:
        data = fetch_stock_data(ticker)
        results.append(data)
        
    generate_html(results)
