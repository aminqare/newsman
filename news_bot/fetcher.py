import html
import re

import feedparser


def _clean_text(value):
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _brief(text, limit=220):
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _extract_summary(entry, limit=220):
    raw = entry.get("summary") or entry.get("description") or entry.get("subtitle") or ""
    cleaned = _clean_text(raw)
    return _brief(cleaned, limit=limit) if cleaned else ""


def _fetch_feed(url, max_per_source, summary_limit):
    try:
        parsed = feedparser.parse(url)
    except Exception:
        return "", []

    feed_title = parsed.feed.get("title", "") if hasattr(parsed, "feed") else ""
    entries = getattr(parsed, "entries", []) or []
    results = []
    seen = set()

    for entry in entries[:max_per_source]:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not title:
            continue
        summary = _extract_summary(entry, limit=summary_limit)
        key = f"{title}|{link}"
        if key in seen:
            continue
        seen.add(key)
        results.append(
            {
                "title": title,
                "link": link,
                "summary": summary,
                "source": feed_title,
                "source_url": url,
            }
        )

    return feed_title, results


def fetch_headlines(sources, max_per_source=5, summary_limit=220):
    """Fetch recent headlines from a list of RSS feed URLs.

    Returns a list of dicts: {'title','link','summary','source','source_url'}
    """
    seen = set()
    results = []

    for url in sources:
        _, items = _fetch_feed(url, max_per_source, summary_limit)
        for item in items:
            key = f"{item['title']}|{item['link']}"
            if key in seen:
                continue
            seen.add(key)
            results.append(item)

    return results


def fetch_headlines_grouped(sources, max_per_source=5, summary_limit=220):
    """Fetch recent headlines grouped by source.

    Returns a list of dicts: {'source','source_url','items'}
    """
    groups = []
    for url in sources:
        feed_title, items = _fetch_feed(url, max_per_source, summary_limit)
        source_name = feed_title or url
        groups.append(
            {"source": source_name, "source_url": url, "items": items}
        )

    return groups
