# Daily Stock Performance Report

Python-based automation that fetches real-time stock data and emails a formatted daily report at market close.

## Author
Nathan Kinert | 25+ years Industrial Reliability | MLA | MLT  
IIoT | Predictive Maintenance | Data Analytics | Heavy Industrial  
[GitHub Portfolio](https://github.com/nkinert)

## What This Project Does
- Fetches the top 5 Yahoo Finance market headlines of the day
- Pulls closing price and daily % change for a custom stock watchlist
- Generates a clean HTML email with color-coded performance indicators (▲/▼)
- Sends automatically via Gmail SMTP, scheduled daily on PythonAnywhere

## Tools & Libraries
- Python
- yfinance
- feedparser
- smtplib
- PythonAnywhere

## Data Source
Yahoo Finance (via yfinance API)

## Security
Email credentials managed via environment variables — no hardcoded passwords.

## Disclaimer
Not financial advice. For personal tracking purposes only.
