import os
import time
import datetime
import json
import pandas as pd
import numpy as np
import requests
import yfinance as yf

# Configure custom browser session to prevent Yahoo bot detection
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36"
})

STOCK_UNIVERSE = [
    # STI 30 Components
    {"ticker": "D05.SI", "name": "DBS Group Holdings", "sector": "Banking", "is_anchor": True},
    {"ticker": "O39.SI", "name": "OCBC Bank", "sector": "Banking", "is_anchor": True},
    {"ticker": "U11.SI", "name": "UOB", "sector": "Banking", "is_anchor": True},
    {"ticker": "Z74.SI", "name": "Singtel", "sector": "Telecommunications", "is_anchor": True},
    {"ticker": "S68.SI", "name": "Singapore Exchange", "sector": "Financial Services", "is_anchor": True},
    {"ticker": "C6L.SI", "name": "Singapore Airlines", "sector": "Aviation", "is_anchor": False},
    {"ticker": "BN4.SI", "name": "Keppel Ltd", "sector": "Conglomerate", "is_anchor": False},
    {"ticker": "F34.SI", "name": "Wilmar International", "sector": "Consumer Goods", "is_anchor": False},
    {"ticker": "BS6.SI", "name": "Yangzijiang Shipbuilding", "sector": "Industrials", "is_anchor": False},
    {"ticker": "S63.SI", "name": "ST Engineering", "sector": "Industrials", "is_anchor": False},
    {"ticker": "G13.SI", "name": "Genting Singapore", "sector": "Consumer Services", "is_anchor": False},
    {"ticker": "Y92.SI", "name": "Thai Beverage", "sector": "Consumer Goods", "is_anchor": False},
    {"ticker": "9CI.SI", "name": "CapitaLand Investment", "sector": "Real Estate", "is_anchor": False},
    {"ticker": "C38U.SI", "name": "CapitaLand Int Comm Trust", "sector": "REIT", "is_anchor": True},
    {"ticker": "A17U.SI", "name": "CapitaLand Ascendas REIT", "sector": "REIT", "is_anchor": True},
    {"ticker": "M44U.SI", "name": "Mapletree Logistics Trust", "sector": "REIT", "is_anchor": False},
    {"ticker": "ME8U.SI", "name": "Mapletree Industrial Trust", "sector": "REIT", "is_anchor": False},
    {"ticker": "N2IU.SI", "name": "Mapletree Pan Asia Comm Trust", "sector": "REIT", "is_anchor": False},
    {"ticker": "J69U.SI", "name": "Frasers Centrepoint Trust", "sector": "REIT", "is_anchor": False},
    {"ticker": "BUOU.SI", "name": "Frasers Logistics & Comm Trust", "sector": "REIT", "is_anchor": False},
    {"ticker": "J36.SI", "name": "Jardine Matheson", "sector": "Conglomerate", "is_anchor": False},
    {"ticker": "C07.SI", "name": "Jardine Cycle & Carriage", "sector": "Consumer Services", "is_anchor": False},
    {"ticker": "U96.SI", "name": "Sembcorp Industries", "sector": "Utilities", "is_anchor": False},
    {"ticker": "S58.SI", "name": "SATS Ltd", "sector": "Aviation Services", "is_anchor": False},
    {"ticker": "5E2.SI", "name": "Seatrium Ltd", "sector": "Offshore & Marine", "is_anchor": False},
    {"ticker": "C09.SI", "name": "City Developments Ltd", "sector": "Real Estate", "is_anchor": False},
    {"ticker": "U14.SI", "name": "UOL Group", "sector": "Real Estate", "is_anchor": False},
    {"ticker": "H78.SI", "name": "Hongkong Land", "sector": "Real Estate", "is_anchor": False},
    {"ticker": "D01.SI", "name": "DFI Retail Group", "sector": "Consumer Staples", "is_anchor": False},
    {"ticker": "EMI.SI", "name": "Emperador Inc", "sector": "Consumer Staples", "is_anchor": False},
    
    # Growth & Mid-Cap Additions
    {"ticker": "OV8.SI", "name": "Sheng Siong Group", "sector": "Consumer Staples", "is_anchor": False},
    {"ticker": "AIY.SI", "name": "iFAST Corporation", "sector": "Fintech / Wealth", "is_anchor": False},
    {"ticker": "MZH.SI", "name": "Nanofilm Technologies", "sector": "Technology", "is_anchor": False},
    {"ticker": "BSL.SI", "name": "Raffles Medical Group", "sector": "Healthcare", "is_anchor": False}
]

def compute_rsi(series, period=14):
    if len(series) < period:
        return pd.Series([np.nan] * len(series), index=series.index)
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))

def format_pct(val):
    if val is None or pd.isna(val) or val == "N/A": return "N/A"
    try:
        num = float(val)
        return f"{num * 100:.2f}%" if abs(num) < 1.0 else f"{num:.2f}%"
    except: return "N/A"

def format_compact(val):
    if val is None or pd.isna(val) or val == "N/A": return "N/A"
    try:
        num = float(val)
        if abs(num) >= 1e9: return f"${num/1e9:.2f}B"
        if abs(num) >= 1e6: return f"${num/1e6:.2f}M"
        return f"${num:,.0f}"
    except: return "N/A"

def get_statement_row(df, possible_names):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty: return None
    for name in possible_names:
        for idx in df.index:
            if str(idx).strip().lower() == name.strip().lower():
                return df.loc[idx]
    return None

def analyze_universe_batch(stock_universe):
    tickers = [item["ticker"] for item in stock_universe]
    print(f"⚡ Downloading 1-year price history for {len(tickers)} tickers in 1 batch request...")

    try:
        batch_df = yf.download(tickers, period="1y", group_by="ticker", threads=True, progress=False, session=session)
    except Exception as e:
        print(f"⚠️ Warning during batch download: {e}")
        batch_df = pd.DataFrame()

    analyzed_stocks = []

    for item in stock_universe:
        symbol = item["ticker"]
        name = item["name"]
        sector = item["sector"]
        is_anchor = item["is_anchor"]

        data = {
            "ticker": symbol, "name": name, "sector": sector, "is_anchor": is_anchor,
            "price": "N/A", "change": 0.0, "p_change": 0.0, "pe_ratio": "N/A", "pb_ratio": "N/A",
            "div_yield": 0.0, "mkt_cap": "N/A", "mkt_cap_raw": 0, "52w_range": "N/A",
            "ma50": "N/A", "ma200": "N/A", "rsi": "N/A", "vol_surge": False,
            "intrinsic_val": "N/A", "moat": "Medium", "short_debt": "N/A", "long_debt": "N/A",
            "hist_prices": [], "hist_labels": [],
            "daily_prices": [], "daily_dates": [],
            "years": [], "revenue": [], "net_income": [],
            "ocf": [], "fcf": [], "dividends": [], "assets_cash": "N/A", "assets_st_inv": "N/A",
            "assets_ppe": "N/A", "signal": "NEUTRAL", "scores": {"anchor": 0, "momentum": 0, "growth": 0, "compounder": 0}
        }

        # 1. Price Data Parsing
        try:
            hist = None
            if not batch_df.empty:
                if len(tickers) == 1:
                    hist = batch_df.dropna(how="all")
                elif symbol in batch_df.columns.levels[0]:
                    hist = batch_df[symbol].dropna(how="all")

            if hist is not None and not hist.empty and len(hist) >= 5:
                last_close = float(hist["Close"].iloc[-1])
                prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last_close
                data["price"] = last_close
                data["change"] = last_close - prev_close
                data["p_change"] = (data["change"] / (prev_close + 1e-9)) * 100

                # Full Daily Data for Interactive Modal Charting
                data["daily_prices"] = [round(float(p), 2) for p in hist["Close"].tolist()]
                data["daily_dates"] = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d) for d in hist.index]

                # Sampled Data for Mini Sparklines
                sample_step = max(1, len(hist) // 20)
                sampled_df = hist.iloc[::sample_step]
                data["hist_prices"] = [round(float(p), 2) for p in sampled_df["Close"].tolist()]
                data["hist_labels"] = [d.strftime("%b %y") if hasattr(d, 'strftime') else str(d) for d in sampled_df.index]

                if len(hist) >= 50:
                    ma50_s = hist["Close"].rolling(50).mean()
                    c_ma50 = ma50_s.iloc[-1]
                    data["ma50"] = round(float(c_ma50), 2) if not pd.isna(c_ma50) else "N/A"

                if len(hist) >= 200:
                    ma200_s = hist["Close"].rolling(200).mean()
                    c_ma200 = ma200_s.iloc[-1]
                    data["ma200"] = round(float(c_ma200), 2) if not pd.isna(c_ma200) else "N/A"

                rsi_s = compute_rsi(hist["Close"], 14)
                c_rsi = rsi_s.iloc[-1] if not rsi_s.empty else np.nan
                data["rsi"] = round(float(c_rsi), 1) if not pd.isna(c_rsi) else "N/A"

                c_vol = float(hist["Volume"].iloc[-1]) if "Volume" in hist.columns else 0
                avg_vol_20 = float(hist["Volume"].tail(20).mean()) if "Volume" in hist.columns and len(hist) >= 20 else 1
                data["vol_surge"] = bool(c_vol > 1.5 * avg_vol_20)

                if data["ma50"] != "N/A" and data["ma200"] != "N/A":
                    if data["ma50"] > data["ma200"]:
                        data["signal"] = "BULLISH TREND"
                if data["signal"] == "NEUTRAL" and isinstance(c_rsi, (int, float)):
                    if c_rsi < 35: data["signal"] = "OVERSOLD"
                    elif c_rsi > 68: data["signal"] = "OVERBOUGHT"
                if data["vol_surge"]:
                    data["signal"] += " + VOL SURGE"

        except Exception as e:
            print(f"⚠️ Note: Failed processing price history for {symbol}: {e}")

        # 2. Metadata & Financial Statements Parsing
        try:
            time.sleep(0.3)
            ticker_obj = yf.Ticker(symbol, session=session)
            
            info = {}
            try:
                info = ticker_obj.info or {}
            except Exception:
                pass

            data["mkt_cap_raw"] = info.get("marketCap", 0) or 0
            data["mkt_cap"] = format_compact(data["mkt_cap_raw"])
            data["pe_ratio"] = round(info.get("trailingPE"), 2) if info.get("trailingPE") else "N/A"
            data["pb_ratio"] = round(info.get("priceToBook"), 2) if info.get("priceToBook") else "N/A"
            data["div_yield"] = float(info.get("dividendYield", 0) or 0)

            eps = info.get("trailingEps")
            if eps and eps > 0:
                data["intrinsic_val"] = f"${eps * 15.5:.2f}"

            if is_anchor or data["mkt_cap_raw"] > 1e10:
                data["moat"] = "WIDE MOAT"
            elif data["mkt_cap_raw"] > 2e9:
                data["moat"] = "NARROW MOAT"
            else:
                data["moat"] = "MODERATE MOAT"

            # Financials
            try:
                fin = ticker_obj.financials
                if fin is not None and not fin.empty:
                    cols = list(fin.columns[:5])
                    data["years"] = [d.strftime("%Y") if hasattr(d, 'strftime') else str(d) for d in cols][::-1]
                    rev_row = get_statement_row(fin, ["Total Revenue", "Operating Revenue", "Revenue"])
                    net_row = get_statement_row(fin, ["Net Income", "Net Income Common Stockholders"])
                    data["revenue"] = [format_compact(rev_row[c]) if rev_row is not None and c in rev_row else "N/A" for c in cols][::-1]
                    data["net_income"] = [format_compact(net_row[c]) if net_row is not None and c in net_row else "N/A" for c in cols][::-1]
            except Exception:
                pass

            try:
                cf = ticker_obj.cashflow
                if cf is not None and not cf.empty:
                    cols = list(cf.columns[:5])
                    ocf_row = get_statement_row(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"])
                    capex_row = get_statement_row(cf, ["Capital Expenditure", "Capital Expenditures"])
                    ocf_vals = [ocf_row[c] if ocf_row is not None and c in ocf_row else 0 for c in cols]
                    capex_vals = [abs(capex_row[c]) if capex_row is not None and c in capex_row else 0 for c in cols]
                    fcf_vals = [o - ca for o, ca in zip(ocf_vals, capex_vals)]
                    data["ocf"] = [format_compact(v) for v in ocf_vals][::-1]
                    data["fcf"] = [format_compact(v) for v in fcf_vals][::-1]
            except Exception:
                pass

            try:
                bs = ticker_obj.balance_sheet
                if bs is not None and not bs.empty:
                    c0 = bs.columns[0]
                    st_debt = get_statement_row(bs, ["Current Debt", "Current Debt And Capital Lease Obligation", "Short Term Debt"])
                    lt_debt = get_statement_row(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"])
                    cash = get_statement_row(bs, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])
                    ppe = get_statement_row(bs, ["Gross PPE", "Net PPE", "Properties"])
                    data["short_debt"] = format_compact(st_debt[c0]) if st_debt is not None and c0 in st_debt else "N/A"
                    data["long_debt"] = format_compact(lt_debt[c0]) if lt_debt is not None and c0 in lt_debt else "N/A"
                    data["assets_cash"] = format_compact(cash[c0]) if cash is not None and c0 in cash else "N/A"
                    data["assets_ppe"] = format_compact(ppe[c0]) if ppe is not None and c0 in ppe else "N/A"
            except Exception:
                pass

        except Exception as e:
            print(f"⚠️ Note: Fundamentals skipped for {symbol}: {e}")

        # 3. Scoring
        if is_anchor or data["mkt_cap_raw"] > 8e9:
            data["scores"]["anchor"] = (data["div_yield"] * 100) + (15 if "MOAT" in data["moat"] else 0)

        mom_score = 0
        if "BULLISH TREND" in data["signal"]: mom_score += 30
        if data["vol_surge"]: mom_score += 20
        if isinstance(data["rsi"], (int, float)) and 40 <= data["rsi"] <= 65: mom_score += 15
        data["scores"]["momentum"] = mom_score

        data["scores"]["growth"] = (15 if data["sector"] in ["Technology", "Consumer Staples", "Fintech / Wealth"] else 5) + (10 if data["moat"] != "MODERATE MOAT" else 0)
        data["scores"]["compounder"] = (data["div_yield"] * 50) + (20 if data["short_debt"] != "N/A" else 5)

        analyzed_stocks.append(data)

    return analyzed_stocks

def allocate_top_8_buckets(stock_data_list):
    selected_tickers = set()
    recommendations = []

    def get_top_candidates(score_key, limit=2):
        sorted_stocks = sorted(
            [s for s in stock_data_list if s["ticker"] not in selected_tickers],
            key=lambda x: x["scores"][score_key],
            reverse=True
        )
        picked = sorted_stocks[:limit]
        for p in picked:
            selected_tickers.add(p["ticker"])
        return picked

    b1 = get_top_candidates("anchor", 2)
    b2 = get_top_candidates("momentum", 2)
    b3 = get_top_candidates("growth", 2)
    b4 = get_top_candidates("compounder", 2)

    for item in b1: recommendations.append({"bucket": "Blue Chip Anchor", "badge_class": "b-anchor", "data": item})
    for item in b2: recommendations.append({"bucket": "Short-Term Momentum", "badge_class": "b-momentum", "data": item})
    for item in b3: recommendations.append({"bucket": "Mid-Term Growth", "badge_class": "b-growth", "data": item})
    for item in b4: recommendations.append({"bucket": "Long-Term Compounder", "badge_class": "b-compounder", "data": item})

    return recommendations

def render_html_dashboard(all_stocks, top_8_recs):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    rec_cards_html = ""
    for rec in top_8_recs:
        stk = rec["data"]
        price_str = f"${stk['price']:.2f}" if isinstance(stk['price'], (int, float)) else "N/A"
        div_str = format_pct(stk["div_yield"])
        
        rec_cards_html += f"""
        <div class="rec-card" onclick="openModal('{stk['ticker']}')">
            <div class="bucket-tag {rec['badge_class']}">{rec['bucket']}</div>
            <div class="rec-header">
                <div>
                    <div class="rec-ticker">{stk['ticker']}</div>
                    <div class="rec-name">{stk['name']}</div>
                </div>
                <div class="rec-price">{price_str}</div>
            </div>
            <div class="rec-stats">
                <span>Signal: <strong>{stk['signal']}</strong></span>
                <span>Div Yield: <strong>{div_str}</strong></span>
                <span>P/B: <strong>{stk['pb_ratio']}</strong></span>
                <span>Moat: <strong>{stk['moat']}</strong></span>
            </div>
            <div class="chart-container">
                <canvas id="chart-{stk['ticker'].replace('.', '_')}"></canvas>
            </div>
        </div>
        """

    table_rows_html = ""
    for stk in all_stocks:
        price_str = f"${stk['price']:.2f}" if isinstance(stk['price'], (int, float)) else "N/A"
        div_str = format_pct(stk["div_yield"])
        chg = stk["change"]
        p_chg = stk["p_change"]
        
        if chg > 0:
            badge = f'<span class="badge pos">+${chg:.2f} (+{p_chg:.2f}%)</span>'
        elif chg < 0:
            badge = f'<span class="badge neg">-${abs(chg):.2f} ({p_chg:.2f}%)</span>'
        else:
            badge = '<span class="badge neu">$0.00 (0.00%)</span>'

        table_rows_html += f"""
        <tr onclick="openModal('{stk['ticker']}')" style="cursor: pointer;">
            <td><strong>{stk['ticker']}</strong></td>
            <td>{stk['name']}<br><small class="text-muted">{stk['sector']}</small></td>
            <td><strong>{price_str}</strong></td>
            <td>{badge}</td>
            <td><span class="signal-tag">{stk['signal']}</span></td>
            <td>{div_str}</td>
            <td>{stk['pb_ratio']}</td>
            <td>{stk['mkt_cap']}</td>
            <td><button class="btn-detail">Deep Dive & Chart</button></td>
        </tr>
        """

    json_data = {s["ticker"]: s for s in all_stocks}

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SGX Stock Scanner Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; background: #0b1120; color: #f8fafc; }}
        .container {{ max-width: 1380px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 24px; }}
        h1 {{ font-size: 1.8rem; margin: 0; color: #38bdf8; }}
        .text-muted {{ color: #94a3b8; font-size: 0.85rem; }}
        .section-title {{ font-size: 1.25rem; font-weight: 700; color: #f1f5f9; margin-bottom: 16px; }}
        .rec-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 36px; }}
        .rec-card {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 16px; cursor: pointer; transition: transform 0.2s, border-color 0.2s; }}
        .rec-card:hover {{ transform: translateY(-3px); border-color: #38bdf8; }}
        .bucket-tag {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 10px; }}
        .b-anchor {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; }}
        .b-momentum {{ background: rgba(250, 204, 21, 0.2); color: #facc15; }}
        .b-growth {{ background: rgba(74, 222, 128, 0.2); color: #4ade80; }}
        .b-compounder {{ background: rgba(192, 132, 252, 0.2); color: #c084fc; }}
        .rec-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
        .rec-ticker {{ font-size: 1.1rem; font-weight: 800; color: #f8fafc; }}
        .rec-name {{ font-size: 0.8rem; color: #94a3b8; }}
        .rec-price {{ font-size: 1.2rem; font-weight: 700; color: #f8fafc; }}
        .rec-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.75rem; color: #cbd5e1; margin-bottom: 12px; background: #0f172a; padding: 8px; border-radius: 6px; }}
        .chart-container {{ height: 90px; width: 100%; }}
        .table-card {{ background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow-x: auto; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem; }}
        th {{ background: #0f172a; padding: 14px 16px; color: #cbd5e1; font-weight: 600; border-bottom: 1px solid #334155; text-transform: uppercase; font-size: 0.75rem; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #334155; vertical-align: middle; }}
        tr:hover {{ background: #26354a; }}
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }}
        .pos {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; }}
        .neg {{ background: rgba(239, 68, 68, 0.15); color: #f87171; }}
        .neu {{ background: rgba(148, 163, 184, 0.15); color: #cbd5e1; }}
        .signal-tag {{ font-weight: 700; font-size: 0.75rem; color: #38bdf8; }}
        .btn-detail {{ background: #0284c7; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.75rem; }}
        
        /* Modal Styling */
        .modal {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); justify-content: center; align-items: center; z-index: 100; padding: 20px; }}
        .modal-content {{ background: #1e293b; max-width: 900px; width: 100%; max-height: 92vh; border-radius: 12px; border: 1px solid #475569; overflow-y: auto; padding: 24px; position: relative; }}
        .close-btn {{ position: absolute; top: 16px; right: 20px; font-size: 1.5rem; color: #94a3b8; cursor: pointer; }}
        .modal-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; background: #0f172a; padding: 16px; border-radius: 8px; }}
        .data-table {{ width: 100%; margin-top: 12px; border: 1px solid #334155; }}
        .data-table th, .data-table td {{ border: 1px solid #334155; padding: 8px; text-align: center; font-size: 0.8rem; }}
        
        /* Interactive Chart Controls */
        .modal-chart-box {{ background: #0f172a; padding: 16px; border-radius: 8px; margin: 16px 0; }}
        .tf-btn-group {{ display: flex; gap: 8px; margin-bottom: 12px; justify-content: flex-end; }}
        .tf-btn {{ background: #334155; color: #cbd5e1; border: none; padding: 5px 12px; border-radius: 4px; font-weight: 600; font-size: 0.75rem; cursor: pointer; transition: all 0.2s; }}
        .tf-btn.active, .tf-btn:hover {{ background: #0284c7; color: white; }}
        .big-chart-container {{ height: 260px; width: 100%; position: relative; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>SGX Stock Scanner Dashboard</h1>
                <div class="text-muted">STI 30 + Mid-Caps • Batch Download Enabled</div>
            </div>
            <div class="text-muted">Updated: {timestamp}</div>
        </div>

        <div class="section-title">⭐ Top 8 Recommended Opportunities</div>
        <div class="rec-grid">
            {rec_cards_html}
        </div>

        <div class="section-title">📊 Full SGX Stock Universe Scan</div>
        <div class="table-card">
            <table>
                <thead>
                    <tr>
                        <th>Ticker</th>
                        <th>Company & Sector</th>
                        <th>Price (SGD)</th>
                        <th>Day Change</th>
                        <th>Signal</th>
                        <th>Div Yield</th>
                        <th>P/B Ratio</th>
                        <th>Market Cap</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <div id="deepDiveModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeModal()">&times;</span>
            <h2 id="m-title" style="margin:0; color:#38bdf8;">Stock Detail</h2>
            <div id="m-subtitle" class="text-muted" style="margin-bottom:12px;">Sector</div>
            
            <div class="modal-chart-box">
                <div class="tf-btn-group">
                    <button class="tf-btn" onclick="updateModalChart('1M')">1M</button>
                    <button class="tf-btn" onclick="updateModalChart('3M')">3M</button>
                    <button class="tf-btn" onclick="updateModalChart('6M')">6M</button>
                    <button class="tf-btn active" onclick="updateModalChart('1Y')">1Y</button>
                </div>
                <div class="big-chart-container">
                    <canvas id="modalChartCanvas"></canvas>
                </div>
            </div>

            <div class="modal-grid">
                <div>Short-Term Debt: <strong id="m-st-debt">N/A</strong></div>
                <div>Long-Term Debt: <strong id="m-lt-debt">N/A</strong></div>
                <div>Cash Assets: <strong id="m-cash">N/A</strong></div>
                <div>PPE / Buildings: <strong id="m-ppe">N/A</strong></div>
                <div>Intrinsic Value: <strong id="m-intrinsic">N/A</strong></div>
                <div>Economic Moat: <strong id="m-moat">N/A</strong></div>
            </div>

            <h3 style="font-size:1rem; margin-top:16px;">5-Year Financial & Cash Flow Statement</h3>
            <table class="data-table">
                <thead>
                    <tr id="m-hist-years"><th>Metric</th></tr>
                </thead>
                <tbody>
                    <tr id="m-hist-rev"><td>Revenue</td></tr>
                    <tr id="m-hist-net"><td>Net Income</td></tr>
                    <tr id="m-hist-ocf"><td>Op. Cash Flow</td></tr>
                    <tr id="m-hist-fcf"><td>Free Cash Flow</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const stockData = {json.dumps(json_data)};
        const recData = {json.dumps([r['data']['ticker'] for r in top_8_recs])};
        let modalChartInstance = null;
        let activeModalTicker = null;

        window.onload = function() {{
            recData.forEach(ticker => {{
                const item = stockData[ticker];
                if (item && item.hist_prices && item.hist_prices.length > 0) {{
                    const canvasId = 'chart-' + ticker.replace('.', '_');
                    const ctx = document.getElementById(canvasId);
                    if (ctx) {{
                        new Chart(ctx, {{
                            type: 'line',
                            data: {{
                                labels: item.hist_labels,
                                datasets: [{{
                                    data: item.hist_prices,
                                    borderColor: '#38bdf8',
                                    borderWidth: 2,
                                    fill: false,
                                    pointRadius: 0
                                }}]
                            }},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {{ legend: {{ display: false }} }},
                                scales: {{ x: {{ display: false }}, y: {{ display: false }} }}
                            }}
                        }});
                    }}
                }}
            }});
        }};

        function openModal(ticker) {{
            const item = stockData[ticker];
            if (!item) return;

            activeModalTicker = ticker;

            document.getElementById('m-title').innerText = item.ticker + ' - ' + item.name;
            document.getElementById('m-subtitle').innerText = item.sector + ' | ' + item.mkt_cap + ' Market Cap';
            document.getElementById('m-st-debt').innerText = item.short_debt;
            document.getElementById('m-lt-debt').innerText = item.long_debt;
            document.getElementById('m-cash').innerText = item.assets_cash;
            document.getElementById('m-ppe').innerText = item.assets_ppe;
            document.getElementById('m-intrinsic').innerText = item.intrinsic_val;
            document.getElementById('m-moat').innerText = item.moat;

            const yearsHeader = '<th>Metric</th>' + (item.years && item.years.length > 0 ? item.years.map(y => `<th>${{y}}</th>`).join('') : '<th>N/A</th>');
            document.getElementById('m-hist-years').innerHTML = yearsHeader;
            
            document.getElementById('m-hist-rev').innerHTML = '<td>Revenue</td>' + (item.revenue && item.revenue.length > 0 ? item.revenue.map(v => `<td>${{v}}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-net').innerHTML = '<td>Net Income</td>' + (item.net_income && item.net_income.length > 0 ? item.net_income.map(v => `<td>${{v}}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-ocf').innerHTML = '<td>Op Cashflow</td>' + (item.ocf && item.ocf.length > 0 ? item.ocf.map(v => `<td>${{v}}</td>`).join('') : '<td>N/A</td>');
            document.getElementById('m-hist-fcf').innerHTML = '<td>Free Cashflow</td>' + (item.fcf && item.fcf.length > 0 ? item.fcf.map(v => `<td>${{v}}</td>`).join('') : '<td>N/A</td>');

            document.getElementById('deepDiveModal').style.display = 'flex';
            
            // Render 1Y chart by default
            updateModalChart('1Y');
        }}

        function updateModalChart(timeframe) {{
            if (!activeModalTicker || !stockData[activeModalTicker]) return;

            const item = stockData[activeModalTicker];
            const dates = item.daily_dates || [];
            const prices = item.daily_prices || [];

            if (dates.length === 0 || prices.length === 0) return;

            // Highlight active button
            const buttons = document.querySelectorAll('.tf-btn');
            buttons.forEach(btn => {{
                if (btn.innerText === timeframe) btn.classList.add('active');
                else btn.classList.remove('active');
            }});

            // Slice dataset according to timeframe
            let count = dates.length;
            if (timeframe === '1M') count = Math.min(21, dates.length);
            else if (timeframe === '3M') count = Math.min(63, dates.length);
            else if (timeframe === '6M') count = Math.min(126, dates.length);

            const filteredDates = dates.slice(-count);
            const filteredPrices = prices.slice(-count);

            const ctx = document.getElementById('modalChartCanvas').getContext('2d');

            if (modalChartInstance) {{
                modalChartInstance.destroy();
            }}

            modalChartInstance = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: filteredDates,
                    datasets: [{{
                        label: 'Price (SGD)',
                        data: filteredPrices,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 1,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{ mode: 'index', intersect: false }}
                    }},
                    scales: {{
                        x: {{
                            grid: {{ color: '#1e293b' }},
                            ticks: {{ color: '#94a3b8', maxTicksLimit: 8 }}
                        }},
                        y: {{
                            grid: {{ color: '#1e293b' }},
                            ticks: {{ color: '#94a3b8' }}
                        }}
                    }}
                }}
            }});
        }}

        function closeModal() {{
            document.getElementById('deepDiveModal').style.display = 'none';
        }}
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_doc)
    print("✅ Dashboard generated successfully: index.html")

def main():
    print(f"Starting SGX scanner...")
    analyzed = analyze_universe_batch(STOCK_UNIVERSE)
    top_8 = allocate_top_8_buckets(analyzed)
    render_html_dashboard(analyzed, top_8)

if __name__ == "__main__":
    main()
