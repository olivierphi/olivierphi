# Heavily ~copy-pasted~ inspired by Simon Willison's README repo :-)
# @link https://github.com/simonw/simonw
# The `replace_chunk` function and the `if __name__ == "__main__"` block are pretty much copy-pasted from there,
# the rest is my own quick code.

import http.client
import re
import xml.etree.ElementTree as ET
from datetime import date
from http import HTTPStatus
from typing import NamedTuple

DEVBLOG_RSS_FEED_URL = {"host": "devblog.dunsap.com", "path": "/feed_rss_created.xml"}
DEVBLOG_RSS_FEED_ITEMS_EXCLUDE_LIST = ("Homepage", "Tags")
DEVBLOG_ITEM_URL_PATTERN = re.compile(
    r"^https://[^/]+/(?P<year>\d{4})/(?P<month>\d{2})-(?P<day>\d{2})---(?P<slug>[^/]+)/$"
)
DEVBLOG_RSS_FEED_ITEMS_LIMIT = 10


class DevblogItem(NamedTuple):
    title: str
    url: str
    published_at: date


def parse_devblog_rss_feed(feed_content: bytes) -> list[DevblogItem]:
    # xml_data = ET.parse("./rss_example.xml") # useful for debugging ^_^
    xml_data = ET.fromstring(feed_content.decode())
    items = xml_data.findall(".//item")

    results: list[DevblogItem] = []
    for raw_item in items:
        title = raw_item.find("title").text
        if title in DEVBLOG_RSS_FEED_ITEMS_EXCLUDE_LIST:
            continue
        url = raw_item.find("link").text.strip()
        url_match = DEVBLOG_ITEM_URL_PATTERN.fullmatch(url)
        if not url_match:
            continue
        published_at = date.fromisoformat(f"{url_match['year']}-{url_match['month']}-{url_match['day']}")
        results.append(DevblogItem(title=title, url=url, published_at=published_at))

    return sorted(results, key=lambda item: item.published_at, reverse=True)


def download_devblog_rss_feed() -> bytes:
    # N.B. We could have done that using The Requests package, but plain Python's stdlib will do the job too :-)
    conn = http.client.HTTPSConnection(DEVBLOG_RSS_FEED_URL["host"])
    conn.request("GET", DEVBLOG_RSS_FEED_URL["path"])
    response = conn.getresponse()
    if status := response.status != HTTPStatus.OK:
        raise RuntimeError(f"Got status '{status}' from HTTP response while downloading the RSS feed")
    return response.read()


def replace_chunk(content: str, marker: str, chunk: str) -> str:
    # Copy-pasted (and slightly adapted) from Simon Willison's own `replace_chunk` function
    r = re.compile(
        rf"<!\-\- {marker} starts \-\->.*<!\-\- {marker} ends \-\->",
        re.DOTALL,
    )
    chunk = f"<!-- {marker} starts -->\n{chunk}\n<!-- {marker} ends -->"
    return r.sub(chunk, content)


if __name__ == "__main__":
    from pathlib import Path

    # Pretty much a copy-paste from Simon Willison's own script, once again :-)

    root = Path(__file__).parent.resolve()

    # Manage devblog content:
    rss_feed_content = download_devblog_rss_feed()
    rss_feed_items = parse_devblog_rss_feed(rss_feed_content)
    devblog_markdown = md = "\n".join(
        [
            f"* {item.published_at}: [{item.title}]({item.url})"
            for item in rss_feed_items[:DEVBLOG_RSS_FEED_ITEMS_LIMIT]
        ]
    )

    # Read the current README...
    readme_path = root / "README.md"
    readme_contents = readme_path.open("rt").read()

    # ...Rewrite some of its content...
    rewritten = replace_chunk(readme_contents, "devblog", devblog_markdown)

    # ...And rewrite the file! :-)
    readme_path.open("wt").write(rewritten)
