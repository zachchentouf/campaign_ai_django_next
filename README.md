> **AI Generated** — This README was written by Claude based on reading the actual source code.

# Campaign AI — Django + Next.js Monorepo

A full-stack political intelligence tool that scrapes social media and news sources, runs weekly AI analysis on undecided voter sentiment, and surfaces results through a Next.js dashboard.

## What it does

The backend collects posts from Twitter and News API, runs them through OpenAI to produce weekly breakdowns of why voters are undecided (e.g. `{"economy": 45, "healthcare": 30}`), and stores scraped posts, analysis results, and supporting evidence in Postgres. The frontend displays this data and is protected by JWT-based authentication.

## Architecture

```
campaign_ai_django_next/
├── backend/                  # Django REST API + Celery workers
│   └── src/
│       ├── backend/          # Core app: custom User model, auth, settings
│       ├── undecided_voters/ # Scraping, analysis tasks, data models
│       └── analysis/         # Analysis views
└── frontend/                 # Next.js monorepo (pnpm workspaces)
    ├── apps/web/             # Main Next.js app
    └── packages/
        ├── types/            # OpenAPI-generated types shared from backend
        └── ui/               # Shared UI components
```

## Services (Docker Compose)

| Service | Port | Description |
|---|---|---|
| `web` | 3001 | Next.js frontend |
| `api` | 8000 | Django REST API + Swagger at `/api/schema/swagger-ui/` |
| `db` | internal | Postgres |
| `redis` | 6379 | Celery broker |
| `celery_worker` | — | Runs scraping/analysis tasks |
| `celery_beat` | — | Schedules recurring tasks |

## Running locally

**Prerequisites:** Docker Desktop

```bash
git clone <this-repo>
cd campaign_ai_django_next

# Create env files
cp .env.backend.template .env.backend   # set SECRET_KEY and DEBUG=1
cp .env.frontend.template .env.frontend  # set NEXTAUTH_SECRET (openssl rand -base64 32)

docker compose up
```

Frontend: http://localhost:3001
Django admin: http://localhost:8000/admin
Swagger: http://localhost:8000/api/schema/swagger-ui/

**Create a superuser:**
```bash
docker compose exec api poetry run python src/manage.py createsuperuser
```

**Trigger scraping manually:**
```bash
./trigger_scraping.sh
./trigger_analysis.sh
```

## Data models

- **`ScrapingRun`** — tracks each scraping session (source, status, date range, post count)
- **`RawPost`** — individual scraped posts with content, author, metadata (likes/retweets), publisher
- **`WeeklyAnalysis`** — AI-generated weekly summaries: reasons JSON with percentages, detailed analysis, supporting evidence quotes
- **`User`** — extended Django user with `created_at` / `modified_at`

## Auth

JWT tokens issued by Django (`djangorestframework-simplejwt`) and consumed by `next-auth` on the frontend. Set `NEXTAUTH_SECRET` in `.env.frontend` before starting.

## Updating the OpenAPI schema

After changing Django serializers, regenerate TypeScript types:
```bash
docker compose exec web pnpm openapi:generate
```

## Tech stack

**Backend:** Python 3.13, Django, Django REST Framework, Celery, Redis, Postgres, Poetry
**Frontend:** Next.js 15, TypeScript, Tailwind CSS, next-auth, react-hook-form, zod, react-usa-map
**Infra:** Docker Compose
