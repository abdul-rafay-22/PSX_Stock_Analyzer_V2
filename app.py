import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from scraper import get_market_data, get_kse25_only, get_historical_yfinance_data
from analysis import run_all_analysis, get_top_gainers, get_top_losers, get_sector_performance, get_52_week_high_low

st.set_page_config(
    page_title="KSE-100 Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

st.title("📈 KSE-25 Stock Market Analyzer")
st.caption("Live market data simplified for everyone — educational purposes only, not financial advice.")
st.divider()

@st.cache_data(ttl=300)
def load_data():
    # 1. Fetch live PSX Data
    raw_live_data = get_market_data()
    latest_df = get_kse25_only(raw_live_data)
    
    # 2. Fetch historical yfinance data for charts
    all_df = get_historical_yfinance_data(period="6mo") 
    all_df = run_all_analysis(all_df)
    
    return all_df, latest_df

with st.spinner("Fetching live KSE-100 data from PSX..."):
    all_df, latest_df = load_data()

if latest_df.empty:
    st.error("Could not fetch live data. Check your internet connection or PSX website status.")
    st.stop()

st.subheader("🗂️ Market Snapshot")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_change = latest_df["change_pct"].mean()
    st.metric("Market Avg Change", f"{avg_change:.2f}%")

with col2:
    gainers_count = len(latest_df[latest_df["change_pct"] > 0])
    st.metric("Stocks Up Today", gainers_count)

with col3:
    losers_count = len(latest_df[latest_df["change_pct"] < 0])
    st.metric("Stocks Down Today", losers_count)

with col4:
    top_stock = latest_df.loc[latest_df["current"].idxmax(), "symbol"]
    st.metric("Highest Priced Stock", top_stock)

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🟢 Top 5 Gainers")
    gainers = get_top_gainers(latest_df)
    st.dataframe(
        gainers[["symbol", "company", "current", "change_pct", "volume"]],
        use_container_width=True,
        hide_index=True
    )
with col_right:
    st.subheader("🔴 Top 5 Losers")
    losers = get_top_losers(latest_df)
    st.dataframe(
        losers[["symbol", "company", "current", "change_pct", "volume"]],
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("🏭 Sector Performance")
sector_df = get_sector_performance(latest_df)
if not sector_df.empty:
    fig_sector = px.bar(
        sector_df,
        x="Sector",
        y="Avg Change %",
        color="Avg Change %",
        color_continuous_scale=["red", "yellow", "green"],
        title="Average % Change by Sector Today"
    )
    st.plotly_chart(fig_sector, use_container_width=True)
else:
    st.info("Not enough sector data available currently.")
st.divider()

st.subheader("🔎 Analyze a Stock")

selected_stock = st.selectbox(
    "Select a company to analyze",
    options=latest_df["symbol"].tolist()
)

stock_df_historical = all_df[all_df["Company"] == selected_stock].copy()
current_live_data = latest_df[latest_df["symbol"] == selected_stock].iloc[0]

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("Current Price", f"PKR {current_live_data['current']:,.2f}")
with col_b:
    st.metric("Today's Change", f"{current_live_data['change_pct']:.2f}%")
with col_c:
    st.metric("Volume", f"{current_live_data['volume']:,}")

if not stock_df_historical.empty:
    fig_candle = go.Figure(data=[go.Candlestick(
        x=stock_df_historical["Date"],
        open=stock_df_historical["Open"],
        high=stock_df_historical["High"],
        low=stock_df_historical["Low"],
        close=stock_df_historical["Close"],
        name=selected_stock
    )])

    fig_candle.add_trace(go.Scatter(
        x=stock_df_historical["Date"],
        y=stock_df_historical["MA50"],
        name="50-Day MA",
        line=dict(color="orange", width=1.5)
    ))

    fig_candle.update_layout(
        title=f"{selected_stock} — 6 Month Price History",
        xaxis_title="Date",
        yaxis_title="Price (PKR)",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig_candle, use_container_width=True)

    st.subheader("📊 6-Month Range")
    week_df = get_52_week_high_low(all_df)
    
    if not week_df[week_df["Company"] == selected_stock].empty:
        stock_week = week_df[week_df["Company"] == selected_stock].iloc[0]
        col_x, col_y = st.columns(2)
        with col_x:
            st.metric("6-Month High", f"PKR {stock_week['High_52W']:,.2f}")
        with col_y:
            st.metric("6-Month Low", f"PKR {stock_week['Low_52W']:,.2f}")
            
    st.subheader("⚡ Price Volatility (30-Day Rolling)")
    fig_vol = px.line(
        stock_df_historical,
        x="Date",
        y="Volatility",
        title=f"{selected_stock} — Volatility Over Time"
    )
    st.plotly_chart(fig_vol, use_container_width=True)
else:
    st.warning("Historical data is currently unavailable for this specific stock.")
st.divider()
st.caption("Live data sourced directly from PSX. Historical charts powered by yfinance.")