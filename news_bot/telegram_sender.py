import requests


def send_message(bot_token, chat_id, text, parse_mode="HTML"):
    """Send a message via Telegram Bot API.

    Raises requests.HTTPError on failure.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": False}
    resp = requests.post(url, data=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()
