from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import smtplib

load_dotenv()

HEADERS = {
    'Accept-Language' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    'User-Agent':"en-US,en;q=0.9,te;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "priority": "u=0, i",
    "sec-ch-ua-platform": "Windows",
}

URL = os.getenv("AMAZON_PRODUCT_URL")
BUY_PRICE = int(os.getenv("TARGET_PRICE"))

def fetch_price_data(url):
    """Fetches and parses price data from the Amazon product page."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_text = soup.select_one('.a-price-whole')
        if price_text:
            price = int(price_text.getText().replace(",", "").replace(".", ""))
            return price, soup.find(id="productTitle").getText().strip()
        else:
            print("Price data not found on the page.")
            return None, None
    except requests.RequestException as e:
        print(f"Error fetching the product page: {e}")
        return None, None

def send_email(subject, message):
    """Sends an email notification."""
    try:
        with smtplib.SMTP(os.environ["SMTP_ADDRESS"], port=587) as connection:
            connection.starttls()
            connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
            connection.sendmail(
                from_addr=os.environ["EMAIL_ADDRESS"],
                to_addrs=os.environ["EMAIL_ADDRESS"],
                msg=f"Subject:{subject}\n\n{message}".encode("utf-8")
            )
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main Logic
if __name__ == "__main__":
    price, title = fetch_price_data(URL)
    if price and price <= BUY_PRICE:
        subject = "Amazon Price Alert!"
        message = f"{title} is now {price} rupees. Check it out here: {URL}"
        send_email(subject, message)
    else:
        print(f"Price is {price}. Target price is {BUY_PRICE}.")    