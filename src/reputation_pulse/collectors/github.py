from __future__ import annotations

from typing import Any

import httpx

from reputation_pulse.cache import CacheStore
from reputation_pulse.errors import CollectorError, UpstreamNotFoundError, UpstreamRateLimitError
from reputation_pulse.settings import settings


class GitHubCollector:
    def __init__(self, cache: CacheStore | None = None) -> None:
        self.cache = cache or CacheStore()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "reputation-pulse/0.1.0"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        return headers

    async def collect(self, handle: str) -> dict[str, Any]:
        cache_key = f"github:{handle}"
        cached = self.cache.get(cache_key, settings.github_cache_ttl_seconds)
        if cached is not None:
            return cached

        headers = self._headers()
        async with httpx.AsyncClient(timeout=settings.default_timeout) as client:
            try:
                user_resp = await client.get(
                    settings.github_user_url.format(handle=handle),
                    headers=headers,
                )
            except httpx.HTTPError as exc:
                raise CollectorError(f"GitHub request failed: {exc}") from exc

        if user_resp.status_code == 404:
            raise UpstreamNotFoundError(f"GitHub user '{handle}' was not found")
        if user_resp.status_code in (403, 429):
            raise UpstreamRateLimitError("GitHub rate limit reached")
        if user_resp.status_code >= 400:
            raise CollectorError(f"GitHub user lookup failed with status {user_resp.status_code}")

        user_data = user_resp.json()
        repo_data = await self._collect_all_repos(handle, headers)
        stars = sum(repo.get("stargazers_count", 0) for repo in repo_data)
        recent_repos = [
            {
                "name": repo.get("name"),
                "pushed_at": repo.get("pushed_at"),
                "stargazers": repo.get("stargazers_count", 0),
            }
            for repo in sorted(
                repo_data,
                key=lambda r: r.get("pushed_at") or "",
                reverse=True,
            )[: settings.max_recent_repos]
        ]

        result = {
            "handle": handle,
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "public_repos": user_data.get("public_repos", 0),
            "created_at": user_data.get("created_at"),
            "updated_at": user_data.get("updated_at"),
            "blog_url": user_data.get("blog") or "",
            "stars": stars,
            "recent_repos": recent_repos,
        }
        self.cache.set(cache_key, result)
        return result

    async def _collect_all_repos(
        self,
        handle: str,
        headers: dict[str, str],
    ) -> list[dict[str, Any]]:
        repos: list[dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=settings.default_timeout) as client:
            for page in range(1, settings.github_max_repo_pages + 1):
                try:
                    repos_resp = await client.get(
                        settings.github_repos_url.format(handle=handle),
                        params={"per_page": settings.github_repos_per_page, "page": page},
                        headers=headers,
                    )
                except httpx.HTTPError as exc:
                    raise CollectorError(f"GitHub repos request failed: {exc}") from exc

                if repos_resp.status_code == 404:
                    raise UpstreamNotFoundError(f"GitHub user '{handle}' was not found")
                if repos_resp.status_code in (403, 429):
                    raise UpstreamRateLimitError("GitHub rate limit reached")
                if repos_resp.status_code >= 400:
                    raise CollectorError(
                        f"GitHub repos lookup failed with status {repos_resp.status_code}"
                    )

                payload = repos_resp.json()
                if not isinstance(payload, list):
                    raise CollectorError("GitHub repos payload is invalid")

                repos.extend(payload)
                if len(payload) < settings.github_repos_per_page:
                    break

        return repos
