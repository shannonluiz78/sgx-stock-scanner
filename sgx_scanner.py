import yfinance as yf
import pandas as pd
import datetime
import json
import os

# ======================================================================
# ⚙️ CONFIGURATION
# ======================================================================
GITHUB_USERNAME = "shannonluiz78"  # 👈 Updated from your workflow run
GITHUB_REPO_NAME = "sgx-stock-scanner"

BLUECHIP_TICKERS = ["D05.SI", "O39.SI", "U11.SI", "Z74.SI", "S63.SI", "BN4.SI"]

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

STOCK_METADATA = {
    "D05.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)", "horizon_grp": "SHORT", "badge_cls": "badge-short",
        "catalyst": "Dominant regional wealth hub engine and commitment to steady quarterly dividend growth.",
        "fundamentals": "Highest Return on Equity (ROE) in Southeast Asia (~18%) with strong capital reserves.",
        "technicals": "Strong institutional accumulation; consistently supported by 50-day SMA during pullbacks.",
        "risks": "Global economic slowdown leading to lower loan demand and credit provisions.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.12, "stop_mult": 0.93,
        "intrinsic_val": "S$ 44.50", "pb_ratio": "1.58x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$14.3B", "S$16.5B", "S$20.2B", "S$21.4B", "S$22.8B"],
        "fin_net": ["S$6.80B", "S$8.19B", "S$10.29B", "S$10.85B", "S$11.40B"],
        "fin_ocf": ["S$7.10B", "S$9.40B", "S$12.50B", "S$13.10B", "S$13.80B"],
        "fin_fcf": ["S$6.50B", "S$8.80B", "S$11.90B", "S$12.40B", "S$13.00B"],
        "fin_div": ["S$1.20", "S$1.50", "S$1.92", "S$2.16", "S$2.40"],
        "asset_cash": ["S$52.1B", "S$58.4B", "S$65.0B", "S$70.8B", "S$75.2B"],
        "asset_st_inv": ["S$82.0B", "S$91.2B", "S$100.5B", "S$106.3B", "S$112.5B"],
        "asset_ppe": ["S$3.1B", "S$3.3B", "S$3.5B", "S$3.7B", "S$3.8B"],
        "asset_other": ["S$450.0B", "S$480.0B", "S$510.0B", "S$535.0B", "S$552.5B"],
        "asset_total": ["S$587.2B", "S$632.9B", "S$679.0B", "S$715.8B", "S$744.0B"],
        "fin_st_debt": ["S$8.5B", "S$9.8B", "S$10.5B", "S$11.2B", "S$12.4B"],
        "fin_lt_debt": ["S$16.0B", "S$18.2B", "S$19.8B", "S$20.9B", "S$22.1B"],
        "fin_moat": "Wide Moat (Dominant SG Market Share) • 9.5/10"
    },
    "O39.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)", "horizon_grp": "SHORT", "badge_cls": "badge-short",
        "catalyst": "Robust wealth management fee inflows and strong capital management buffer.",
        "fundamentals": "P/B ratio remains reasonable (~1.1x) with an attractive yield floor above 5.0%.",
        "technicals": "Stock frequently tests and bounces off key 50-day moving average support lines.",
        "risks": "Potential interest rate cuts lowering Net Interest Margin (NIM) growth.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.10, "stop_mult": 0.93,
        "intrinsic_val": "S$ 17.80", "pb_ratio": "1.12x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$10.1B", "S$11.7B", "S$13.5B", "S$14.2B", "S$15.0B"],
        "fin_net": ["S$4.86B", "S$5.75B", "S$7.02B", "S$7.45B", "S$7.85B"],
        "fin_ocf": ["S$5.20B", "S$6.80B", "S$8.90B", "S$9.20B", "S$9.70B"],
        "fin_fcf": ["S$4.80B", "S$6.30B", "S$8.40B", "S$8.70B", "S$9.10B"],
        "fin_div": ["S$0.53", "S$0.68", "S$0.84", "S$0.88", "S$0.92"],
        "asset_cash": ["S$31.0B", "S$34.2B", "S$38.0B", "S$40.5B", "S$42.1B"],
        "asset_st_inv": ["S$51.5B", "S$56.0B", "S$61.2B", "S$65.0B", "S$68.3B"],
        "asset_ppe": ["S$2.4B", "S$2.5B", "S$2.7B", "S$2.8B", "S$2.9B"],
        "asset_other": ["S$220.0B", "S$240.0B", "S$260.0B", "S$272.0B", "S$283.7B"],
        "asset_total": ["S$304.9B", "S$332.7B", "S$361.9B", "S$380.3B", "S$397.0B"],
        "fin_st_debt": ["S$5.8B", "S$6.4B", "S$7.2B", "S$7.8B", "S$8.2B"],
        "fin_lt_debt": ["S$10.5B", "S$11.8B", "S$13.0B", "S$13.9B", "S$14.5B"],
        "fin_moat": "Wide Moat (Regional Wealth Franchise) • 9.0/10"
    },
    "BS6.SI": {
        "horizon": "⚡ SHORT-TERM (1–3 MOS)", "horizon_grp": "SHORT", "badge_cls": "badge-short",
        "catalyst": "Record order backlog into 2028 with higher-margin clean energy vessel contracts.",
        "fundamentals": "Strong net cash position; high ROE exceeding 20% with strong dividend coverage.",
        "technicals": "Bullish momentum breakout with institutional volume surge; trading above 20 & 50 SMA.",
        "risks": "Fluctuations in steel raw material costs and USD/RMB exchange rate volatility.",
        "buy_mult": (0.96, 0.99), "target_mult": 1.15, "stop_mult": 0.91,
        "intrinsic_val": "S$ 2.90", "pb_ratio": "1.35x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["RMB16.8B", "RMB20.7B", "RMB24.1B", "RMB26.8B", "RMB29.5B"],
        "fin_net": ["RMB3.70B", "RMB2.81B", "RMB4.10B", "RMB4.85B", "RMB5.40B"],
        "fin_ocf": ["RMB4.20B", "RMB3.90B", "RMB5.80B", "RMB6.20B", "RMB6.90B"],
        "fin_fcf": ["RMB3.60B", "RMB3.20B", "RMB5.10B", "RMB5.50B", "RMB6.10B"],
        "fin_div": ["S$0.05", "S$0.05", "S$0.065", "S$0.085", "S$0.10"],
        "asset_cash": ["RMB10.2B", "RMB11.8B", "RMB13.5B", "RMB15.0B", "RMB16.2B"],
        "asset_st_inv": ["RMB3.5B", "RMB4.2B", "RMB5.0B", "RMB5.4B", "RMB5.8B"],
        "asset_ppe": ["RMB5.8B", "RMB6.1B", "RMB6.4B", "RMB6.7B", "RMB6.9B"],
        "asset_other": ["RMB14.5B", "RMB16.2B", "RMB18.5B", "RMB20.1B", "RMB22.1B"],
        "asset_total": ["RMB34.0B", "RMB38.3B", "RMB43.4B", "RMB47.2B", "RMB51.0B"],
        "fin_st_debt": ["RMB1.8B", "RMB2.2B", "RMB2.6B", "RMB2.9B", "RMB3.1B"],
        "fin_lt_debt": ["RMB0.8B", "RMB0.9B", "RMB1.0B", "RMB1.1B", "RMB1.2B"],
        "fin_moat": "Narrow Moat (Cost Leadership in Shipbuilding) • 8.0/10"
    },
    "OU8.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
        "catalyst": "Acute shortage of foreign worker accommodation in SG and student housing in the UK.",
        "fundamentals": "Consistent revenue growth with strong occupancy rates exceeding 95% across key markets.",
        "technicals": "Sustained uptrend structure making higher lows; steady RSI accumulation without spike exhaustion.",
        "risks": "Regulatory changes in foreign worker quotas or student visa policies.",
        "buy_mult": (0.95, 0.99), "target_mult": 1.24, "stop_mult": 0.88,
        "intrinsic_val": "S$ 0.95", "pb_ratio": "0.85x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$123M", "S$180M", "S$207M", "S$235M", "S$260M"],
        "fin_net": ["S$52M", "S$71M", "S$153M", "S$175M", "S$192M"],
        "fin_ocf": ["S$68M", "S$92M", "S$115M", "S$138M", "S$155M"],
        "fin_fcf": ["S$45M", "S$65M", "S$88M", "S$105M", "S$120M"],
        "fin_div": ["S$0.025", "S$0.025", "S$0.045", "S$0.055", "S$0.065"],
        "asset_cash": ["S$45M", "S$58M", "S$72M", "S$84M", "S$92M"],
        "asset_st_inv": ["S$8M", "S$11M", "S$14M", "S$16M", "S$18M"],
        "asset_ppe": ["S$1.10B", "S$1.22B", "S$1.35B", "S$1.42B", "S$1.48B"],
        "asset_other": ["S$60M", "S$75M", "S$90M", "S$100M", "S$110M"],
        "asset_total": ["S$1.21B", "S$1.36B", "S$1.52B", "S$1.62B", "S$1.70B"],
        "fin_st_debt": ["S$42M", "S$55M", "S$68M", "S$75M", "S$82M"],
        "fin_lt_debt": ["S$450M", "S$520M", "S$600M", "S$640M", "S$680M"],
        "fin_moat": "Narrow Moat (Regulatory Operating Licenses) • 8.0/10"
    },
    "Z74.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
        "catalyst": "ST25 strategic restructuring plan unlocking value from regional data centers and Optus.",
        "fundamentals": "Improving free cash flow supporting sustainable dividend payouts and debt reduction.",
        "technicals": "Rounded bottom reversal pattern emerging with rising 20-day moving average.",
        "risks": "Competitive pricing pressure in regional mobile markets (e.g., Australia).",
        "buy_mult": (0.96, 0.99), "target_mult": 1.18, "stop_mult": 0.91,
        "intrinsic_val": "S$ 3.80", "pb_ratio": "1.42x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$15.6B", "S$15.3B", "S$14.6B", "S$14.1B", "S$14.8B"],
        "fin_net": ["S$1.54B", "S$1.95B", "S$2.23B", "S$2.48B", "S$2.70B"],
        "fin_ocf": ["S$3.80B", "S$4.10B", "S$4.20B", "S$4.50B", "S$4.80B"],
        "fin_fcf": ["S$2.10B", "S$2.40B", "S$2.60B", "S$2.90B", "S$3.20B"],
        "fin_div": ["S$0.075", "S$0.093", "S$0.149", "S$0.150", "S$0.170"],
        "asset_cash": ["S$1.20B", "S$1.45B", "S$1.60B", "S$1.75B", "S$1.85B"],
        "asset_st_inv": ["S$280M", "S$320M", "S$360M", "S$390M", "S$420M"],
        "asset_ppe": ["S$10.5B", "S$10.9B", "S$11.2B", "S$11.5B", "S$11.8B"],
        "asset_other": ["S$28.5B", "S$30.1B", "S$31.8B", "S$33.2B", "S$34.4B"],
        "asset_total": ["S$40.48B", "S$42.77B", "S$44.96B", "S$46.84B", "S$48.57B"],
        "fin_st_debt": ["S$1.50B", "S$1.70B", "S$1.85B", "S$1.98B", "S$2.10B"],
        "fin_lt_debt": ["S$6.80B", "S$7.30B", "S$7.80B", "S$8.20B", "S$8.50B"],
        "fin_moat": "Wide Moat (Infrastructure & Spectrum Assets) • 8.5/10"
    },
    "G13.SI": {
        "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
        "catalyst": "Ongoing RWS 2.0 expansion & ongoing recovery in regional flight capacities and Chinese tourism.",
        "fundamentals": "Pristine balance sheet with over S$3B in net cash providing downside cushion.",
        "technicals": "Trading near multi-year valuation support zone; low RSI indicates minimal downside risk.",
        "risks": "Slower-than-expected recovery in high-roller VIP gaming spend.",
        "buy_mult": (0.95, 1.00), "target_mult": 1.24, "stop_mult": 0.89,
        "intrinsic_val": "S$ 1.15", "pb_ratio": "1.05x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$1.07B", "S$1.73B", "S$2.42B", "S$2.65B", "S$2.85B"],
        "fin_net": ["S$183M", "S$345M", "S$611M", "S$680M", "S$740M"],
        "fin_ocf": ["S$310M", "S$540M", "S$890M", "S$980M", "S$1.05B"],
        "fin_fcf": ["S$220M", "S$410M", "S$680M", "S$750M", "S$810M"],
        "fin_div": ["S$0.01", "S$0.035", "S$0.040", "S$0.045", "S$0.050"],
        "asset_cash": ["S$2.50B", "S$2.95B", "S$3.30B", "S$3.60B", "S$3.85B"],
        "asset_st_inv": ["S$120M", "S$150M", "S$175M", "S$195M", "S$210M"],
        "asset_ppe": ["S$4.50B", "S$4.38B", "S$4.25B", "S$4.15B", "S$4.10B"],
        "asset_other": ["S$180M", "S$195M", "S$210M", "S$225M", "S$240M"],
        "asset_total": ["S$7.30B", "S$7.675B", "S$7.935B", "S$8.17B", "S$8.40B"],
        "fin_st_debt": ["S$10M", "S$12M", "S$14M", "S$15M", "S$15M"],
        "fin_lt_debt": ["S$280M", "S$250M", "S$230M", "S$220M", "S$210M"],
        "fin_moat": "Wide Moat (Duopoly Gaming License in SG) • 9.0/10"
    },
    "U11.SI": {
        "horizon": "🏛️ LONG-TERM (3–5+ YRS)", "horizon_grp": "LONG", "badge_cls": "badge-long",
        "catalyst": "Citigroup ASEAN consumer portfolio acquisition driving broader regional fee income.",
        "fundamentals": "Steady dividend payout ratio (~50%) with solid non-performing loan (NPL) coverage.",
        "technicals": "Long-term bullish trend channel intact; low volatility consolidation near current levels.",
        "risks": "Broader ASEAN macroeconomic slowdown impacting regional credit growth.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.15, "stop_mult": 0.92,
        "intrinsic_val": "S$ 38.00", "pb_ratio": "1.15x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$9.8B", "S$11.6B", "S$13.9B", "S$14.5B", "S$15.2B"],
        "fin_net": ["S$4.07B", "S$4.57B", "S$5.71B", "S$6.05B", "S$6.40B"],
        "fin_ocf": ["S$4.50B", "S$5.30B", "S$7.10B", "S$7.50B", "S$8.00B"],
        "fin_fcf": ["S$4.10B", "S$4.80B", "S$6.60B", "S$7.00B", "S$7.50B"],
        "fin_div": ["S$1.20", "S$1.35", "S$1.70", "S$1.80", "S$1.90"],
        "asset_cash": ["S$26.5B", "S$30.1B", "S$33.8B", "S$36.2B", "S$38.5B"],
        "asset_st_inv": ["S$52.0B", "S$58.5B", "S$64.2B", "S$68.0B", "S$72.1B"],
        "asset_ppe": ["S$2.8B", "S$3.0B", "S$3.1B", "S$3.3B", "S$3.4B"],
        "asset_other": ["S$320.0B", "S$345.0B", "S$368.0B", "S$380.0B", "S$393.0B"],
        "asset_total": ["S$401.3B", "S$436.6B", "S$469.1B", "S$487.5B", "S$507.0B"],
        "fin_st_debt": ["S$4.8B", "S$5.2B", "S$5.8B", "S$6.1B", "S$6.5B"],
        "fin_lt_debt": ["S$8.5B", "S$9.4B", "S$10.2B", "S$10.8B", "S$11.2B"],
        "fin_moat": "Wide Moat (Regional Banking Franchise) • 8.8/10"
    },
    "C52.SI": {
        "horizon": "🏛️ LONG-TERM (3–5+ YRS)", "horizon_grp": "LONG", "badge_cls": "badge-long",
        "catalyst": "Winning lucrative long-term overseas public bus/rail tenders in Australia and the UK.",
        "fundamentals": "Defensive business model with stable cash generation and healthy dividend yield (~5.5%).",
        "technicals": "Price consolidating inside a tight accumulation range above the 200-day moving average.",
        "risks": "Driver shortages and wage inflation impacting overseas operational margins.",
        "buy_mult": (0.96, 1.00), "target_mult": 1.22, "stop_mult": 0.90,
        "intrinsic_val": "S$ 1.80", "pb_ratio": "1.08x",
        "fin_years": ["2021", "2022", "2023", "2024", "2025"],
        "fin_rev": ["S$3.54B", "S$3.78B", "S$3.88B", "S$4.10B", "S$4.35B"],
        "fin_net": ["S$123M", "S$173M", "S$180M", "S$210M", "S$235M"],
        "fin_ocf": ["S$480M", "S$520M", "S$590M", "S$640M", "S$690M"],
        "fin_fcf": ["S$290M", "S$340M", "S$410M", "S$450M", "S$490M"],
        "fin_div": ["S$0.043", "S$0.084", "S$0.072", "S$0.080", "S$0.090"],
        "asset_cash": ["S$610M", "S$680M", "S$740M", "S$790M", "S$840M"],
        "asset_st_inv": ["S$80M", "S$95M", "S$105M", "S$112M", "S$120M"],
        "asset_ppe": ["S$2.30B", "S$2.42B", "S$2.50B", "S$2.58B", "S$2.65B"],
        "asset_other": ["S$1.05B", "S$1.12B", "S$1.18B", "S$1.24B", "S$1.30B"],
        "asset_total": ["S$4.04B", "S$4.315B", "S$4.525B", "S$4.722B", "S$4.91B"],
        "fin_st_debt": ["S$95M", "S$110M", "S$122M", "S$132M", "S$140M"],
        "fin_lt_debt": ["S$210M", "S$235M", "S$255M", "S$275M", "S$290M"],
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
        return 0.04

def scan_stocks():
    results = []
    
    for ticker, name in SGX_TICKERS.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5y")
            
            if df.empty or len(df) < 20:
                continue
                
            df = df.fillna(method='ffill').dropna()
            
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
            df['RSI_14'] = calculate_rsi(df['Close'])
            
            latest = df.iloc[-1]
            latest_price = float(latest['Close'])
            vol_sma = float(latest['Vol_SMA_20']) if 'Vol_SMA_20' in latest else 1.0
            volume_surge = (float(latest['Volume']) / vol_sma) if vol_sma > 0 else 1.0
            
            rsi = float(latest['RSI_14']) if not pd.isna(latest['RSI_14']) else 50.0
            trend_bullish = latest['SMA_20'] > latest['SMA_50'] if not pd.isna(latest['SMA_50']) else True
            price_above_50sma = latest_price > latest['SMA_50'] if not pd.isna(latest['SMA_50']) else True
            div_yield = get_dividend_yield(stock)
            
            df_1y = df.tail(252)
            high_52w = float(df_1y['Close'].max())
            low_52w = float(df_1y['Close'].min())
            perf_52w = ((latest_price - float(df_1y['Close'].iloc[0])) / float(df_1y['Close'].iloc[0])) * 100.0
            
            is_bluechip = ticker in BLUECHIP_TICKERS
            score = 5
            
            if volume_surge >= 1.15: score += 2
            if trend_bullish: score += 1
            if price_above_50sma: score += 1
            if 40 <= rsi <= 72: score += 1
            
            meta = STOCK_METADATA.get(ticker, {
                "horizon": "📈 MID-TERM (1–3 YRS)", "horizon_grp": "MID", "badge_cls": "badge-mid",
                "catalyst": "Technical trend alignment supported by positive institutional trading volume.",
                "fundamentals": "Stable market capitalization with consistent historical
