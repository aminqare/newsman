NewsPaperMan — Telegram news headlines sender

Overview

This small Python project fetches headlines from RSS feeds and posts them to your Telegram chat every 3 hours.

Quickstart

1. Create a Python virtualenv and activate it.

   python3 -m venv .venv
   source .venv/bin/activate

2. Install dependencies

   pip install -r requirements.txt

3. Copy `.env.example` to `.env` and fill in your `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, and `NEWS_SOURCES` (plus optional GDELT settings).

4. Run the service

   python -m news_bot.main

Files

- [requirements.txt](requirements.txt)
- [.env.example](.env.example)
- [news_bot/main.py](news_bot/main.py)
- [news_bot/fetcher.py](news_bot/fetcher.py)
- [news_bot/telegram_sender.py](news_bot/telegram_sender.py)

Notes

- `NEWS_SOURCES` should be a comma-separated list of RSS feed URLs.
- The scheduler sends updates immediately on start and then every 3 hours.
- To run as a background service, consider using a systemd unit, Docker container, or process manager like `supervisord`.
- Optional GDELT queries can be added via `GDELT_QUERIES` for broader coverage.
