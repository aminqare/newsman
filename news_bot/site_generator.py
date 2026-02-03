import hashlib
import json
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

from .fetcher import fetch_gdelt_grouped, fetch_headlines_grouped


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
    site_password = os.getenv("SITE_PASSWORD", "")
    raw_gdelt = os.getenv("GDELT_QUERIES", "")
    gdelt_timespan = os.getenv("GDELT_TIMESPAN", "1day").strip()
    gdelt_sort = os.getenv("GDELT_SORT", "datedesc").strip()
    raw_gdelt_max = os.getenv("GDELT_MAXRECORDS", "25").strip()
    gdelt_maxrecords = int(raw_gdelt_max) if raw_gdelt_max else 25

    gdelt_queries = [q.strip() for q in raw_gdelt.split(",") if q.strip()]
    if not raw_sources and not gdelt_queries:
        log.error("Missing NEWS_SOURCES and GDELT_QUERIES in environment")
        return 1

    groups = []
    if raw_sources:
        sources = [s.strip() for s in raw_sources.split(",") if s.strip()]
        groups.extend(
            fetch_headlines_grouped(
                sources, max_per_source=max_per_source, summary_limit=summary_limit
            )
        )
    if gdelt_queries:
        groups.extend(
            fetch_gdelt_grouped(
                gdelt_queries,
                maxrecords=gdelt_maxrecords,
                timespan=gdelt_timespan,
                sort=gdelt_sort,
            )
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

    access_hash = ""
    if site_password:
        access_hash = hashlib.sha256(site_password.encode("utf-8")).hexdigest()

    payload = {
        "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": groups,
        "iran": iran_items,
        "access_hash": access_hash,
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
