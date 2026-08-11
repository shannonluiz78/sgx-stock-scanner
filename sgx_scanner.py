import yfinance as yf
import pandas as pd
import datetime
import os

# ======================================================================
# ⚙️ CONFIGURATION (SETTINGS AT THE VERY TOP!)
# ======================================================================
GITHUB_USERNAME = "shannonluiz78"  # 👈 Change to your GitHub username
GITHUB_REPO_NAME = "sgx-stock-scanner"     # 👈 Change if your repo name is different
TOP_STOCKS_COUNT = 8                       # 👈 Expanded to Top 8 Stocks
# ======================================================================

# 30-Stock SGX Universe
SGX_TICKERS = {
    "D05.SI": "DBS Group",
    "O39.SI": "OCBC Bank",
    "U11.SI": "UOB Bank",
    "S68.SI": "SGX Ltd",
    "AIY.SI": "iFAST Corp",
    "OV8.SI": "Sheng Siong",
    "F34.SI": "Wilmar Intl",
    "F03.SI": "Food Empire",
    "OYY.SI": "PropNex Ltd",
    "CLN.SI": "APAC Realty",
    "C52.SI": "ComfortDelGro",
    "S58.SI": "SATS Ltd",
    "C6L.SI": "Singapore Airlines",
    "BS6.SI": "Yangzijiang Shipbuilding",
    "BN4.SI": "Keppel Ltd",
    "S63.SI": "ST Engineering",
    "U96.SI": "Sembcorp Industries",
    "F9D.SI": "Boustead Singapore",
    "V03.SI": "Venture Corp",
    "E26.SI": "Frencken Group",
    "AWX.SI": "AEM Holdings",
    "532.SI": "Micro-Mechanics",
    "OU8.SI": "Centurion Corp",
    "Z74.SI": "Singtel",
    "G13.SI": "Genting Singapore",
    "C38U.SI": "CICT REIT",
    "A17U.SI": "CapitaLand Ascendas REIT",
    "M44U.SI": "Mapletree Logistics Trust",
    "BUOU.SI": "Frasers Centrepoint Trust",
    "N2IU.SI": "Mapletree Pan Asia Comm Trust"
}

# Metadata & Trade Setups for High-Conviction Picks
STOCK_METADATA = {
    "BS6.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)",
        "badge_cls": "badge-short",
        "reason": "<strong>Momentum Breakout.</strong> Massive volume accumulation driven by record-high order books for eco-friendly container vessels. RSI is elevated, so aim to enter on a minor pullback.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.15, "stop_mult": 0.91
    },
    "O39.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)",
        "badge_cls": "badge-short",
        "reason": "<strong>Swing Trade Opportunity.</strong> Strong institutional support and steady wealth management inflows. Ideal for riding price bounces off major moving average support levels.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.10, "stop_mult": 0.93
    },
    "OU8.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "badge_cls": "badge-mid",
        "reason": "<strong>Growth & Supply Shortage.</strong> Specialized worker and foreign student accommodation operator benefiting from severe supply shortages across Singapore and the UK.",
        "buy_mult": (0.95, 0.99), "target_mult": 1.24, "stop_mult": 0.88
    },
    "G13.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "badge_cls": "badge-mid",
        "reason": "<strong>Value Recovery.</strong> Trading near low valuation levels with a strong net-cash balance sheet. RWS 2.0 expansion and resilient tourism volume provide multi-month upside.",
        "buy_mult": (0.95, 1.00), "target_mult": 1.24, "stop_mult": 0.89
    },
    "U11.SI": {
        "horizon": "🏛️ LONG-TERM (5–10 YRS)",
        "badge_cls": "badge-long",
        "reason": "<strong>Core Income Anchor.</strong> Regional ASEAN expansion continues to drive wealth management and loan growth. Healthy RSI consolidation makes it an attractive income compounder.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.15, "stop_mult": 0.92
    },
    "C52.SI": {
        "horizon": "🏛️ LONG-TERM (3–5+ YRS)",
        "badge_cls": "badge-long",
        "reason": "<strong>Defensive Yield.</strong> Global land transport operator winning lucrative public transport tenders in the UK and Australia. Highly stable, high-dividend defensive stock.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.22, "stop_mult": 0.90
    },
    "D05.SI": {
        "horizon": "🏛️ LONG-TERM (5–10 YRS)",
        "badge_cls": "badge-long",
        "reason": "<strong>Dividend Pillar.</strong> Southeast Asia's largest banking network with industry-leading ROE figures. Consistent quarterly payouts make it a foundational portfolio holding.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.12, "stop_mult": 0.93
    }
}

VOLUME_SURGE_THRESHOLD = 1.5

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_dividend_yield(ticker_obj):
    """Safely retrieves dividend yield and normalizes percentage scale."""
    try:
        info = ticker_obj.info
        yield_val = info.get('dividendYield') or info.get('trailingAnnualDividendYield') or 0.0
        yield_val = float(yield_val)
        
        if yield_val > 1.0:
            yield_val = yield_val / 100.0
            
        return yield_val
    except Exception:
        return 0.0

def scan_stocks():
    results = []
    
    for ticker, name in SGX_TICKERS.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y")
            
            if df.empty or len(df) < 50:
                continue
            
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            df['RSI_14'] = calculate_rsi(df['Close'])
            
            latest = df.iloc[-1]
            latest_price = latest['Close']
            vol_sma = latest['Vol_SMA_20']
            volume_surge = (latest['Volume'] / vol_sma) if vol_sma > 0 else 1.0
            
            rsi = latest['RSI_14']
            trend_bullish = latest['SMA_20'] > latest['SMA_50']
            price_above_50sma = latest_price > latest['SMA_50']
            div_yield = get_dividend_yield(stock)
            
            score = 0
            if volume_surge >= VOLUME_SURGE_THRESHOLD: score += 3
            elif volume_surge >= 1.2: score += 1
            
            if trend_bullish: score += 2
            if price_above_50sma: score += 1
            if 45 <= rsi <= 68: score += 2
            if div_yield >= 0.05: score += 2
            elif div_yield >= 0.035: score += 1
            
            # Metadata fallback for stocks not explicitly customized
            meta = STOCK_METADATA.get(ticker, {
                "horizon": "📈 MID-TERM (1–3 YRS)",
                "badge_cls": "badge-mid",
                "reason": "Technical trend alignment with solid volume support and dividend backing.",
                "buy_mult": (0.96, 0.99), "target_mult": 1.18, "stop_mult": 0.90
            })
            
            buy_low = latest_price * meta["buy_mult"][0]
            buy_high = latest_price * meta["buy_mult"][1]
            target_sell = latest_price * meta["target_mult"]
            stop_loss = latest_price * meta["stop_mult"]
            
            results.append({
                "Ticker": ticker,
                "Name": name,
                "Price": latest_price,
                "Price_Str": f"S${latest_price:.2f}",
                "Yield": f"{div_yield * 100:.2f}%",
                "VolSurge": f"{volume_surge:.2f}x",
                "RSI": f"{rsi:.1f}",
                "Score": score,
                "Horizon": meta["horizon"],
                "BadgeCls": meta["badge_cls"],
                "Reason": meta["reason"],
                "BuyZone": f"S${buy_low:.2f} – S${buy_high:.2f}",
                "TargetSell": f"S${target_sell:.2f}",
                "StopLoss": f"S${stop_loss:.2f}"
            })
        except Exception as e:
            print(f"Error scanning {ticker}: {e}")

    results_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    return results_df.head(TOP_STOCKS_COUNT)

def build_html_dashboard(top_stocks):
    now = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p SGT")
    rescan_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/actions/workflows/scanner.yml"
    
    cards_html = ""
    for _, row in top_stocks.iterrows():
        cards_html += f"""
        <div class="stock-card">
            <div class="card-top">
                <div class="ticker-title">
                    <h2>{row['Ticker']} <span class="company-name">• {row['Name']}</span></h2>
                </div>
                <div class="badges">
                    <span class="badge {row['BadgeCls']}">{row['Horizon']}</span>
                    <span class="badge badge-score">SCORE: {row['Score']}/10</span>
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-label">Price</div>
                    <div class="metric-value">{row['Price_Str']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Yield</div>
                    <div class="metric-value highlight-yield">{row['Yield']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Vol Surge</div>
                    <div class="metric-value">{row['VolSurge']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">RSI (14)</div>
                    <div class="metric-value">{row['RSI']}</div>
                </div>
            </div>

            <div class="trade-setup">
                <div>🎯 <strong>Target Buy:</strong> {row['BuyZone']}</div>
                <div>🚀 <strong>Target Sell:</strong> {row['TargetSell']}</div>
                <div>🛡️ <strong>Stop Loss:</strong> {row['StopLoss']}</div>
            </div>

            <div class="reason-box">
                {row['Reason']}
            </div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGX Weekly Stock Scanner Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-purple: #a855f7;
            --accent-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-rose: #f43f5e;
            --accent-amber: #f59e0b;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-gradient);
            background-attachment: fixed;
            color: var(--text-primary);
            margin: 0;
            padding: 24px 16px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 860px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 32px;
        }}

        .header h1 {{
            font-size: 2.2em;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #f43f5e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 8px 0;
            letter-spacing: -0.5px;
        }}

        .timestamp {{
            color: var(--text-secondary);
            font-size: 0.9em;
            font-weight: 600;
            margin-bottom: 18px;
        }}

        .rescan-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: #ffffff;
            padding: 12px 24px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95em;
            transition: all 0.25s ease;
            box-shadow: 0 8px 20px -4px rgba(168, 85, 247, 0.4);
        }}

        .rescan-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 25px -4px rgba(168, 85, 247, 0.6);
            background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
        }}

        .stock-card {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 22px;
            margin-bottom: 22px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
            transition: border-color 0.3s ease, transform 0.2s ease;
        }}

        .stock-card:hover {{
            border-color: rgba(168, 85, 247, 0.3);
            transform: translateY(-2px);
        }}

        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 14px;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }}

        .ticker-title h2 {{
            margin: 0;
            color: #38bdf8;
            font-size: 1.4em;
            font-weight: 800;
        }}

        .company-name {{
            color: var(--text-secondary);
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badges {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .badge {{
            padding: 6px 12px;
            border-radius: 30px;
            font-size: 0.78em;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}

        .badge-score {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}
        .badge-short {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-mid {{ background: rgba(6, 182, 212, 0.15); color: #38bdf8; border: 1px solid rgba(6, 182, 212, 0.3); }}
        .badge-long {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            background: rgba(15, 23, 42, 0.6);
            padding: 14px;
            border-radius: 14px;
            margin-bottom: 16px;
            text-align: center;
        }}

        .metric-label {{
            font-size: 0.72em;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}

        .metric-value {{
            font-size: 1.15em;
            font-weight: 800;
            color: var(--text-primary);
            margin-top: 4px;
        }}

        .highlight-yield {{
            color: #34d399;
        }}

        .trade-setup {{
            display: flex;
            justify-content: space-between;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.25);
            padding: 12px 18px;
            border-radius: 12px;
            font-size: 0.9em;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 10px;
            color: #e0e7ff;
        }}

        .reason-box {{
            background: rgba(15, 23, 42, 0.5);
            border-left: 4px solid var(--accent-purple);
            padding: 14px 16px;
            border-radius: 0 12px 12px 0;
            font-size: 0.9em;
            color: #cbd5e1;
            line-height: 1.6;
        }}

        .footer {{
            margin-top: 40px;
            font-size: 0.82em;
            color: var(--text-secondary);
            text-align: center;
            font-weight: 600;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🇸🇬 SGX Top 8 Weekly Watchlist</h1>
        <div class="timestamp">Last Updated: {now}</div>
        <a href="{rescan_url}" target="_blank" class="rescan-btn">⚡ Rescan Now (Mid-Week)</a>
    </div>

    {cards_html}

    <div class="footer">
        Automated Quantitative Screen across 30 SGX Counters. Powered by GitHub Actions & Python.
    </div>
</div>

</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard generated successfully in index.html")

if __name__ == "__main__":
    top_df = scan_stocks()
    build_html_dashboard(top_df)
