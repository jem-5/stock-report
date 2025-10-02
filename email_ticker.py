import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
import os

STOCKS = ["SPY", "DIA"]
EMAIL_SENDER = os.environ["EMAIL_SENDER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_RECEIVER = os.environ["EMAIL_RECEIVER"]


def get_stock_data(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            prev_close = hist["Close"].iloc[-2]
            latest_close = hist["Close"].iloc[-1]
            change = (latest_close - prev_close) / prev_close * 100
            data.append((ticker, latest_close, change))
    return data


def format_html(data):
    today = date.today().strftime("%B %d, %Y")
    html = f"<h2>Daily Stock Report - {today}</h2>"
    html += "<table border='1' cellpadding='6' cellspacing='0'>"
    html += "<tr><th>Ticker</th><th>Close</th><th>Change</th></tr>"
    
    for ticker, price, change in data:
        color = "green" if change >= 0 else "red"
        html += f"<tr><td>{ticker}</td><td>${price:.2f}</td><td style='color:{color}'>{change:.2f}%</td></tr>"
    
    html += "</table>"
    return html


def send_email(subject, body_html):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject

    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())


def main():
    stock_data = get_stock_data(STOCKS)
    html_report = format_html(stock_data)
    send_email("📈 Daily Stock Report", html_report)
    print("Email sent!")

if __name__ == "__main__":
    main()
