"""
Task 2 - Crawl news articles about Vietnamese artists related to drug cases.

The preferred crawler is Crawl4AI. This module uses Crawl4AI when it is
installed, and falls back to Python standard-library HTML fetching/parsing so
the assignment can still run in a minimal local environment.
"""

import asyncio
import html
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


ARTICLE_URLS = [
    "https://vietnamnet.vn/ngoai-nguyen-cong-tri-nhung-nghe-si-nao-tung-bi-bat-vi-ma-tuy-2424971.html",
    "https://ngoisao.vnexpress.net/nhung-nghe-si-viet-nga-ngua-vi-ma-tuy-4816068.html",
    "https://ngoisao.vnexpress.net/nam-than-lai-nga-nhikolai-dinh-bi-bat-4762594.html",
    "https://vnexpress.net/dien-vien-hai-bi-tam-giu-vi-lien-quan-ma-tuy-4475240.html",
    "https://amp.vtcnews.vn/ca-si-son-ngoc-minh-vua-bi-bat-vi-lien-quan-ma-tuy-la-ai-ar1019052.html",
]


def setup_directory() -> None:
    """Create data/landing/news/ if it does not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


class ArticleTextExtractor(HTMLParser):
    """Small dependency-free extractor for news pages."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe"}

    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in {"p", "h1", "h2", "h3", "li", "br"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in {"p", "h1", "h2", "h3", "li"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        text = html.unescape(data).strip()
        if not text:
            return
        if self._in_title:
            self.title += f" {text}"
            return
        if self._skip_depth == 0:
            self._parts.append(text)

    def markdown(self) -> str:
        text = " ".join(self._parts)
        text = re.sub(r"\s*\n\s*", "\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        lines = [line.strip() for line in text.splitlines() if len(line.strip()) > 30]
        return "\n\n".join(lines)


def slugify(text: str, fallback: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return (text or fallback)[:90]


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        return raw.decode(charset, errors="replace")


async def crawl_article_with_fallback(url: str) -> dict:
    html_content = await asyncio.to_thread(fetch_html, url)
    extractor = ArticleTextExtractor()
    extractor.feed(html_content)

    title = re.sub(r"\s+", " ", extractor.title).strip() or "Unknown"
    content_markdown = extractor.markdown()
    if not content_markdown:
        raise ValueError(f"Cannot extract content from {url}")

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(timespec="seconds"),
        "content_markdown": content_markdown,
        "crawler": "urllib-htmlparser-fallback",
    }


async def crawl_article(url: str) -> dict:
    """
    Crawl one news article and return metadata plus markdown content.

    Returns:
        {
            "url": str,
            "title": str,
            "date_crawled": str,
            "content_markdown": str,
            "crawler": str
        }
    """
    try:
        from crawl4ai import AsyncWebCrawler

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            title = "Unknown"
            if getattr(result, "metadata", None):
                title = result.metadata.get("title") or title
            return {
                "url": url,
                "title": title,
                "date_crawled": datetime.now().isoformat(timespec="seconds"),
                "content_markdown": getattr(result, "markdown", "") or "",
                "crawler": "crawl4ai",
            }
    except ImportError:
        return await crawl_article_with_fallback(url)
    except Exception as exc:
        print(f"  ! Crawl4AI failed, using fallback: {exc}")
        return await crawl_article_with_fallback(url)


async def crawl_all() -> None:
    """Crawl all configured news articles into JSON files."""
    setup_directory()

    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        article = await crawl_article(url)

        filename = f"article_{i:02d}_{slugify(article['title'], f'article-{i:02d}')}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Saved: {filepath}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
