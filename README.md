# KSE-25 Stock Market Analyzer — V2

A real-time stock market dashboard for Pakistan's top 25 companies (KSE-25), built with Streamlit.

**V2** scrapes all data — live and historical — directly from the [PSX Data Portal](https://dps.psx.com.pk). No Yahoo Finance, no API keys, no third-party data providers.

> For educational purposes only. Not financial advice.

---

## What's New in V2

- **Direct PSX scraping** — all data is fetched straight from `dps.psx.com.pk`
- **No Yahoo Finance** — removed `yfinance` dependency entirely
- **Full OHLCV history** — historical Open, High, Low, Close, Volume data scraped via PSX's own historical endpoint
- **Parallel fetching** — 10 concurrent threads for fast historical data loading
- **KSE-25 focus** — narrowed down from KSE-100 to the top 25 stocks for cleaner analysis

---

## Features

- **Live Market Snapshot** — current price, daily change %, and volume for all KSE-25 stocks
- **Top 5 Gainers & Losers** — updated every 5 minutes
- **Sector Performance** — average % change by sector as a bar chart
- **Individual Stock Analysis:**
  - Candlestick chart with 50-day moving average (6-month history)
  - 6-month High / Low range
  - 30-day rolling volatility chart

---

## Project Structure

```
PSX_Project/
├── app.py          # Streamlit UI and layout
├── scraper.py      # PSX web scrapers (live + historical)
└── analysis.py     # Technical indicators and data transformations
```

---

## How It Works

| Data | Source | Method |
|---|---|---|
| Live prices | `dps.psx.com.pk/market-watch` | GET → HTML parse |
| KSE-25 constituents | `dps.psx.com.pk/KSE25` | GET → HTML parse |
| Historical OHLCV | `dps.psx.com.pk/historical` | POST per month → HTML parse |

Historical data is fetched in parallel (10 threads) — 25 stocks × 6 months = 150 requests completing in ~5–10 seconds. Results are cached for 5 minutes via `@st.cache_data`.

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/kse25-analyzer.git
cd kse25-analyzer
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install streamlit plotly pandas requests beautifulsoup4 lxml
```

**4. Run the app**
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `plotly` | Interactive charts |
| `pandas` | Data manipulation |
| `requests` | HTTP scraping |
| `beautifulsoup4` | HTML parsing |
| `lxml` | HTML parser backend |

---

## Disclaimer

This project is built for educational and learning purposes. Data is sourced from the Pakistan Stock Exchange public portal. Nothing in this dashboard constitutes financial advice. Always do your own research before making investment decisions.
