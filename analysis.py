import pandas as pd
import numpy as np

def calculate_moving_average(df):
    df["MA50"] = df.groupby("Company")["Close"].transform(lambda x: x.rolling(window=50, min_periods=1).mean())
    df["MA200"] = df.groupby("Company")["Close"].transform(lambda x: x.rolling(window=200, min_periods=1).mean())
    return df

def calculate_daily_returns(df):
    df["Daily_Return"] = df.groupby("Company")["Close"].pct_change() * 100
    return df

def calculate_volatility(df):
    df["Volatility"] = df.groupby("Company")["Daily_Return"].transform(lambda x: x.rolling(window=30, min_periods=1).std() * np.sqrt(252))
    return df

def get_52_week_high_low(df):
    result = df.groupby("Company")["Close"].agg(High_52W="max", Low_52W="min").reset_index()
    return result

def run_all_analysis(df):
    # Removed latest_df argument as it's not needed for historical calculations
    df = calculate_moving_average(df)
    df = calculate_daily_returns(df)
    df = calculate_volatility(df)
    return df

def get_top_movers(df, top_n=5):
    return df.sort_values(by="change_pct", ascending=False).head(top_n)

def get_top_gainers(df, top_n=5):
    return df.sort_values(by="change_pct", ascending=False).head(top_n)

def get_top_losers(df, top_n=5):
    return df.sort_values(by="change_pct", ascending=True).head(top_n)

def get_sector_performance(latest_df):
    sectors = {
        "Oil & Gas": ["OGDC", "PPL", "PSO", "MARI", "POL", "SNGP"],
        "Banking": ["HBL", "UBL", "MCB", "BAHL", "MEBL", "NBP"],
        "Cement & Industry": ["LUCK", "HUBC", "UNITY"],
        "FMCG": ["ENGRO", "FFC", "COLG", "NESTLE", "SEARL"]
    }
    
    sector_data = []

    for sector, companies in sectors.items():
        # Filter using the new 'symbol' column
        sector_df = latest_df[latest_df["symbol"].isin(companies)]

        if not sector_df.empty:
            avg_change = sector_df["change_pct"].mean()
            sector_data.append({
                "Sector": sector,
                "Avg Change %": round(avg_change, 2)
            })
    return pd.DataFrame(sector_data)