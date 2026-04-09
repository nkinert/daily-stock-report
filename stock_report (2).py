"""
Daily Stock Performance Report
================================
Fetches stock prices and emails a report with top market headlines.

Setup:
    pip install yfinance feedparser

PythonAnywhere:
    - Upload this file to your PythonAnywhere account
    - Schedule it under Tasks > Daily task
    - Set the command to:  python3 /home/Bananassassin/stock_report.py
"""

import yfinance as yf
import smtplib
import feedparser
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- YOUR SETTINGS -----------------------------------------------------------

MY_STOCKS = [
    "AAPL", "ALL", "CAT", "NVDA", "MSFT", "AMZN",
    "COPX", "CRPT", "GBTC", "GLDM", "GOOG",
    "PSTG", "QQQ", "QQQM", "VGT", "VXUS", "XSD"
]

EMAIL_FROM     = "nkinert@gmail.com"
EMAIL_TO       = "nkinert@gmail.com"
EMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# -----------------------------------------------------------------------------


def fetch_market_headlines():
    """Fetch top financial headlines from Yahoo Finance RSS."""
    try:
        feed = feedparser.parse("https://finance.yahoo.com/news/rssindex")
        headlines = []
        for entry in feed.entries[:5]:
            headlines.append({
                "title": entry.title,
                "link":  entry.link
            })
        print(f"  Fetched {len(headlines)} headlines")
        return headlines
    except Exception as e:
        print(f"  Headlines fetch failed: {e}")
        return []


def fetch_stock_data(ticker):
    """Fetch today's performance for a single stock."""
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period="1mo")
        if hist.empty or len(hist) < 2:
            return None

        latest_close     = hist["Close"].iloc[-1]
        previous_close   = hist["Close"].iloc[-2]
        daily_change_pct = ((latest_close - previous_close) / previous_close) * 100

        try:
            name = stock.info.get("shortName", ticker)
        except Exception:
            name = ticker

        return {
            "ticker":           ticker,
            "name":             name,
            "latest_close":     round(latest_close, 2),
            "daily_change_pct": round(daily_change_pct, 2),
        }
    except Exception as e:
        print(f"  {ticker}: ERROR — {e}")
        return None


def build_html_body(stock_data_list, headlines=None):
    """Build a clean HTML email body."""
    date_str = datetime.today().strftime("%A, %B %d %Y")

    # Headlines block
    if headlines:
        headline_rows = ""
        for h in headlines:
            headline_rows += f"""
            <tr>
              <td style="padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:14px;
                         line-height:1.5">
                <a href="{h['link']}" style="color:#1a1a1a;text-decoration:none">
                  {h['title']}
                </a>
              </td>
            </tr>"""

        headlines_block = f"""
        <div style="margin-bottom:28px">
          <div style="font-size:11px;font-weight:bold;color:#3a5bd9;
                      text-transform:uppercase;letter-spacing:.06em;margin-bottom:12px">
            Market Headlines
          </div>
          <table style="width:100%;border-collapse:collapse">
            {headline_rows}
          </table>
        </div>"""
    else:
        headlines_block = ""

    # Stock rows
    rows = ""
    for d in stock_data_list:
        change = d["daily_change_pct"]
        color  = "#00c853" if change >= 0 else "#d50000"
        sign   = "+" if change >= 0 else ""
        arrow  = "▲" if change >= 0 else "▼"
        rows += f"""
        <tr>
            <td style="padding:10px;font-weight:bold">{d['ticker']}</td>
            <td style="padding:10px">{d['name']}</td>
            <td style="padding:10px">${d['latest_close']}</td>
            <td style="padding:10px;color:{color};font-weight:bold">{arrow} {sign}{change}%</td>
        </tr>"""

    return f"""
    <html><body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px">
      <div style="max-width:700px;margin:auto;background:white;border-radius:12px;
                  overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.1)">
        <div style="background:#111;padding:24px;color:white">
          <h1 style="margin:0;font-size:22px">Daily Stock Report</h1>
          <p style="margin:6px 0 0;color:#aaa">{date_str}</p>
        </div>
        <div style="padding:24px">
          {headlines_block}
          <table style="width:100%;border-collapse:collapse;font-size:15px">
            <thead>
              <tr style="background:#f0f0f0">
                <th style="padding:10px;text-align:left">Ticker</th>
                <th style="padding:10px;text-align:left">Company</th>
                <th style="padding:10px;text-align:left">Close</th>
                <th style="padding:10px;text-align:left">Today</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <div style="padding:16px 24px;background:#f9f9f9;color:#999;font-size:12px">
          Data via Yahoo Finance &nbsp;·&nbsp; Not financial advice.
        </div>
      </div>
    </body></html>
    """


def send_report():
    """Fetch all stock data and send the email report."""

    print("\nFetching market headlines...")
    headlines = fetch_market_headlines()

    print("\nFetching stock data, please wait...")
    stock_data_list = []
    for ticker in MY_STOCKS:
        data = fetch_stock_data(ticker)
        if data:
            stock_data_list.append(data)
            print(f"  {ticker}: ${data['latest_close']} ({data['daily_change_pct']:+.2f}%)")
        else:
            print(f"  {ticker}: could not fetch")

    if not stock_data_list:
        print("No data fetched. Aborting.")
        return

    print("\nBuilding email...")
    html_body = build_html_body(stock_data_list, headlines)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Stock Report — {datetime.today().strftime('%A, %b %d')}"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))

    print("Sending via Gmail SMTP...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print(f"\nDone! Report sent to {EMAIL_TO}")


# --- Run it! -----------------------------------------------------------------

if __name__ == "__main__":
    send_report()
