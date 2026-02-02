import feedparser


def fetch_headlines(sources, max_per_source=5):
    """Fetch recent headlines from a list of RSS feed URLs.

    Returns a list of dicts: {'title','link','source'}
    """
    seen = set()
    results = []

    for url in sources:
        try:
            parsed = feedparser.parse(url)
        except Exception:
            continue

        feed_title = parsed.feed.get("title", "") if hasattr(parsed, "feed") else ""
        entries = getattr(parsed, "entries", []) or []

        for entry in entries[:max_per_source]:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title:
                continue
            key = f"{title}|{link}"
            if key in seen:
                continue
            seen.add(key)
            results.append({"title": title, "link": link, "source": feed_title})

    return results
