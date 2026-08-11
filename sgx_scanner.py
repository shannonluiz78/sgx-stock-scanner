import yfinance as yf
import pandas as pd
import datetime
import os
import requests

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

VOLUME_SURGE_THRESHOLD = 1.5

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_dividend_yield(ticker_obj):
    try:
        info = ticker_obj.info
        yield_val = info.get('dividendYield') or info.get('trailingAnnualDividendYield') or 0.0
        return float(yield_val)
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
            
            results.append({
                "Ticker": ticker,
                "Name": name,
                "Price": f"S${latest_price:.2f}",
                "Yield": f"{div_yield * 100:.2f}%",
                "VolSurge": f"{volume_surge:.2f}x",
                "RSI": f"{rsi:.1f}",
                "Score": score
            })
        except Exception as e:
            print(f"Error scanning {ticker}: {e}")

    results_df = pd.DataFrame(results).sort_values(by="Score", ascending=False)
    return results_df.head(5)

def build_html_dashboard(top_stocks):
    now = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p SGT")
    
    rows_html = ""
    for idx, row in top_stocks.iterrows():
        rows_html += f"""
        <tr>
            <td class="ticker"><strong>{row['Ticker']}</strong></td>
            <td>{row['Name']}</td>
            <td>{row['Price']}</td>
            <td><span class="badge yield">{row['Yield']}</span></td>
            <td><span class="badge surge">{row['VolSurge']}</span></td>
            <td>{row['RSI']}</td>
            <td><span class="badge score">{row['Score']} / 10</span></td>
        </tr>
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
            max-width: 900px;
            margin: 0 auto;
            background: #1e293b;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}
        h1 {{
            color: #38bdf8;
            margin-bottom: 5px;
        }}
        .timestamp {{
            color: #94a3b8;
            font-size: 0.9em;
            margin-bottom: 25px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }}
        th {{
            background-color: #0f172a;
            color: #38bdf8;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        tr:hover {{
            background-color: #334155;
        }}
        .ticker {{
            color: #f59e0b;
        }}
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .yield {{ background: #065f46; color: #34d399; }}
        .surge {{ background: #1e40af; color: #93c5fd; }}
        .score {{ background: #831843; color: #f472b6; }}
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
        <h1>🇸🇬 SGX Top 5 High-Conviction Picks</h1>
        <div class="timestamp">Last Updated: {now} | Target Execution: Monday Market Open</div>
        
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
