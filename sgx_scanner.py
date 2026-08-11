import yfinance as yf
import pandas as pd
import numpy as np

# Top SGX Stocks with correct Yahoo Finance suffix (.SI)
SGX_TICKERS = [
    "D05.SI",   # DBS Group Holdings
    "O39.SI",   # OCBC Bank
    "U11.SI",   # UOB
    "Z74.SI",   # Singtel
    "BN4.SI",   # Keppel Ltd
    "F34.SI",   # Wilmar International
    "C38U.SI",  # CapitaLand Integrated Commercial Trust
    "A17U.SI"   # CapitaLand Ascendas REIT
]

def get_financial_row(df, keywords):
    """Safely retrieves a row from yfinance Financials/Balance Sheet DataFrame by matching keywords."""
    if df is None or df.empty:
        return None
    for idx in df.index:
        idx_str = str(idx).lower()
        if any(kw.lower() in idx_str for kw in keywords):
            return df.loc[idx]
    return None

def fetch_sgx_stock_data(ticker_symbol):
    """Fetches key stock info, 5-year price history, and 5-year financials from Yahoo Finance."""
    print(f"Fetching data for {ticker_symbol}...")
    stock = yf.Ticker(ticker_symbol)
    
    # 1. Fetch Info Safely
    try:
        info = stock.info or {}
    except Exception as e:
        print(f"  Warning: Could not fetch info for {ticker_symbol}: {e}")
        info = {}
        
    price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('navPrice') or 0.0
    pe_ratio = info.get('trailingPE')
    pb_ratio = info.get('priceToBook')
    div_yield = info.get('dividendYield')
    if div_yield is not None and div_yield < 1.0:
        div_yield *= 100 # Convert decimal to percentage if needed
        
    market_cap = info.get('marketCap', 0)
    company_name = info.get('shortName') or info.get('longName') or ticker_symbol

    # 2. Fetch 5-Year Historical Prices
    try:
        hist_5y = stock.history(period="5y")
    except Exception as e:
        hist_5y = pd.DataFrame()

    # 3. Fetch Financial Statements
    try:
        financials = stock.financials
    except Exception as e:
        financials = pd.DataFrame()

    # Extract Revenue and Net Income safely
    revenue_series = get_financial_row(financials, ['total revenue', 'operating revenue', 'revenue'])
    net_income_series = get_financial_row(financials, ['net income', 'net income common stockholders'])

    # Format 5-Year Financial Summary
    financial_summary = []
    if revenue_series is not None:
        for date, rev in revenue_series.items():
            year = str(date)[:4] if hasattr(date, 'year') else str(date)
            net_inc = net_income_series[date] if (net_income_series is not None and date in net_income_series) else np.nan
            financial_summary.append({
                'Year': year,
                'Revenue (SGD)': rev,
                'Net Income (SGD)': net_inc
            })

    return {
        'Ticker': ticker_symbol,
        'Name': company_name,
        'Price': price,
        'PE_Ratio': pe_ratio if pe_ratio else 'N/A',
        'PB_Ratio': pb_ratio if pb_ratio else 'N/A',
        'Dividend_Yield_%': round(div_yield, 2) if div_yield else 'N/A',
        'Market_Cap': market_cap,
        'History_5Y': hist_5y,
        'Financials_5Y': pd.DataFrame(financial_summary)
    }

def run_sgx_scanner():
    results = []
    for ticker in SGX_TICKERS:
        try:
            data = fetch_sgx_stock_data(ticker)
            results.append(data)
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            
    summary_df = pd.DataFrame([{
        'Ticker': r['Ticker'],
        'Name': r['Name'],
        'Price (SGD)': r['Price'],
        'P/E': r['PE_Ratio'],
        'P/B': r['PB_Ratio'],
        'Div Yield (%)': r['Dividend_Yield_%']
    } for r in results])
    
    return summary_df, results

if __name__ == "__main__":
    df_summary, raw_data = run_sgx_scanner()
    print("\n--- SGX Stock Scanner Summary ---")
    print(df_summary.to_string(index=False))
