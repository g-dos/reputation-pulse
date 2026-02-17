from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_user_url: str = "https://api.github.com/users/{handle}"
    github_repos_url: str = "https://api.github.com/users/{handle}/repos"
    max_recent_repos: int = 3
    default_timeout: float = 15.0

settings = Settings()
