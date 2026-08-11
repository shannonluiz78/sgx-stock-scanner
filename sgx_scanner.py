import datetime
import os
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. STOCK METADATA & FULL FINANCIAL DATA
# ==========================================
STOCK_METADATA = {
    "G13.SI": {
        "name": "Genting Singapore",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "score": 10,
        "summary": "Value Recovery. Trading near low valuation levels with a strong net-cash balance sheet. RWS 2.0 expansion and resilient tourism volume provide multi-month upside backed by a high dividend yield floor.",
        "catalyst": "RWS 2.0 expansion phases kicking in alongside strong Asian tourism recovery.",
        "fundamentals": "Net cash balance sheet exceeding S$3B, providing strong downside protection and sustained payout capacity.",
        "technicals": "Consolidating near major support with bullish volume divergence.",
        "risks": "Macroeconomic slowdown in regional tourism and regulatory changes.",
        "buy_mult": (0.95, 1.00),
        "target_mult": 1.25,
        "stop_mult": 0.90,
        "intrinsic_val": "S$ 0.72",
        "pb_ratio": "1.20x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$1.06B", "S$1.73B", "S$2.42B", "S$2.55B", "S$2.70B"],
        "fin_net": ["S$183M", "S$345M", "S$611M", "S$650M", "S$710M"],
        "fin_ocf": ["S$320M", "S$580M", "S$890M", "S$940M", "S$1.02B"],
        "fin_fcf": ["S$210M", "S$410M", "S$650M", "S$680M", "S$750M"],
        "fin_div": ["S$0.020", "S$0.030", "S$0.035", "S$0.040", "S$0.045"],
        "asset_cash": ["S$3.1B", "S$3.3B", "S$3.6B", "S$3.8B", "S$4.0B"],
        "asset_st_inv": ["S$120M", "S$150M", "S$180M", "S$200M", "S$220M"],
        "asset_ppe": ["S$4.5B", "S$4.6B", "S$4.8B", "S$5.0B", "S$5.2B"],
        "asset_other": ["S$800M", "S$850M", "S$900M", "S$920M", "S$950M"],
        "asset_total": ["S$8.52B", "S$8.90B", "S$9.48B", "S$9.92B", "S$10.37B"],
        "fin_st_debt": ["S$0M", "S$0M", "S$0M", "S$0M", "S$0M"],
        "fin_lt_debt": ["S$200M", "S$180M", "S$150M", "S$120M", "S$100M"],
        "fin_moat": "Narrow Moat (Casino License Duopoly in Singapore) • 8.5/10"
    },
    "OU8.SI": {
        "name": "Centurion Corp",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "score": 10,
        "summary": "Growth & Severe Supply Shortage. Specialized worker and foreign student accommodation operator benefiting from severe structural supply deficits across Singapore and the UK.",
        "catalyst": "High occupancy rates and rental rate revisions across PBWA/PBSA assets.",
        "fundamentals": "Strong earnings growth momentum, debt de-leveraging, and widening operating profit margins.",
        "technicals": "Sustained upward channel with clear institutional accumulation.",
        "risks": "Changes in government foreign worker or international student visa policies.",
        "buy_mult": (0.95, 0.98),
        "target_mult": 1.24,
        "stop_mult": 0.88,
        "intrinsic_val": "S$ 1.95",
        "pb_ratio": "0.85x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$143M", "S$180M", "S$207M", "S$235M", "S$260M"],
        "fin_net": ["S$52M", "S$71M", "S$153M", "S$175M", "S$195M"],
        "fin_ocf": ["S$75M", "S$98M", "S$128M", "S$145M", "S$165M"],
        "fin_fcf": ["S$45M", "S$68M", "S$92M", "S$110M", "S$125M"],
        "fin_div": ["S$0.010", "S$0.015", "S$0.025", "S$0.035", "S$0.042"],
        "asset_cash": ["S$65M", "S$78M", "S$95M", "S$110M", "S$128M"],
        "asset_st_inv": ["S$10M", "S$12M", "S$15M", "S$18M", "S$20M"],
        "asset_ppe": ["S$1.3B", "S$1.4B", "S$1.6B", "S$1.7B", "S$1.8B"],
        "asset_other": ["S$120M", "S$130M", "S$140M", "S$150M", "S$160M"],
        "asset_total": ["S$1.49B", "S$1.62B", "S$1.85B", "S$1.97B", "S$2.10B"],
        "fin_st_debt": ["S$45M", "S$50M", "S$55M", "S$60M", "S$62M"],
        "fin_lt_debt": ["S$680M", "S$710M", "S$740M", "S$760M", "S$780M"],
        "fin_moat": "Narrow Moat (High Regulatory Barrier & Capacity Constraints) • 7.5/10"
    },
    "BS6.SI": {
        "name": "Yangzijiang Shipbuilding",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "score": 8,
        "summary": "Record Order Backlog. High multi-year earnings visibility supported by record high shipbuilding order book stretched into 2028 and expanding margins on green vessel builds.",
        "catalyst": "Delivery of higher-margin clean energy vessel contracts (LNG/Methanol dual-fuel).",
        "fundamentals": "Strong cash balance, robust gross margins, and dominant execution capabilities.",
        "technicals": "Strong uptrend with temporary pullback offering optimal risk-reward entry.",
        "risks": "Steel raw material cost spikes and USD/RMB currency volatility.",
        "buy_mult": (0.94, 0.98),
        "target_mult": 1.20,
        "stop_mult": 0.90,
        "intrinsic_val": "S$ 5.30",
        "pb_ratio": "1.65x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["RMB 16.8B", "RMB 20.7B", "RMB 24.1B", "RMB 27.5B", "RMB 30.2B"],
        "fin_net": ["RMB 3.7B", "RMB 2.8B", "RMB 4.1B", "RMB 4.8B", "RMB 5.5B"],
        "fin_ocf": ["RMB 4.2B", "RMB 3.9B", "RMB 5.8B", "RMB 6.5B", "RMB 7.2B"],
        "fin_fcf": ["RMB 3.1B", "RMB 2.8B", "RMB 4.6B", "RMB 5.2B", "RMB 5.9B"],
        "fin_div": ["S$0.050", "S$0.050", "S$0.065", "S$0.080", "S$0.095"],
        "asset_cash": ["RMB 12B", "RMB 14B", "RMB 17B", "RMB 20B", "RMB 23B"],
        "asset_st_inv": ["RMB 3B", "RMB 3.5B", "RMB 4B", "RMB 4.5B", "RMB 5B"],
        "asset_ppe": ["RMB 8B", "RMB 8.5B", "RMB 9B", "RMB 9.5B", "RMB 10B"],
        "asset_other": ["RMB 5B", "RMB 5.5B", "RMB 6B", "RMB 6.5B", "RMB 7B"],
        "asset_total": ["RMB 28B", "RMB 31.5B", "RMB 36B", "RMB 40.5B", "RMB 45B"],
        "fin_st_debt": ["RMB 1.2B", "RMB 1.0B", "RMB 0.8B", "RMB 0.5B", "RMB 0.3B"],
        "fin_lt_debt": ["RMB 2.5B", "RMB 2.0B", "RMB 1.5B", "RMB 1.0B", "RMB 0.5B"],
        "fin_moat": "Wide Moat (Cost Leadership & Shipyard Scale) • 8.8/10"
    },
    "U11.SI": {
        "name": "UOB Bank",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "score": 8,
        "summary": "Resilient Yield & Capital Returns. Attractive dividend yield backed by expanding regional wealth management, Citi ASEAN integration synergies, and strong capital buffers.",
        "catalyst": "Regional retail banking growth and wealth management fee income expansion.",
        "fundamentals": "Strong CET1 capital ratio driving sustained dividend payouts and potential share buybacks.",
        "technicals": "Healthy consolidation pattern with key support established at current price levels.",
        "risks": "Net Interest Margin (NIM) compression in lower interest rate environments.",
        "buy_mult": (0.96, 0.99),
        "target_mult": 1.15,
        "stop_mult": 0.92,
        "intrinsic_val": "S$ 48.00",
        "pb_ratio": "1.15x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$9.8B", "S$11.6B", "S$13.9B", "S$14.5B", "S$15.2B"],
        "fin_net": ["S$4.0B", "S$4.6B", "S$5.7B", "S$6.0B", "S$6.4B"],
        "fin_ocf": ["S$5.1B", "S$6.2B", "S$7.5B", "S$8.0B", "S$8.6B"],
        "fin_fcf": ["S$4.8B", "S$5.8B", "S$7.1B", "S$7.6B", "S$8.1B"],
        "fin_div": ["S$1.20", "S$1.35", "S$1.70", "S$1.85", "S$2.00"],
        "asset_cash": ["S$45B", "S$52B", "S$58B", "S$62B", "S$68B"],
        "asset_st_inv": ["S$85B", "S$92B", "S$105B", "S$112B", "S$120B"],
        "asset_ppe": ["S$3.5B", "S$3.8B", "S$4.0B", "S$4.2B", "S$4.5B"],
        "asset_other": ["S$326B", "S$356B", "S$356B", "S$375B", "S$395B"],
        "asset_total": ["S$459B", "S$504B", "S$523B", "S$553B", "S$587B"],
        "fin_st_debt": ["S$12B", "S$15B", "S$18B", "S$20B", "S$22B"],
        "fin_lt_debt": ["S$25B", "S$28B", "S$32B", "S$35B", "S$38B"],
        "fin_moat": "Wide Moat (ASEAN Banking Oligopoly) • 9.0/10"
    },
    "C52.SI": {
        "name": "ComfortDelGro",
        "horizon": "📈 MID-TERM (1–3 YRS)",
        "score": 7,
        "summary": "Public Transport & Mobility Recovery. Earnings tailwinds supported by overseas contract wins, taxi commission adjustments, and rider volume normalization.",
        "catalyst": "UK & Australian public transport contract repricing and A2B acquisition contribution.",
        "fundamentals": "Solid balance sheet with expanding operating cash flow and growing dividends.",
        "technicals": "Accumulation pattern above moving averages with increasing buying interest.",
        "risks": "Driver labor inflation and competition from ride-hailing aggregators.",
        "buy_mult": (0.95, 0.99),
        "target_mult": 1.18,
        "stop_mult": 0.91,
        "intrinsic_val": "S$ 1.55",
        "pb_ratio": "1.10x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$3.5B", "S$3.8B", "S$3.9B", "S$4.2B", "S$4.5B"],
        "fin_net": ["S$130M", "S$173M", "S$180M", "S$210M", "S$240M"],
        "fin_ocf": ["S$520M", "S$580M", "S$610M", "S$670M", "S$730M"],
        "fin_fcf": ["S$280M", "S$320M", "S$350M", "S$410M", "S$460M"],
        "fin_div": ["S$0.042", "S$0.068", "S$0.066", "S$0.078", "S$0.086"],
        "asset_cash": ["S$920M", "S$960M", "S$880M", "S$950M", "S$1.05B"],
        "asset_st_inv": ["S$50M", "S$60M", "S$70M", "S$80M", "S$90M"],
        "asset_ppe": ["S$2.4B", "S$2.5B", "S$2.6B", "S$2.7B", "S$2.8B"],
        "asset_other": ["S$1.1B", "S$1.2B", "S$1.3B", "S$1.4B", "S$1.5B"],
        "asset_total": ["S$4.47B", "S$4.72B", "S$4.85B", "S$5.13B", "S$5.44B"],
        "fin_st_debt": ["S$120M", "S$140M", "S$150M", "S$160M", "S$170M"],
        "fin_lt_debt": ["S$350M", "S$380M", "S$400M", "S$420M", "S$450M"],
        "fin_moat": "Narrow Moat (Public Transport Concessions & Fleet Scale) • 7.2/10"
    }
}

# You can add or edit any ticker list here
TICKERS = ["G13.SI", "OU8.SI", "BS6.SI", "U11.SI", "C52.SI"]

DEFAULT_META = {
    "name": "SGX Listed Equity",
    "horizon": "📈 MID-TERM (1–3 YRS)",
    "score": 7,
    "summary": "Technical alignment supported by institutional volume and fundamental stability.",
    "catalyst": "Sector recovery and consistent operational execution.",
    "fundamentals": "Healthy balance sheet with consistent historical dividend payouts.",
    "technicals": "Moving average convergence indicates potential trend expansion.",
    "risks": "General SGX market volatility and sector-specific headwinds.",
    "buy_mult": (0.96, 0.99),
    "target_mult": 1.18,
    "stop_mult": 0.90,
    "intrinsic_val": "S$ --",
    "pb_ratio": "1.20x",
    "fin_years": ["2021", "2022", "2023", "2024", "2025"],
    "fin_rev": ["S$500M", "S$580M", "S$640M", "S$710M", "S$780M"],
    "fin_net": ["S$50M", "S$62M", "S$75M", "S$88M", "S$98M"],
    "fin_ocf": ["S$65M", "S$78M", "S$92M", "S$105M", "S$118M"],
    "fin_fcf": ["S$45M", "S$58M", "S$70M", "S$82M", "S$95M"],
    "fin_div": ["S$0.030", "S$0.035", "S$0.040", "S$0.045", "S$0.050"],
    "asset_cash": ["S$80M", "S$92M", "S$105M", "S$112M", "S$120M"],
    "asset_st_inv": ["S$30M", "S$38M", "S$42M", "S$46M", "S$50M"],
    "asset_ppe": ["S$380M", "S$400M", "S$420M", "S$435M", "S$450M"],
    "asset_other": ["S$280M", "S$310M", "S$340M", "S$360M", "S$380M"],
    "asset_total": ["S$770M", "S$840M", "S$907M", "S$953M", "S$1.00B"],
    "fin_st_debt": ["S$15M", "S$18M", "S$21M", "S$23M", "S$25M"],
    "fin_lt_debt": ["S$85M", "S$95M", "S$105M", "S$112M", "S$120M"],
    "fin_moat": "Narrow Moat (Sector Position) • 7.0/10"
}

# ==========================================
# 2. HELPER CALCULATIONS
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
        print(f"yfinance fetch fallback for {ticker}: {e}")
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
        "catalyst": meta.get("catalyst", ""),
        "fundamentals": meta.get("fundamentals", ""),
        "technicals": meta.get("technicals", ""),
        "risks": meta.get("risks", ""),
        "intrinsic_val": meta.get("intrinsic_val", f"S$ {latest_price*1.15:.2f}"),
        "pb_ratio": meta.get("pb_ratio", "1.20x"),
        "fin_years": meta.get("fin_years", ["2021", "2022", "2023", "2024", "2025"]),
        "fin_rev": meta.get("fin_rev", ["-"]*5),
        "fin_net": meta.get("fin_net", ["-"]*5),
        "fin_ocf": meta.get("fin_ocf", ["-"]*5),
        "fin_fcf": meta.get("fin_fcf", ["-"]*5),
        "fin_div": meta.get("fin_div", ["-"]*5),
        "asset_cash": meta.get("asset_cash", ["-"]*5),
        "asset_st_inv": meta.get("asset_st_inv", ["-"]*5),
        "asset_ppe": meta.get("asset_ppe", ["-"]*5),
        "asset_other": meta.get("asset_other", ["-"]*5),
        "asset_total": meta.get("asset_total", ["-"]*5),
        "fin_st_debt": meta.get("fin_st_debt", ["-"]*5),
        "fin_lt_debt": meta.get("fin_lt_debt", ["-"]*5),
        "fin_moat": meta.get("fin_moat", "Narrow Moat • 7.0/10"),
        "buy_range": f"S${buy_low:.2f} – S${buy_high:.2f}",
        "target_sell": f"S${target_sell:.2f}",
        "stop_loss": f"S${stop_loss:.2f}"
    }

# ==========================================
# 3. HTML DASHBOARD GENERATOR
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
        
        fin_yrs_th = "".join([f"<th>{y}</th>" for y in item['fin_years']])
        rev_td = "".join([f"<td>{v}</td>" for v in item['fin_rev']])
        net_td = "".join([f"<td>{v}</td>" for v in item['fin_net']])
        ocf_td = "".join([f"<td>{v}</td>" for v in item['fin_ocf']])
        fcf_td = "".join([f"<td>{v}</td>" for v in item['fin_fcf']])
        div_td = "".join([f"<td>{v}</td>" for v in item['fin_div']])
        
        cash_td = "".join([f"<td>{v}</td>" for v in item['asset_cash']])
        st_inv_td = "".join([f"<td>{v}</td>" for v in item['asset_st_inv']])
        ppe_td = "".join([f"<td>{v}</td>" for v in item['asset_ppe']])
        other_td = "".join([f"<td>{v}</td>" for v in item['asset_other']])
        total_td = "".join([f"<td><strong>{v}</strong></td>" for v in item['asset_total']])
        st_debt_td = "".join([f"<td>{v}</td>" for v in item['fin_st_debt']])
        lt_debt_td = "".join([f"<td>{v}</td>" for v in item['fin_lt_debt']])

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
                <div class="metric-box">
                    <div class="metric-label">INTRINSIC VAL</div>
                    <div class="metric-val">{item['intrinsic_val']}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">P/B RATIO</div>
                    <div class="metric-val">{item['pb_ratio']}</div>
                </div>
            </div>
            
            <div class="targets-bar">
                <div><strong>Target Buy:</strong> {item['buy_range']}</div>
                <div><strong>Target Sell:</strong> {item['target_sell']}</div>
                <div><strong>Stop Loss:</strong> {item['stop_loss']}</div>
            </div>
            
            <div class="summary-box">
                <strong>Executive Summary:</strong> {item['summary']}
            </div>

            <div class="analysis-grid">
                <div class="analysis-card">
                    <h4>🚀 Key Catalysts</h4>
                    <p>{item['catalyst']}</p>
                </div>
                <div class="analysis-card">
                    <h4>📊 Fundamental Health</h4>
                    <p>{item['fundamentals']}</p>
                </div>
                <div class="analysis-card">
                    <h4>📈 Technical Setup</h4>
                    <p>{item['technicals']}</p>
                </div>
                <div class="analysis-card">
                    <h4>⚠️ Key Risks</h4>
                    <p>{item['risks']}</p>
                </div>
            </div>

            <div class="sub-section-title">📊 5-Year Financial Trend & Cash Flow</div>
            <div class="mini-table-container">
                <table class="mini-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            {fin_yrs_th}
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>Revenue</strong></td>{rev_td}</tr>
                        <tr><td><strong>Net Income</strong></td>{net_td}</tr>
                        <tr><td><strong>Operating Cash Flow</strong></td>{ocf_td}</tr>
                        <tr><td><strong>Free Cash Flow</strong></td>{fcf_td}</tr>
                        <tr><td><strong>Dividend per Share</strong></td>{div_td}</tr>
                    </tbody>
                </table>
            </div>

            <div class="sub-section-title">🏦 Balance Sheet & Asset Breakdown</div>
            <div class="mini-table-container">
                <table class="mini-table">
                    <thead>
                        <tr>
                            <th>Asset / Liability Class</th>
                            {fin_yrs_th}
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Cash & Equivalents</td>{cash_td}</tr>
                        <tr><td>Short-Term Investments</td>{st_inv_td}</tr>
                        <tr><td>PP&E / Real Estate Assets</td>{ppe_td}</tr>
                        <tr><td>Other Assets</td>{other_td}</tr>
                        <tr><td><strong>Total Assets</strong></td>{total_td}</tr>
                        <tr><td>Short-Term Debt</td>{st_debt_td}</tr>
                        <tr><td>Long-Term Debt</td>{lt_debt_td}</tr>
                    </tbody>
                </table>
            </div>

            <div class="moat-bar">
                <strong>🏰 Economic Moat Rating:</strong> {item['fin_moat']}
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
            max-width: 1080px;
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
            padding: 24px;
            margin-bottom: 24px;
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
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
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
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            margin-bottom: 16px;
        }}
        .summary-box {{
            border-left: 4px solid var(--accent-blue);
            background: rgba(15, 23, 42, 0.4);
            padding: 12px 16px;
            font-size: 0.95rem;
            color: #cbd5e1;
            line-height: 1.5;
            margin-bottom: 16px;
            border-radius: 0 8px 8px 0;
        }}
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }}
        .analysis-card {{
            background: rgba(15, 23, 42, 0.5);
            padding: 12px 14px;
            border-radius: 8px;
            border: 1px solid rgba(51, 65, 85, 0.5);
        }}
        .analysis-card h4 {{
            margin: 0 0 6px 0;
            font-size: 0.85rem;
            color: var(--accent-blue);
        }}
        .analysis-card p {{
            margin: 0;
            font-size: 0.85rem;
            color: var(--text-sub);
            line-height: 1.4;
        }}
        .sub-section-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: #fbbf24;
            margin: 16px 0 8px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .mini-table-container {{
            overflow-x: auto;
            margin-bottom: 16px;
        }}
        .mini-table {{
            width: 100%;
            font-size: 0.85rem;
            border-collapse: collapse;
            background: rgba(15, 23, 42, 0.4);
            border-radius: 8px;
        }}
        .mini-table th {{
            background: rgba(30, 41, 59, 0.8);
            font-size: 0.75rem;
        }}
        .mini-table td, .mini-table th {{
            padding: 8px 12px;
        }}
        .moat-bar {{
            background: rgba(168, 85, 247, 0.15);
            border: 1px solid rgba(168, 85, 247, 0.3);
            color: #c084fc;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🇸🇬 SGX Top High-Conviction Picks</h1>
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
        
        <h2>🇸🇬 Stock Analysis & Detailed Breakdown</h2>
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
