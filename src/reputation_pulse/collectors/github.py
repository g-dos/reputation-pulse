from __future__ import annotations

from typing import Any

import httpx

from reputation_pulse.settings import settings


class GitHubCollector:
    async def collect(self, handle: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=settings.default_timeout) as client:
            user_resp = await client.get(settings.github_user_url.format(handle=handle))
            user_resp.raise_for_status()
            repos_resp = await client.get(
                settings.github_repos_url.format(handle=handle), params={"per_page": 50}
            )
            repos_resp.raise_for_status()

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
