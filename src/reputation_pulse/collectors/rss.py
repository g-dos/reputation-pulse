from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urljoin
from xml.etree import ElementTree

import httpx

from reputation_pulse.settings import settings


class RssCollector:
    async def collect(self, website_url: str) -> dict[str, Any]:
        normalized_url = website_url.strip()
        if not normalized_url:
            return {"blog_url": "", "feed_url": "", "recent_entries_30d": 0, "last_post_at": None}
        if normalized_url.startswith("www."):
            normalized_url = f"https://{normalized_url}"
        if not normalized_url.startswith(("http://", "https://")):
            normalized_url = f"https://{normalized_url}"

        feed_candidates = [
            normalized_url,
            urljoin(normalized_url, "/feed"),
            urljoin(normalized_url, "/rss"),
            urljoin(normalized_url, "/rss.xml"),
            urljoin(normalized_url, "/atom.xml"),
        ]
        for candidate in feed_candidates:
            parsed = await self._parse_feed(candidate)
            if parsed is not None:
                parsed["blog_url"] = normalized_url
                return parsed

        return {
            "blog_url": normalized_url,
            "feed_url": "",
            "recent_entries_30d": 0,
            "last_post_at": None,
        }

    async def _parse_feed(self, feed_url: str) -> dict[str, Any] | None:
        async with httpx.AsyncClient(
            timeout=settings.default_timeout,
            follow_redirects=True,
        ) as client:
            try:
                response = await client.get(feed_url)
            except httpx.HTTPError:
                return None
        if response.status_code >= 400:
            return None
        try:
            root = ElementTree.fromstring(response.text)
        except ElementTree.ParseError:
            return None

        datetimes = self._extract_entry_datetimes(root)
        recent_threshold = datetime.now(timezone.utc) - timedelta(days=30)
        recent_count = sum(1 for dt in datetimes if dt >= recent_threshold)
        last_post = max(datetimes).isoformat() if datetimes else None
        return {
            "feed_url": feed_url,
            "recent_entries_30d": recent_count,
            "last_post_at": last_post,
        }

    def _extract_entry_datetimes(self, root: ElementTree.Element) -> list[datetime]:
        tags = (
            ".//item/pubDate",
            ".//item/date",
            ".//entry/updated",
            ".//entry/published",
            ".//{http://purl.org/dc/elements/1.1/}date",
        )
        values: list[datetime] = []
        for tag in tags:
            for node in root.findall(tag):
                if not node.text:
                    continue
                parsed = self._parse_datetime(node.text.strip())
                if parsed is not None:
                    values.append(parsed)
        return values

    def _parse_datetime(self, raw: str) -> datetime | None:
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except (TypeError, ValueError):
            pass
        try:
            normalized = raw.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            return None
