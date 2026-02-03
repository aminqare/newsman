import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

from .fetcher import fetch_gdelt_headlines, fetch_headlines
from .telegram_sender import send_message


log = logging.getLogger("news_bot")


def build_message(headlines):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    if not headlines:
        return f"<b>News update — {now}</b>\n\nNo headlines found."

    lines = [f"<b>News update — {now}</b>\n"]
    for i, h in enumerate(headlines, start=1):
        title = h.get("title")
        link = h.get("link")
        source = h.get("source") or ""
        lines.append(f"{i}. <a href=\"{link}\">{title}</a> — {source}")

    return "\n".join(lines)


def job(bot_token, chat_id, sources, max_per_source, gdelt_queries, gdelt_timespan, gdelt_sort, gdelt_maxrecords):
    try:
        headlines = fetch_headlines(sources, max_per_source=max_per_source)
        if gdelt_queries:
            headlines.extend(
                fetch_gdelt_headlines(
                    gdelt_queries,
                    maxrecords=gdelt_maxrecords,
                    timespan=gdelt_timespan,
                    sort=gdelt_sort,
                )
            )
        msg = build_message(headlines)
        send_message(bot_token, chat_id, msg)
        log.info("Sent %d headlines", len(headlines))
    except Exception as e:
        log.exception("Failed to fetch or send headlines: %s", e)


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    raw_sources = os.getenv("NEWS_SOURCES", "")
    raw_max = os.getenv("MAX_PER_SOURCE", "5").strip()
    max_per_source = int(raw_max) if raw_max else 5
    run_once = os.getenv("RUN_ONCE", "").strip().lower() in {"1", "true", "yes", "y"}
    raw_gdelt = os.getenv("GDELT_QUERIES", "")
    gdelt_timespan = os.getenv("GDELT_TIMESPAN", "1day").strip()
    gdelt_sort = os.getenv("GDELT_SORT", "datedesc").strip()
    raw_gdelt_max = os.getenv("GDELT_MAXRECORDS", "25").strip()
    gdelt_maxrecords = int(raw_gdelt_max) if raw_gdelt_max else 25

    gdelt_queries = [q.strip() for q in raw_gdelt.split(",") if q.strip()]

    if not bot_token or not chat_id or (not raw_sources and not gdelt_queries):
        log.error(
            "Missing TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, or NEWS_SOURCES/GDELT_QUERIES in environment"
        )
        return

    sources = [s.strip() for s in raw_sources.split(",") if s.strip()]

    if run_once:
        job(
            bot_token,
            chat_id,
            sources,
            max_per_source,
            gdelt_queries,
            gdelt_timespan,
            gdelt_sort,
            gdelt_maxrecords,
        )
        return

    sched = BlockingScheduler()
    # run immediately once, then every 3 hours
    sched.add_job(
        job,
        "interval",
        hours=3,
        args=[
            bot_token,
            chat_id,
            sources,
            max_per_source,
            gdelt_queries,
            gdelt_timespan,
            gdelt_sort,
            gdelt_maxrecords,
        ],
        next_run_time=datetime.utcnow(),
    )

    log.info("Starting scheduler with %d sources", len(sources))
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down scheduler")


if __name__ == "__main__":
    main()
