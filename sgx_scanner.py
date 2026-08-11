import datetime
import json
import yfinance as yf
import pandas as pd
import numpy as np

# ==========================================
# 1. 8-STOCK METADATA & FULL 5-YEAR DATA
# ==========================================
STOCK_METADATA = {
    # 🏦 BLUE CHIPS / BIG CAP (2 STOCKS)
    "D05.SI": {
        "name": "DBS Group Holdings",
        "category": "🏦 BLUE CHIP / BIG CAP",
        "horizon": "🏛️ CORE BLUE CHIP",
        "score": 9,
        "summary": "Dominant regional banking powerhouse benefiting from high interest margins, record wealth management fees, and digital leadership across Asia.",
        "catalyst": "Strong capital returns, active share buybacks, and expanding wealth AUM across ASEAN and Greater China.",
        "fundamentals": "ROE exceeding 16%, industry-leading cost-to-income ratio, and robust CET1 balance sheet reserves.",
        "technicals": "Holding strong above key moving average trend lines with institutional accumulation.",
        "risks": "Global interest rate cuts compressing NIMs and potential macroeconomic slowdowns in regional trade.",
        "buy_mult": (0.96, 0.99),
        "target_mult": 1.15,
        "stop_mult": 0.91,
        "intrinsic_val": "S$ 42.50",
        "pb_ratio": "1.45x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [14.3, 16.5, 20.1, 21.4, 22.8], # In S$ Billions
        "fin_net": [6.8, 8.2, 10.3, 10.8, 11.5],   # In S$ Billions
        "fin_ocf": ["S$8.5B", "S$10.1B", "S$12.4B", "S$13.1B", "S$14.0B"],
        "fin_fcf": ["S$8.1B", "S$9.6B", "S$11.8B", "S$12.5B", "S$13.3B"],
        "fin_div": ["S$1.20", "S$2.00", "S$2.16", "S$2.32", "S$2.50"],
        "asset_cash": ["S$62B", "S$71B", "S$82B", "S$88B", "S$95B"],
        "asset_st_inv": ["S$110B", "S$125B", "S$140B", "S$150B", "S$162B"],
        "asset_ppe": ["S$4.8B", "S$5.1B", "S$5.4B", "S$5.7B", "S$6.0B"],
        "asset_other": ["S$509B", "S$542B", "S$512B", "S$530B", "S$550B"],
        "asset_total": ["S$685B", "S$743B", "S$739B", "S$773B", "S$813B"],
        "fin_st_debt": ["S$22B", "S$26B", "S$30B", "S$33B", "S$36B"],
        "fin_lt_debt": ["S$35B", "S$40B", "S$45B", "S$48B", "S$52B"],
        "fin_moat": "Wide Moat (Singapore Banking Hegemony & Digital Scale) • 9.5/10"
    },
    "Z74.SI": {
        "name": "Singtel",
        "category": "🏦 BLUE CHIP / BIG CAP",
        "horizon": "🏛️ CORE BLUE CHIP",
        "score": 8,
        "summary": "Singtel's ST28 strategy is unlocking asset value via regional data center growth, Optus operational turnaround, and capital recycling dividends.",
        "catalyst": "Monetization of digital infrastructure assets and Nxera regional data center expansion.",
        "fundamentals": "Improving core EBIT margins, disciplined capital allocation, and growing dividend policy.",
        "technicals": "Multi-year breakout structure supported by consistent institutional volume.",
        "risks": "Foreign exchange depreciation in regional associate markets and Australian regulatory scrutiny.",
        "buy_mult": (0.95, 0.99),
        "target_mult": 1.18,
        "stop_mult": 0.90,
        "intrinsic_val": "S$ 3.60",
        "pb_ratio": "1.30x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [15.6, 15.3, 14.6, 14.1, 14.8], # In S$ Billions
        "fin_net": [0.5, 2.2, 2.2, 0.8, 2.5],     # In S$ Billions
        "fin_ocf": ["S$3.8B", "S$4.1B", "S$4.3B", "S$4.5B", "S$4.8B"],
        "fin_fcf": ["S$2.2B", "S$2.5B", "S$2.7B", "S$2.9B", "S$3.2B"],
        "fin_div": ["S$0.075", "S$0.093", "S$0.149", "S$0.150", "S$0.170"],
        "asset_cash": ["S$2.5B", "S$2.1B", "S$1.8B", "S$2.3B", "S$2.7B"],
        "asset_st_inv": ["S$300M", "S$350M", "S$400M", "S$450M", "S$500M"],
        "asset_ppe": ["S$11.2B", "S$11.8B", "S$12.1B", "S$12.5B", "S$13.0B"],
        "asset_other": ["S$34.0B", "S$33.5B", "S$32.8B", "S$33.2B", "S$34.0B"],
        "asset_total": ["S$48.0B", "S$47.75B", "S$47.1B", "S$48.45B", "S$50.2B"],
        "fin_st_debt": ["S$1.8B", "S$2.1B", "S$1.9B", "S$1.7B", "S$1.5B"],
        "fin_lt_debt": ["S$11.5B", "S$10.8B", "S$10.2B", "S$9.8B", "S$9.2B"],
        "fin_moat": "Wide Moat (Telecom Infrastructure Monopoly & Regional Associates) • 8.8/10"
    },

    # ⚡ SHORT-TERM (1-12 MONTHS) (2 STOCKS)
    "BS6.SI": {
        "name": "Yangzijiang Shipbuilding",
        "category": "⚡ SHORT-TERM (1-12 MTHS)",
        "horizon": "⚡ SHORT-TERM MOMENTUM",
        "score": 9,
        "summary": "Record Order Backlog. Stretched yard capacity through 2028 and expanding gross margins on green vessel builds drive immediate momentum.",
        "catalyst": "Delivery of higher-margin clean energy vessel contracts (LNG/Methanol dual-fuel).",
        "fundamentals": "Net cash position, strong operating cash flow generation, and disciplined execution.",
        "technicals": "Strong momentum chart pattern with bullish volume surges on breakout consolidations.",
        "risks": "Steel raw material price spikes and USD/RMB currency fluctuations.",
        "buy_mult": (0.95, 0.98),
        "target_mult": 1.22,
        "stop_mult": 0.90,
        "intrinsic_val": "S$ 3.20",
        "pb_ratio": "1.65x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [16.8, 20.7, 24.1, 27.5, 30.2], # RMB Billions
        "fin_net": [3.7, 2.8, 4.1, 4.8, 5.5],     # RMB Billions
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
        "fin_moat": "Wide Moat (Cost Leadership & Scale in Chinese Shipbuilding) • 8.8/10"
    },
    "S63.SI": {
        "name": "ST Engineering",
        "category": "⚡ SHORT-TERM (1-12 MTHS)",
        "horizon": "⚡ SHORT-TERM CATALYST",
        "score": 8,
        "summary": "Surging global defense spending and commercial aerospace MRO recovery pushing orderbook to record S$28B+ high.",
        "catalyst": "Accelerating defense contract deliveries and TransCore passenger transport integration earnings.",
        "fundamentals": "Steady dividend payout backed by resilient order book visibility across 3+ years.",
        "technicals": "Ascending triangle chart setup testing major resistance on strong volume.",
        "risks": "Supply chain component delays and integration costs for overseas acquisitions.",
        "buy_mult": (0.96, 0.99),
        "target_mult": 1.18,
        "stop_mult": 0.91,
        "intrinsic_val": "S$ 5.10",
        "pb_ratio": "3.80x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [7.7, 9.0, 10.1, 11.2, 12.1], # S$ Billions
        "fin_net": [0.57, 0.54, 0.59, 0.65, 0.72], # S$ Billions
        "fin_ocf": ["S$1.1B", "S$850M", "S$1.2B", "S$1.4B", "S$1.6B"],
        "fin_fcf": ["S$650M", "S$420M", "S$780M", "S$910M", "S$1.05B"],
        "fin_div": ["S$0.150", "S$0.160", "S$0.160", "S$0.170", "S$0.180"],
        "asset_cash": ["S$820M", "S$640M", "S$750M", "S$880M", "S$980M"],
        "asset_st_inv": ["S$50M", "S$60M", "S$70M", "S$80M", "S$90M"],
        "asset_ppe": ["S$2.1B", "S$2.3B", "S$2.5B", "S$2.7B", "S$2.9B"],
        "asset_other": ["S$8.5B", "S$11.2B", "S$11.8B", "S$12.2B", "S$12.6B"],
        "asset_total": ["S$11.47B", "S$14.2B", "S$15.12B", "S$15.86B", "S$16.57B"],
        "fin_st_debt": ["S$850M", "S$1.5B", "S$1.8B", "S$1.6B", "S$1.4B"],
        "fin_lt_debt": ["S$1.2B", "S$4.8B", "S$4.5B", "S$4.1B", "S$3.8B"],
        "fin_moat": "Wide Moat (Defense Engineering Monopoly & Global MRO Scale) • 9.0/10"
    },

    # 📈 MID-TERM (1-3 YEARS) (2 STOCKS)
    "G13.SI": {
        "name": "Genting Singapore",
        "category": "📈 MID-TERM (1-3 YRS)",
        "horizon": "📈 MID-TERM VALUE",
        "score": 10,
        "summary": "Value Recovery. Unrivaled S$3.5B net-cash balance sheet, RWS 2.0 expansion phases, and Asian tourism recovery offer multi-year upside floor.",
        "catalyst": "Completion of RWS 2.0 expansion attractions and returning high-yield international travelers.",
        "fundamentals": "Zero net debt, resilient cash flow generation, and high dividend payout security.",
        "technicals": "Consolidating at multi-year valuation floor with double-bottom reversal structure.",
        "risks": "Regional gaming competition and macro headwinds in Asian leisure travel.",
        "buy_mult": (0.95, 1.00),
        "target_mult": 1.25,
        "stop_mult": 0.90,
        "intrinsic_val": "S$ 1.15",
        "pb_ratio": "1.20x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [1.06, 1.73, 2.42, 2.55, 2.70], # S$ Billions
        "fin_net": [0.18, 0.35, 0.61, 0.65, 0.71], # S$ Billions
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
        "fin_moat": "Narrow Moat (Singapore Casino License Duopoly) • 8.5/10"
    },
    "OU8.SI": {
        "name": "Centurion Corp",
        "category": "📈 MID-TERM (1-3 YRS)",
        "horizon": "📈 MID-TERM GROWTH",
        "score": 10,
        "summary": "Severe Supply Shortage. Specialized worker and student accommodation operator capturing steep rental rate revisions across Singapore and UK.",
        "catalyst": "Near 100% occupancy rates across PBWA/PBSA assets and organic bed capacity expansions.",
        "fundamentals": "Rapid net profit expansion, active debt deleveraging, and expanding ROE.",
        "technicals": "Strong uptrend with consistent institutional buying volume on minor dips.",
        "risks": "Regulatory updates regarding foreign worker density and foreign student visa policies.",
        "buy_mult": (0.95, 0.98),
        "target_mult": 1.25,
        "stop_mult": 0.88,
        "intrinsic_val": "S$ 1.95",
        "pb_ratio": "0.85x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [0.14, 0.18, 0.21, 0.24, 0.26], # S$ Billions
        "fin_net": [0.05, 0.07, 0.15, 0.18, 0.20], # S$ Billions
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
        "fin_moat": "Narrow Moat (High Regulatory Barriers & Asset Footprint) • 7.8/10"
    },

    # 🛡️ LONG-TERM (3-5+ YEARS) (2 STOCKS)
    "U11.SI": {
        "name": "UOB Bank",
        "category": "🛡️ LONG-TERM (3-5+ YRS)",
        "horizon": "🛡️ LONG-TERM COMPOUNDER",
        "score": 8,
        "summary": "Resilient Dividend Yield. Regional ASEAN expansion powered by Citigroup consumer acquisition and rising wealth management fee flows.",
        "catalyst": "Synergy realization from Citi ASEAN integration and digital banking growth.",
        "fundamentals": "Strong CET1 ratio, high dividend yield floor (~5%+), and strong credit loss coverage.",
        "technicals": "Healthy consolidation pattern with solid support at long-term moving averages.",
        "risks": "Compression in Net Interest Margin (NIM) under lower benchmark interest rates.",
        "buy_mult": (0.96, 0.99),
        "target_mult": 1.16,
        "stop_mult": 0.92,
        "intrinsic_val": "S$ 48.00",
        "pb_ratio": "1.15x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [9.8, 11.6, 13.9, 14.5, 15.2], # S$ Billions
        "fin_net": [4.0, 4.6, 5.7, 6.0, 6.4],    # S$ Billions
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
        "fin_moat": "Wide Moat (Regional ASEAN Banking Oligopoly) • 9.0/10"
    },
    "C52.SI": {
        "name": "ComfortDelGro",
        "category": "🛡️ LONG-TERM (3-5+ YRS)",
        "horizon": "🛡️ LONG-TERM INCOME",
        "score": 7,
        "summary": "Public Transport Mobility Pillar. International tender wins in UK/Australia and taxi booking fee adjustments drive multi-year steady free cash flow.",
        "catalyst": "Overseas bus & rail contract repricing and margin expansion from A2B integration.",
        "fundamentals": "Strong cash generation, pristine balance sheet, and reliable dividend yield.",
        "technicals": "Multi-month base accumulation with steady volume inflows.",
        "risks": "Wage inflation for drivers and aggressive ride-hailing competition.",
        "buy_mult": (0.95, 0.99),
        "target_mult": 1.18,
        "stop_mult": 0.91,
        "intrinsic_val": "S$ 1.65",
        "pb_ratio": "1.10x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": [3.5, 3.8, 3.9, 4.2, 4.5],  # S$ Billions
        "fin_net": [0.13, 0.17, 0.18, 0.21, 0.24], # S$ Billions
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
        "fin_moat": "Narrow Moat (Public Concession Scale & Mobility Ecosystem) • 7.5/10"
    }
}

TICKERS = ["D05.SI", "Z74.SI", "BS6.SI", "S63.SI", "G13.SI", "OU8.SI", "U11.SI", "C52.SI"]

# ==========================================
# 2. HELPER CALCULATIONS & FETCH
# ==========================================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def fetch_stock_data(ticker):
    meta = STOCK_METADATA.get(ticker, {})
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
        if yield_pct == 0:
            fallback_yields = {
                "D05.SI": 5.20, "Z74.SI": 5.10, "BS6.SI": 4.76, "S63.SI": 3.80,
                "G13.SI": 6.45, "OU8.SI": 2.47, "U11.SI": 4.06, "C52.SI": 6.39
            }
            yield_pct = fallback_yields.get(ticker, 4.50)

    except Exception as e:
        print(f"yfinance fetch fallback for {ticker}: {e
