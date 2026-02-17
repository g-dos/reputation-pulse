# reputation-pulse

Reputation Pulse is a Python toolkit that scans a public handle (GitHub, LinkedIn, etc.) and gathers quantitative signals to score reputational activity for decision-makers. It includes a FastAPI endpoint for automation pipelines and a Typer-powered CLI for interactive scans.

## Getting started

- Install via `python3 -m pip install --user poetry` and then `poetry install`.
- Start the API with `poetry run reputation-pulse api`.
- Collect one-shot insights with `poetry run reputation-pulse scan <github-handle>`.
- Review local history with `poetry run reputation-pulse history --limit 20`.
- Generate an HTML report from local history with `poetry run reputation-pulse report <github-handle>`.
  Default output is timestamped per handle in `reports/`.
- Inspect aggregated local stats with `poetry run reputation-pulse insights <github-handle>`.
- Export insights with `poetry run reputation-pulse insights-export <github-handle> --format json`.

## API

- `GET /health`: healthcheck endpoint.
- `POST /scan`: body `{"handle":"g-dos"}` and returns normalized score + recommendations.
- `GET /history?limit=20`: returns recent local scans persisted in SQLite.
- `GET /report/{handle}`: returns HTML for the latest stored scan of that handle.
- `GET /insights/{handle}`: returns aggregated stats (avg/min/max/latest) for a handle.
- `GET /insights/{handle}/export?format=json|csv`: exports insight payload as serialized content.

## Environment

- `GITHUB_TOKEN` (optional): increases GitHub API quota.
- Database path defaults to `reputation_pulse.db` in project root.
- GitHub scans are cached locally for 15 minutes in `.cache/reputation-pulse`.

## Developer workflow

- `make install`
- `make lint`
- `make test`
- `make run-api`

## Design

- `collectors/` stage collects data from GitHub and other sources.
- RSS/blog activity is auto-detected from GitHub `blog_url` when available.
- `scoring/` normalizes signals into actionable scores.
- `reports/` transforms scores into summaries and recommendations for operators.
- `storage.py` persists each scan in local SQLite for trend inspection.

## Next steps

- Add connectors for LinkedIn or RSS feeds (watch for rate limits and scraping rules).
- Introduce caching so repeated scans reuse recent data and avoid hitting public APIs.
- Add webhook/Slack notifications when the weekly score changes by more than 10%.
