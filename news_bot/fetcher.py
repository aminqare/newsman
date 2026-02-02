import feedparser


def _fetch_feed(url, max_per_source):
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
        key = f"{title}|{link}"
        if key in seen:
            continue
        seen.add(key)
        results.append(
            {"title": title, "link": link, "source": feed_title, "source_url": url}
        )

    return feed_title, results


def fetch_headlines(sources, max_per_source=5):
    """Fetch recent headlines from a list of RSS feed URLs.

    Returns a list of dicts: {'title','link','source','source_url'}
    """
    seen = set()
    results = []

    for url in sources:
        _, items = _fetch_feed(url, max_per_source)
        for item in items:
            key = f"{item['title']}|{item['link']}"
            if key in seen:
                continue
            seen.add(key)
            results.append(item)

    return results


def fetch_headlines_grouped(sources, max_per_source=5):
    """Fetch recent headlines grouped by source.

    Returns a list of dicts: {'source','source_url','items'}
    """
    groups = []
    for url in sources:
        feed_title, items = _fetch_feed(url, max_per_source)
        source_name = feed_title or url
        groups.append(
            {"source": source_name, "source_url": url, "items": items}
        )

    return groups
