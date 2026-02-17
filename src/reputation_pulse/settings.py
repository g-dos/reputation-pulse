from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    github_user_url: str = "https://api.github.com/users/{handle}"
    github_repos_url: str = "https://api.github.com/users/{handle}/repos"
    max_recent_repos: int = 3
    default_timeout: float = 15.0
    db_path: str = "reputation_pulse.db"
    github_token: str = os.getenv("GITHUB_TOKEN", "")

settings = Settings()
