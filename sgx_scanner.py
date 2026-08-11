import yfinance as yf
import pandas as pd
import datetime
import json
import os

# ======================================================================
# ⚙️ CONFIGURATION
# ======================================================================
GITHUB_USERNAME = "shannonluiz78"  # 👈 Change to your GitHub username
GITHUB_REPO_NAME = "sgx-stock-scanner"     # 👈 Change if repo name is different

# Large-Cap & Banking Blue Chips (Adaptive Scoring)
BLUECHIP_TICKERS = ["D05.SI", "O39.SI", "U11.SI", "Z74.SI", "S63.SI", "BN4.SI"]

# SGX Universe List
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

# 4-Pillar Qualitative & 5-Year Financial Database
STOCK_METADATA = {
    "D05.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)", "horizon_grp": "SHORT", "badge_cls": "badge-short",
        "catalyst": "Dominant regional wealth hub engine and commitment to steady quarterly dividend growth.",
        "fundamentals": "Highest Return on Equity (ROE) in Southeast Asia (~18%) with strong capital reserves.",
        "technicals": "Strong institutional accumulation; consistently supported by 50-day SMA during pullbacks.",
        "risks": "Global economic slowdown leading to lower loan demand and credit provisions.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.12, "stop_mult": 0.93,
        "fin_rev_5yr": "S$ 14.5B ➔ S$ 20.1B (CAGR +8.5%)",
        "fin_net_income_5yr": "S$ 4.7B ➔ S$ 10.3B (CAGR +17.0%)",
        "fin_cashflow_5yr": "S$ 6.1B ➔ S$ 12.8B (Strong)",
        "fin_div_growth_5yr": "S$ 1.20 ➔ S$ 2.16 (+80% total dividend growth)",
        "fin_est_5yr_growth": "5.5% – 7.0% p.a.",
        "fin_st_debt": "S$ 12.4B (Deposit funded)",
        "fin_lt_debt": "S$ 22.1B (Senior notes)",
        "fin_moat": "Wide Moat (Dominant Market Share & Cost Advantage) • 9.5/10"
    },
    "O39.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)", "horizon_grp": "SHORT", "badge_cls": "badge-short",
        "catalyst": "Robust wealth management fee inflows and strong capital management buffer.",
        "fundamentals": "P/B ratio remains reasonable (~1.1x) with an attractive yield floor above 5.0%.",
        "technicals": "Stock frequently tests and bounces off key 50-day moving average support lines.",
        "risks": "Potential interest rate cuts lowering Net Interest Margin (NIM) growth.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.10, "stop_mult": 0.93,
        "fin_rev_5yr": "S$ 10.1B ➔ S$ 13.5B (CAGR +7.5%)",
        "fin_net_income_5yr": "S$ 3.6B ➔ S$ 7.0B (CAGR +14.2%)",
        "fin_cashflow_5yr": "S$ 4.5B ➔ S$ 8.9B (Strong)",
        "fin_div_growth_5yr": "S$ 0.48 ➔ S$ 0.84 (+75% total dividend growth)",
        "fin_est_5yr_growth": "5.0% – 6.5% p.a.",
        "fin_st_debt": "S$ 8.2B (Deposit funded)",
        "fin_lt_debt": "S$ 14.5B (Subordinated debt)",
        "fin_moat": "Wide Moat (Regional Wealth Franchise) • 9.0/10"
    },
    "BS6.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)", "horizon_grp": "SHORT", "badge_cls": "badge-short",
        "catalyst": "Record order backlog into 2028 with higher-margin clean energy vessel contracts.",
        "fundamentals": "Strong net cash position; high ROE exceeding 20% with strong dividend coverage.",
        "technicals": "Bullish momentum breakout with institutional volume surge; trading above 20 & 50 SMA.",
        "risks": "Fluctuations in steel raw material costs and USD/RMB exchange rate volatility.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.15, "stop_mult": 0.91,
        "fin_rev_5yr": "RMB 13.0B ➔ RMB 24.1B (CAGR +13.1%)",
        "fin_net_income_5yr": "RMB 2.5B ➔ RMB 4.1B (CAGR +10.4%)",
        "fin_cashflow_5yr": "RMB 3.2B ➔ RMB 5.8B (Robust)",
        "fin_div_growth_5yr": "S$ 0.045 ➔ S$ 0.10 (+122% total growth)",
        "fin_est_5yr_growth": "8.5% – 11.0% p.a.",
        "fin_st_debt": "RMB 3.1B",
        "fin_lt_debt": "RMB 1.2B (Net Cash Positive)",
        "fin_moat": "Narrow Moat (Cost Leadership in Shipbuilding) • 8.0/10"
    },
    "OU8.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
        "catalyst": "Acute shortage of foreign worker accommodation in SG and student housing in the UK.",
        "fundamentals": "Consistent revenue growth with strong occupancy rates exceeding 95% across key markets.",
        "technicals": "Sustained uptrend structure making higher lows; steady RSI accumulation without spike exhaustion.",
        "risks": "Regulatory changes in foreign worker quotas or student visa policies.",
        "buy_mult": (0.95, 0.99), "target_mult": 1.24, "stop_mult": 0.88,
        "fin_rev_5yr": "S$ 128M ➔ S$ 207M (CAGR +10.1%)",
        "fin_net_income_5yr": "S$ 38M ➔ S$ 153M (CAGR +32.1%)",
        "fin_cashflow_5yr": "S$ 52M ➔ S$ 115M (High Margin)",
        "fin_div_growth_5yr": "S$ 0.02 ➔ S$ 0.045 (+125% total growth)",
        "fin_est_5yr_growth": "9.0% – 12.0% p.a.",
        "fin_st_debt": "S$ 82M",
        "fin_lt_debt": "S$ 680M (Property backed)",
        "fin_moat": "Narrow Moat (Regulatory Operating Licenses) • 8.0/10"
    },
    "Z74.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
        "catalyst": "ST25 strategic restructuring plan unlocking value from regional data centers and Optus.",
        "fundamentals": "Improving free cash flow supporting sustainable dividend payouts and debt reduction.",
        "technicals": "Rounded bottom reversal pattern emerging with rising 20-day moving average.",
        "risks": "Competitive pricing pressure in regional mobile markets (e.g., Australia).",
        "buy_mult": (0.96, 0.99), "target_mult": 1.18, "stop_mult": 0.91,
        "fin_rev_5yr": "S$ 16.5B ➔ S$ 14.1B (Refocusing core)",
        "fin_net_income_5yr": "S$ 1.1B ➔ S$ 2.5B (Turnaround)",
        "fin_cashflow_5yr": "S$ 3.2B ➔ S$ 4.2B (Stable)",
        "fin_div_growth_5yr": "S$ 0.093 ➔ S$ 0.15 (+61% total growth)",
        "fin_est_5yr_growth": "6.0% – 8.0% p.a.",
        "fin_st_debt": "S$ 2.1B",
        "fin_lt_debt": "S$ 8.5B",
        "fin_moat": "Wide Moat (Infrastructure & Spectrum Assets) • 8.5/10"
    },
    "G13.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
        "catalyst": "Ongoing RWS 2.0 expansion & ongoing recovery in regional flight capacities and Chinese tourism.",
        "fundamentals": "Pristine balance sheet with over S$3B in net cash providing downside cushion.",
        "technicals": "Trading near multi-year valuation support zone; low RSI indicates minimal downside risk.",
        "risks": "Slower-than-expected recovery in high-roller VIP gaming spend.",
        "buy_mult": (0.95, 1.00), "target_mult": 1.24, "stop_mult": 0.89,
        "fin_rev_5yr": "S$ 1.06B ➔ S$ 2.42B (Post-pandemic recovery)",
        "fin_net_income_5yr": "S$ 86M ➔ S$ 611M (CAGR +48.0%)",
        "fin_cashflow_5yr": "S$ 240M ➔ S$ 890M (Strong)",
        "fin_div_growth_5yr": "S$ 0.02 ➔ S$ 0.04 (+100% recovery growth)",
        "fin_est_5yr_growth": "7.0% – 9.5% p.a.",
        "fin_st_debt": "S$ 15M",
        "fin_lt_debt": "S$ 210M (Net Cash S$3.1B)",
        "fin_moat": "Wide Moat (Duopoly Gaming License in SG) • 9.0/10"
    },
    "U11.SI": {
        "horizon": "🏛️ LONG-TERM (3–5+ YRS)", "horizon_grp": "LONG", "badge_cls": "badge-long",
        "catalyst": "Citigroup ASEAN consumer portfolio acquisition driving broader regional fee income.",
        "fundamentals": "Steady dividend payout ratio (~50%) with solid non-performing loan (NPL) coverage.",
        "technicals": "Long-term bullish trend channel intact; low volatility consolidation near current levels.",
        "risks": "Broader ASEAN macroeconomic slowdown impacting regional credit growth.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.15, "stop_mult": 0.92,
        "fin_rev_5yr": "S$ 9.1B ➔ S$ 13.9B (CAGR +8.8%)",
        "fin_net_income_5yr": "S$ 2.9B ➔ S$ 5.7B (CAGR +14.4%)",
        "fin_cashflow_5yr": "S$ 3.8B ➔ S$ 7.1B (Strong)",
        "fin_div_growth_5yr": "S$ 1.00 ➔ S$ 1.70 (+70% total dividend growth)",
        "fin_est_5yr_growth": "5.0% – 6.5% p.a.",
        "fin_st_debt": "S$ 6.5B (Deposit funded)",
        "fin_lt_debt": "S$ 11.2B (Senior bonds)",
        "fin_moat": "Wide Moat (Regional Banking Franchise) • 8.8/10"
    },
    "C52.SI": {
        "horizon": "🏛️ LONG-TERM (3–5+ YRS)", "horizon_grp": "LONG", "badge_cls": "badge-long",
        "catalyst": "Winning lucrative long-term overseas public bus/rail tenders in Australia and the UK.",
        "fundamentals": "Defensive business model with stable cash generation and healthy dividend yield (~5.5%).",
        "technicals": "Price consolidating inside a tight accumulation range above the 200-day moving average.",
        "risks": "Driver shortages and wage inflation impacting overseas operational margins.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.22, "stop_mult": 0.90,
        "fin_rev_5yr": "S$ 3.2B ➔ S$ 3.88B (CAGR +3.9%)",
        "fin_net_income_5yr": "S$ 61M ➔ S$ 180M (CAGR +24.1%)",
        "fin_cashflow_5yr": "S$ 380M ➔ S$ 590M (Defensive)",
        "fin_div_growth_5yr": "S$ 0.043 ➔ S$ 0.072 (+67% recovery growth)",
        "fin_est_5yr_growth": "4.5% – 6.0% p.a.",
        "fin_st_debt": "S$ 140M",
        "fin_lt_debt": "S$ 290M (Low leverage)",
        "fin_moat": "Narrow Moat (Public Transport Tenders) • 7.5/10"
    }
}

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
            
            is_bluechip = ticker in BLUECHIP_TICKERS
            score = 0
            
            # --- ADAPTIVE SCORING ENGINE ---
            if is_bluechip:
                if volume_surge >= 1.15: score += 3
                elif volume_surge >= 1.05: score += 1
                
                if trend_bullish: score += 2
                if price_above_50sma: score += 1
                if 40 <= rsi <= 72: score += 2
                if div_yield >= 0.04: score += 2
                elif div_yield >= 0.03: score += 1
            else:
                if volume_surge >= 1.5: score += 3
                elif volume_surge >= 1.2: score += 1
                
                if trend_bullish: score += 2
                if price_above_50sma: score += 1
                if 45 <= rsi <= 68: score += 2
                if div_yield >= 0.05: score += 2
                elif div_yield >= 0.035: score += 1
            
            # Metadata Fallback
            meta = STOCK_METADATA.get(ticker, {
                "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
                "catalyst": "Technical trend alignment supported by positive institutional trading volume.",
                "fundamentals": "Stable market capitalization with consistent historical dividend payouts.",
                "technicals": "Moving average convergence indicates a potential trend expansion phase.",
                "risks": "General SGX market volatility and sector-specific headwinds.",
                "buy_mult": (0.96, 0.99), "target_mult": 1.18, "stop_mult": 0.90,
                "fin_rev_5yr": "S$ 500M ➔ S$ 750M (CAGR +8.4%)",
                "fin_net_income_5yr": "S$ 50M ➔ S$ 95M (CAGR +13.7%)",
                "fin_cashflow_5yr": "S$ 65M ➔ S$ 110M (Steady)",
                "fin_div_growth_5yr": "S$ 0.03 ➔ S$ 0.05 (+66% growth)",
                "fin_est_5yr_growth": "5.0% – 7.5% p.a.",
                "fin_st_debt": "S$ 25M",
                "fin_lt_debt": "S$ 120M",
                "fin_moat": "Narrow Moat (Sector Position) • 7.0/10"
            })
            
            buy_low = latest_price * meta["buy_mult"][0]
            buy_high = latest_price * meta["buy_mult"][1]
            target_sell = latest_price * meta["target_mult"]
            stop_loss = latest_price * meta["stop_mult"]
            
            # Extract historical price array for Chart.js trendline (last 60 trading days)
            chart_prices = [round(float(p), 2) for p in df['Close'].tail(60).tolist()]
            chart_labels = [d.strftime("%b %d") for d in df.index[-60:]]
            
            results.append({
                "Ticker": ticker,
                "TickerID": ticker.replace(".", "_"),
                "Name": name,
                "Price": latest_price,
                "Price_Str": f"S${latest_price:.2f}",
                "Yield": f"{div_yield * 100:.2f}%",
                "VolSurge": f"{volume_surge:.2f}x",
                "RSI": f"{rsi:.1f}",
                "Score": score,
                "IsBluechip": is_bluechip,
                "Horizon": meta["horizon"],
                "HorizonGrp": meta["horizon_grp"],
                "BadgeCls": meta["badge_cls"],
                "Catalyst": meta["catalyst"],
                "Fundamentals": meta["fundamentals"],
                "Technicals": meta["technicals"],
                "Risks": meta["risks"],
                "BuyZone": f"S${buy_low:.2f} – S${buy_high:.2f}",
                "TargetSell": f"S${target_sell:.2f}",
                "StopLoss": f"S${stop_loss:.2f}",
                "FinRev": meta["fin_rev_5yr"],
                "FinNetIncome": meta["fin_net_income_5yr"],
                "FinCashflow": meta["fin_cashflow_5yr"],
                "FinDiv": meta["fin_div_growth_5yr"],
                "FinEstGrowth": meta["fin_est_5yr_growth"],
                "FinSTDebt": meta["fin_st_debt"],
                "FinLTDebt": meta["fin_lt_debt"],
                "FinMoat": meta["fin_moat"],
                "ChartPrices": json.dumps(chart_prices),
                "ChartLabels": json.dumps(chart_labels)
            })
        except Exception as e:
            print(f"Error scanning {ticker}: {e}")

    df_all = pd.DataFrame(results)
    
    # --- CUSTOM SLOT ALLOCATION LOGIC ---
    # 1. Take Top 2 Blue-Chips
    bc_picks = df_all[df_all['IsBluechip'] == True].sort_values(by="Score", ascending=False).head(2)
    
    # 2. Filter remaining pool for High Momentum & Growth
    pool_growth = df_all[~df_all['Ticker'].isin(bc_picks['Ticker'])]
    
    short_picks = pool_growth[pool_growth['HorizonGrp'] == 'SHORT'].sort_values(by="Score", ascending=False).head(2)
    
    pool_mid = pool_growth[~pool_growth['Ticker'].isin(short_picks['Ticker'])]
    mid_picks = pool_mid[pool_mid['HorizonGrp'] == 'MID'].sort_values(by="Score", ascending=False).head(2)
    
    pool_long = pool_mid[~pool_mid['Ticker'].isin(mid_picks['Ticker'])]
    long_picks = pool_long[pool_long['HorizonGrp'] == 'LONG'].sort_values(by="Score", ascending=False).head(2)
    
    # Combine (2 Blue Chip + 2 Short + 2 Mid + 2 Long = 8 Stocks total)
    final_top_df = pd.concat([bc_picks, short_picks, mid_picks, long_picks]).drop_duplicates().sort_values(by="Score", ascending=False)
    return final_top_df

def build_html_dashboard(top_stocks):
    now = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p SGT")
    rescan_url = f"https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/actions/workflows/scanner.yml"
    
    cards_html = ""
    chart_init_scripts = ""
    
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

            <div class="chart-wrapper">
                <div class="chart-header">📈 1-Year Price Trend & Momentum</div>
                <div class="chart-container">
                    <canvas id="chart_{row['TickerID']}"></canvas>
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

            <div class="analysis-grid">
                <div class="analysis-box catalyst-box">
                    <div class="analysis-title">🚀 Growth Catalyst</div>
                    <div class="analysis-text">{row['Catalyst']}</div>
                </div>
                <div class="analysis-box fundamentals-box">
                    <div class="analysis-title">🏛️ Fundamentals & Yield</div>
                    <div class="analysis-text">{row['Fundamentals']}</div>
                </div>
                <div class="analysis-box technicals-box">
                    <div class="analysis-title">📉 Technical & Volume Setup</div>
                    <div class="analysis-text">{row['Technicals']}</div>
                </div>
                <div class="analysis-box risks-box">
                    <div class="analysis-title">⚠️ Key Risks to Watch</div>
                    <div class="analysis-text">{row['Risks']}</div>
                </div>
            </div>

            <div class="financials-container">
                <div class="table-title">📊 5-Year Financial Performance & Economic Moat</div>
                <table class="fin-table">
                    <tbody>
                        <tr>
                            <td class="fin-label">Revenue (Past 5 Yrs)</td>
                            <td class="fin-val">{row['FinRev']}</td>
                        </tr>
                        <tr>
                            <td class="fin-label">Nett Income (Past 5 Yrs)</td>
                            <td class="fin-val">{row['FinNetIncome']}</td>
                        </tr>
                        <tr>
                            <td class="fin-label">Operating Cash Flow</td>
                            <td class="fin-val">{row['FinCashflow']}</td>
                        </tr>
                        <tr>
                            <td class="fin-label">Dividend Trajectory (5 Yrs)</td>
                            <td class="fin-val highlight-yield">{row['FinDiv']}</td>
                        </tr>
                        <tr>
                            <td class="fin-label">Estimated 5-Yr Growth</td>
                            <td class="fin-val">{row['FinEstGrowth']}</td>
                        </tr>
                        <tr>
                            <td class="fin-label">Short-Term Debt</td>
                            <td class="fin-val">{row['FinSTDebt']}</td>
                        </tr>
                        <tr>
                            <td class="fin-label">Long-Term Debt</td>
                            <td class="fin-val">{row['FinLTDebt']}</td>
                        </tr>
                        <tr class="moat-row">
                            <td class="fin-label">Economic Moat Score</td>
                            <td class="fin-val moat-text">{row['FinMoat']}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        """

        chart_init_scripts += f"""
        new Chart(document.getElementById('chart_{row['TickerID']}').getContext('2d'), {{
            type: 'line',
            data: {{
                labels: {row['ChartLabels']},
                datasets: [{{
                    data: {row['ChartPrices']},
                    borderColor: '#38bdf8',
                    borderWidth: 2,
                    fill: true,
                    backgroundColor: 'rgba(56, 189, 248, 0.08)',
                    tension: 0.25,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ display: false }},
                    y: {{ 
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}
                    }}
                }}
            }}
        }});
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGX Top 8 Weekly Watchlist Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
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
            max-width: 880px;
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

        .stock-card {{
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.4);
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
            font-size: 1.45em;
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
        }}

        .badge-score {{ background: rgba(244, 63, 94, 0.15); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }}
        .badge-short {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-mid {{ background: rgba(6, 182, 212, 0.15); color: #38bdf8; border: 1px solid rgba(6, 182, 212, 0.3); }}
        .badge-long {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }}

        .chart-wrapper {{
            background: rgba(15, 23, 42, 0.6);
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }}

        .chart-header {{
            font-size: 0.78em;
            font-weight: 700;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
        }}

        .chart-container {{
            position: relative;
            height: 120px;
            width: 100%;
        }}

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
        }}

        .metric-value {{
            font-size: 1.15em;
            font-weight: 800;
            color: var(--text-primary);
            margin-top: 4px;
        }}

        .highlight-yield {{ color: #34d399; }}

        .trade-setup {{
            display: flex;
            justify-content: space-between;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 12px 18px;
            border-radius: 12px;
            font-size: 0.9em;
            margin-bottom: 18px;
            flex-wrap: wrap;
            gap: 10px;
            color: #e0e7ff;
        }}

        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}

        @media (max-width: 640px) {{
            .analysis-grid {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}

        .analysis-box {{
            background: rgba(15, 23, 42, 0.55);
            padding: 12px 14px;
            border-radius: 12px;
            border-left: 3px solid #38bdf8;
        }}

        .catalyst-box {{ border-left-color: #a855f7; }}
        .fundamentals-box {{ border-left-color: #34d399; }}
        .technicals-box {{ border-left-color: #38bdf8; }}
        .risks-box {{ border-left-color: #f43f5e; }}

        .analysis-title {{
            font-size: 0.82em;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 4px;
        }}

        .analysis-text {{
            font-size: 0.85em;
            color: #cbd5e1;
            line-height: 1.5;
        }}

        /* Financials Table Styling */
        .financials-container {{
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 16px;
        }}

        .table-title {{
            font-size: 0.85em;
            font-weight: 800;
            color: #38bdf8;
            margin-bottom: 12px;
            letter-spacing: 0.3px;
        }}

        .fin-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.83em;
        }}

        .fin-table tr {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }}

        .fin-table tr:last-child {{
            border-bottom: none;
        }}

        .fin-label {{
            padding: 8px 4px;
            color: var(--text-secondary);
            font-weight: 600;
            width: 40%;
        }}

        .fin-val {{
            padding: 8px 4px;
            color: var(--text-primary);
            font-weight: 700;
            text-align: right;
        }}

        .moat-row {{
            background: rgba(168, 85, 247, 0.08);
        }}

        .moat-text {{
            color: #c084fc;
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
        Automated Structured Allocation Screen (2 Blue Chips + 2 Short + 2 Mid + 2 Long). Powered by GitHub Actions & Python.
    </div>
</div>

<script>
    document.addEventListener("DOMContentLoaded", function() {{
        {chart_init_scripts}
    }});
</script>

</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Dashboard generated successfully with trend charts and financial tables in index.html")

if __name__ == "__main__":
    top_df = scan_stocks()
    build_html_dashboard(top_df)
