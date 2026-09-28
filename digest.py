import html
import os
import sys
from datetime import datetime, timezone, timedelta

import feedparser
import requests

SG_FEEDS = [
    "https://www.channelnewsasia.com/rssfeeds/8395986",  # CNA Singapore
    "https://www.straitstimes.com/news/singapore/rss.xml",  # Straits Times Singapore
    "https://www.todayonline.com/singapore/feed",  # TODAY Singapore
]

BUSINESS_FEEDS = [
    "https://www.channelnewsasia.com/rssfeeds/8395938",  # CNA Business
    "https://www.straitstimes.com/news/business/rss.xml",  # Straits Times Business
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",  # CNBC World Business
]

MAX_ITEMS_PER_SECTION = 6
LOOKBACK_HOURS = 30
TELEGRAM_LIMIT = 3500


def fetch_items(feed_urls):
    items = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    seen_titles = set()
    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            source = parsed.feed.get("title", url)
            for entry in parsed.entries:
                title = entry.get("title", "").strip()
                if not title or title.lower() in seen_titles:
                    continue
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue
                seen_titles.add(title.lower())
                items.append({"title": title, "source": source})
        except Exception as e:
            print(f"Failed to fetch {url}: {e}", file=sys.stderr)
    return items[:MAX_ITEMS_PER_SECTION]


def escape(text):
    return html.escape(text, quote=False)


def format_section(heading, items):
    if not items:
        return f"<b>{heading}</b>\nNo fresh updates found.\n"
    lines = [f"<b>{heading}</b>"]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {escape(item['title'])} <i>({escape(item['source'])})</i>")
    return "\n".join(lines) + "\n"


def build_message():
    sgt = timezone(timedelta(hours=8))
    today = datetime.now(sgt).strftime("%d %b %Y")

    sg_items = fetch_items(SG_FEEDS)
    biz_items = fetch_items(BUSINESS_FEEDS)

    parts = [f"<b>\U0001F4F0 Singapore &amp; Business Digest — {today}</b>\n"]
    parts.append(format_section("\U0001F1F8\U0001F1EC Singapore", sg_items))
    parts.append(format_section("\U0001F4BC Business &amp; Markets", biz_items))

    message = "\n".join(parts).strip()
    if len(message) > TELEGRAM_LIMIT:
        message = message[:TELEGRAM_LIMIT].rsplit("\n", 1)[0]
    return message


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
        timeout=30,
    )
    if not resp.ok:
        print(f"Telegram error response: {resp.text}", file=sys.stderr)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    print("Sent digest successfully.")


if __name__ == "__main__":
    msg = build_message()
    print(msg)
    send_telegram(msg)
