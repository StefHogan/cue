import requests

ZEN_QUOTES_URL = "https://zenquotes.io/api/random"
FALLBACK_QUOTE = "The only way to do great work is to love what you do. — Steve Jobs"


def fetch_quote() -> str:
    try:
        response = requests.get(ZEN_QUOTES_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote = f"{data[0]['q']} — {data[0]['a']}"
    except (requests.RequestException, KeyError, IndexError, ValueError):
        quote = FALLBACK_QUOTE
    return f"Your quote of the day is: {quote}"
