import json
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from .fetcher import fetch_headlines


log = logging.getLogger("news_bot.site")


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    raw_sources = os.getenv("NEWS_SOURCES", "")
    raw_max = os.getenv("MAX_PER_SOURCE", "5").strip()
    max_per_source = int(raw_max) if raw_max else 5
    output_path = os.getenv("OUTPUT_PATH", "docs/data.json")

    if not raw_sources:
        log.error("Missing NEWS_SOURCES in environment")
        return 1

    sources = [s.strip() for s in raw_sources.split(",") if s.strip()]
    headlines = fetch_headlines(sources, max_per_source=max_per_source)

    payload = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(headlines),
        "items": headlines,
    }

    out_dir = os.path.dirname(output_path) or "."
    os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")

    log.info("Wrote %d headlines to %s", len(headlines), output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
