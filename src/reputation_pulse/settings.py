import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    github_user_url: str = "https://api.github.com/users/{handle}"
    github_repos_url: str = "https://api.github.com/users/{handle}/repos"
    github_repos_per_page: int = 100
    github_max_repo_pages: int = 10
    max_recent_repos: int = 3
    default_timeout: float = 15.0
    db_path: str = "reputation_pulse.db"
    cache_dir: str = ".cache/reputation-pulse"
    github_cache_ttl_seconds: int = 900
    github_token: str = os.getenv("GITHUB_TOKEN", "")

settings = Settings()
