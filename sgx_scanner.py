import yfinance as yf
import pandas as pd
import datetime
import os

# ======================================================================
# ⚙️ CONFIGURATION (SETTINGS ARE RIGHT HERE AT THE TOP!)
# ======================================================================
GITHUB_USERNAME = "shannonluiz78"  # 👈 Change to your GitHub username
GITHUB_REPO_NAME = "sgx-stock-scanner"     # 👈 Change if your repo has a different name
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
        "horizon": "SHORT-TERM (1–3 MOS)",
        "badge_cls": "badge-short",
        "reason": "<strong>Momentum Breakout.</strong> Massive volume accumulation driven by record-high order books for eco-friendly container vessels. RSI is elevated, so aim to enter on a minor pull-back into the buy zone.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.15, "stop_mult": 0.91
    },
    "OU8.SI": {
        "horizon": "MID-TERM (1–3 YRS)",
        "badge_cls": "badge-mid",
        "reason": "<strong>Growth & Supply Shortage.</strong> Specialized worker and foreign student accommodation operator benefiting from severe supply shortages across Singapore and the UK. RSI is in the ideal zone for continuation.",
        "buy_mult": (0.95, 0.99), "target_mult": 1.24, "stop_mult": 0.88
    },
    "G13.SI": {
        "horizon": "MID-TERM (1–3 YRS)",
        "badge_cls": "badge-mid",
        "reason": "<strong>Value Recovery.</strong> Trading near low valuation levels with a strong net-cash balance sheet. RWS 2.0 expansion and resilient tourism volume provide multi-month upside backed by a high dividend yield floor.",
        "buy_mult": (0.95, 1.00), "target_mult": 1.24, "stop_mult": 0.89
    },
    "U11.SI": {
        "horizon": "LONG-TERM (5–10 YRS)",
        "badge_cls": "badge-long",
        "reason": "<strong>Core Income Anchor.</strong> ASEAN expansion continues to drive wealth management and loan growth. Healthy RSI consolidation makes it an attractive steady income compounder.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.15, "stop_mult": 0.92
    },
    "C52.SI": {
        "horizon": "LONG-TERM (3–5+ YRS)",
        "badge_cls": "badge-long",
        "reason": "<strong>Defensive Yield.</strong> Global land transport operator winning lucrative overseas public transport contracts in the UK and Australia. Acts as a highly stable, high dividend payer.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.22, "stop_mult": 0.90
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
    """Safely retrieves dividend yield and fixes percentage scaling bugs."""
    try:
        info = ticker_obj.info
        yield_val = info.get('dividendYield') or info.get('trailingAnnualDividendYield') or 0.0
        yield_val = float(yield_val)
        
        # Scale back if returned as a whole percentage
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
            
            # Default metadata fallback
            meta = STOCK_METADATA.get(ticker, {
                "horizon": "MID-TERM (1–3 YRS)",
                "badge_cls": "badge-mid",
                "reason": "Technical trend alignment with solid volume support.",
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
    return results_df.head(5)

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
                <div>
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">{row['Price_Str']}</div>
                </div>
                <div>
                    <div class="metric-label">Dividend Yield</div>
                    <div class="metric-value">{row['Yield']}</div>
                </div>
                <div>
                    <div class="metric-label">Vol Surge</div>
                    <div class="metric-value">{row['VolSurge']}</div>
                </div>
                <div>
                    <div class="metric-label">RSI (14)</div>
                    <div class="metric-value">{row['RSI']}</div>
                </div>
            </div>

            <div class="trade-setup">
                <div><strong>Target Buy:</strong> {row['BuyZone']}</div>
                <div><strong>Target Sell:</strong> {row['TargetSell']}</div>
                <div><strong>Stop Loss:</strong> {row['StopLoss']}</div>
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
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 850px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}
        .header h1 {{
            color: #38bdf8;
            margin-bottom: 5px;
        }}
        .timestamp {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .rescan-btn {{
            display: inline-block;
            background-color: #0284c7;
            color: #ffffff;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.95em;
            transition: background 0.2s;
            box-shadow: 0 4px 10px rgba(2, 132, 199, 0.4);
        }}
        .rescan-btn:hover {{
            background-color: #0369a1;
        }}
        .stock-card {{
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 12px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .ticker-title h2 {{
            margin: 0;
            color: #f59e0b;
            font-size: 1.3em;
        }}
        .company-name {{
            color: #94a3b8;
            font-size: 0.85em;
            font-weight: normal;
        }}
        .badges {{
            display: flex;
            gap: 8px;
        }}
        .badge {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .badge-score {{ background: #831843; color: #f472b6; }}
        .badge-short {{ background: #7c2d12; color: #fdba74; }}
        .badge-mid {{ background: #0e7490; color: #67e8f9; }}
        .badge-long {{ background: #065f46; color: #34d399; }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            background: #0f172a;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 0.75em;
            color: #94a3b8;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 1.1em;
            font-weight: bold;
            color: #f8fafc;
            margin-top: 4px;
        }}
        
        .trade-setup {{
            display: flex;
            justify-content: space-between;
            background: #172554;
            border: 1px solid #1e40af;
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.9em;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .reason-box {{
            background-color: #0f172a;
            border-left: 4px solid #38bdf8;
            padding: 12px 15px;
            border-radius: 0 8px 8px 0;
            font-size: 0.9em;
            color: #cbd5e1;
            line-height: 1.5;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 0.8em;
            color: #64748b;
            text-align: center;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🇸🇬 SGX Stock Scanner Dashboard</h1>
        <div class="timestamp">Last Scanned: {now}</div>
        <a href="{rescan_url}" target="_blank" class="rescan-btn">⚡ Rescan Now (Mid-Week Scan)</a>
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
