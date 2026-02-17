from __future__ import annotations

from typing import Any

import httpx

from reputation_pulse.errors import CollectorError, UpstreamNotFoundError, UpstreamRateLimitError
from reputation_pulse.settings import settings


class GitHubCollector:
    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "reputation-pulse/0.1.0"}
        if settings.github_token:
            headers["Authorization"] = f"Bearer {settings.github_token}"
        return headers

    async def collect(self, handle: str) -> dict[str, Any]:
        headers = self._headers()
        async with httpx.AsyncClient(timeout=settings.default_timeout) as client:
            try:
                user_resp = await client.get(
                    settings.github_user_url.format(handle=handle),
                    headers=headers,
                )
                repos_resp = await client.get(
                    settings.github_repos_url.format(handle=handle),
                    params={"per_page": 50},
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

        if repos_resp.status_code in (403, 429):
            raise UpstreamRateLimitError("GitHub rate limit reached")
        if repos_resp.status_code >= 400:
            raise CollectorError(f"GitHub repos lookup failed with status {repos_resp.status_code}")

        user_data = user_resp.json()
        repo_data = repos_resp.json()
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

        return {
            "handle": handle,
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "public_repos": user_data.get("public_repos", 0),
            "created_at": user_data.get("created_at"),
            "updated_at": user_data.get("updated_at"),
            "stars": stars,
            "recent_repos": recent_repos,
        }
