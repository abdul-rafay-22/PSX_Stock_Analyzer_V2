import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_market_data():
    url = "https://dps.psx.com.pk/market-watch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dps.psx.com.pk",
        "X-Requested-With": "XMLHttpRequest"
    }
    print("Fetching live data from PSX...")
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    rows = soup.find("tbody", class_="tbl__body").find_all("tr")

    all_stocks = []

    for row in rows:
        try:
            cells = row.find_all("td")

            symbol = cells[0].get("data-search", "").strip()

            company = cells[0].find("a").get("data-title", "").strip()
            sector = cells[1].text.strip()
            ldcp = float(cells[3].get("data-order", 0))      # last day closing price
            open_price = float(cells[4].get("data-order", 0))
            high = float(cells[5].get("data-order", 0))
            low = float(cells[6].get("data-order", 0))
            current = float(cells[7].get("data-order", 0))
            change = float(cells[8].get("data-order", 0))
            change_pct = float(cells[9].get("data-order", 0))
            volume = int(float(cells[10].get("data-order", 0)))

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            all_stocks.append({
                "symbol": symbol,
                "company": company,
                "sector": sector,
                "ldcp": ldcp,
                "open": open_price,
                "high": high,
                "low": low,
                "current": current,
                "change": change,
                "change_pct": change_pct,
                "volume": volume,
                "timestamp": timestamp
            })

        except Exception as e:
            continue

    df = pd.DataFrame(all_stocks)
    print(f"Fetched {len(df)} stocks from PSX")
    return df

def get_kse100_only(df):
    # PSX includes all listed stocks — we filter KSE100 using the listed column
    # KSE100 stocks have KSE100 in their listed indices
    kse100 = df[df["symbol"].isin(get_kse100_symbols())]
    print(f"Filtered to {len(kse100)} KSE-100 stocks")
    return kse100

def get_kse100_symbols():
    # fetch KSE100 constituent symbols directly from PSX
    url = "https://dps.psx.com.pk/KSE100"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dps.psx.com.pk"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    symbols = []
    rows = soup.find("tbody").find_all("tr") if soup.find("tbody") else []

    for row in rows:
        cells = row.find_all("td")
        if cells:
            symbol = cells[0].get("data-search", "").strip()
            if symbol:
                symbols.append(symbol)

    if not symbols:
        symbols = [
            "OGDC", "PPL", "PSO", "HBL", "UBL", "MCB", "LUCK", "FFC",
            "HUBC", "MARI", "BAHL", "MEBL", "NBP", "POL", "SEARL",
            "COLG", "NESTLE", "SNGP", "EFERT", "FATIMA", "ENGRO",
            "AIRLINK", "SYS", "TRG", "GHNI", "GAL", "SAZEW", "MTL",
            "ATLH", "INDU", "HCAR", "PAEL", "ISL", "INIL", "MUGHAL",
            "CHCC", "MLCF", "DGKC", "FCCL", "LUCK", "PIOC", "KOHC",
            "BWCL", "ACPL", "THCCL", "DCR", "JVDC", "TPLRF1", "GRR",
            "SHFA", "AGP", "GLAXO", "ABOT", "HINOON", "HALEON",
            "NATF", "SEARL", "CPHL", "ILP", "NML", "KTML", "GATM"
        ]

    return symbols

def get_kse25_symbols():
    url = "https://dps.psx.com.pk/KSE25"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dps.psx.com.pk"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        symbols = []
        rows = soup.find("tbody").find_all("tr") if soup.find("tbody") else []
        for row in rows:
            cells = row.find_all("td")
            if cells:
                symbol = cells[0].get("data-search", "").strip()
                if symbol:
                    symbols.append(symbol)
        if symbols:
            return symbols
    except Exception:
        pass

    return [
        "OGDC", "PPL", "PSO", "HBL", "UBL",
        "MCB", "LUCK", "FFC", "HUBC", "MARI",
        "BAHL", "MEBL", "ENGRO", "NBP", "POL",
        "SEARL", "SNGP", "EFERT", "SYS", "TRG",
        "INDU", "NESTLE", "COLG", "FATIMA", "MTL"
    ]

def get_kse25_only(df):
    kse25 = df[df["symbol"].isin(get_kse25_symbols())]
    print(f"Filtered to {len(kse25)} KSE-25 stocks")
    return kse25

def _scrape_month(symbol, month, year, headers):
    """Scrape one month of OHLCV data for a symbol via POST to /historical."""
    try:
        resp = requests.post(
            "https://dps.psx.com.pk/historical",
            data={"symbol": symbol, "month": str(month), "year": str(year)},
            headers=headers,
            timeout=15
        )
        soup = BeautifulSoup(resp.text, "lxml")
        table = soup.find("table")
        if not table:
            return []

        rows = []
        for tr in table.find("tbody").find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) < 6:
                continue
            try:
                rows.append({
                    "Company": symbol,
                    "Date":   pd.Timestamp(int(cells[0].get("data-order", 0)), unit="s"),
                    "Open":   float(cells[1].text.strip().replace(",", "") or 0),
                    "High":   float(cells[2].text.strip().replace(",", "") or 0),
                    "Low":    float(cells[3].text.strip().replace(",", "") or 0),
                    "Close":  float(cells[4].text.strip().replace(",", "") or 0),
                    "Volume": int(float(cells[5].text.strip().replace(",", "") or 0)),
                })
            except (ValueError, IndexError):
                continue
        return rows
    except Exception:
        return []

def get_historical_yfinance_data(period="6mo"):
    period_months = {"1mo": 1, "3mo": 3, "6mo": 6, "1y": 12}
    months_back = period_months.get(period, 6)

    today = datetime.today()
    month_list = []
    for i in range(months_back):
        d = today - timedelta(days=30 * i)
        month_list.append((d.month, d.year))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://dps.psx.com.pk/historical",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    symbols = get_kse25_symbols()
    tasks = [(sym, m, y) for sym in symbols for m, y in month_list]
    print(f"Scraping {period} OHLCV data: {len(symbols)} stocks × {months_back} months ({len(tasks)} requests)...")

    all_rows = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(_scrape_month, sym, m, y, headers): (sym, m, y)
                   for sym, m, y in tasks}
        for future in as_completed(futures):
            all_rows.extend(future.result())

    if not all_rows:
        print("Warning: No historical data fetched from PSX.")
        return pd.DataFrame(columns=["Company", "Date", "Open", "High", "Low", "Close", "Volume"])

    result = pd.DataFrame(all_rows)
    result = result.drop_duplicates(subset=["Company", "Date"])
    result = result.sort_values(["Company", "Date"]).reset_index(drop=True)
    print(f"Historical data scraped: {len(result)} rows for {result['Company'].nunique()} stocks")
    return result
