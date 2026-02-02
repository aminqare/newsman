import json
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from .fetcher import fetch_headlines_grouped


log = logging.getLogger("news_bot.site")


def main():
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    raw_sources = os.getenv("NEWS_SOURCES", "")
    raw_max = os.getenv("MAX_PER_SOURCE", "5").strip()
    max_per_source = int(raw_max) if raw_max else 5
    raw_summary = os.getenv("SUMMARY_LIMIT", "220").strip()
    summary_limit = int(raw_summary) if raw_summary else 220
    output_path = os.getenv("OUTPUT_PATH", "docs/data.json")

    if not raw_sources:
        log.error("Missing NEWS_SOURCES in environment")
        return 1

    sources = [s.strip() for s in raw_sources.split(",") if s.strip()]
    groups = fetch_headlines_grouped(
        sources, max_per_source=max_per_source, summary_limit=summary_limit
    )

    iran_items = []
    seen = set()
    for group in groups:
        for item in group.get("items", []):
            haystack = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            if "iran" not in haystack:
                continue
            key = f"{item.get('title')}|{item.get('link')}"
            if key in seen:
                continue
            seen.add(key)
            iran_items.append(item)

    payload = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": groups,
        "iran": iran_items,
    }

    out_dir = os.path.dirname(output_path) or "."
    os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2)
        f.write("\n")

    total_items = sum(len(g.get("items", [])) for g in groups)
    log.info("Wrote %d headlines to %s", total_items, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
