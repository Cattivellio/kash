# Kash

Personal finance tracker — simple, fast, mobile-first.

## Stack

- **FastAPI** + Jinja2 SSR + Pydantic
- **PostgreSQL** via psycopg2 (connection pool)
- **Vanilla JS** + CSS liquid glass (no framework)
- **Docker** + docker-compose

## Quick Start

```bash
# 1. Create database
psql -U admin_root -c "CREATE DATABASE kash;"

# 2. Copy and edit env
cp .env.example .env

# 3. Install deps
pip install -r requirements.txt

# 4. Run
uvicorn app.main:app --host 0.0.0.0 --port 8200 --reload
```

## Docker

```bash
docker compose up -d
```

Joins the `postgree_red_central_db` network. Port `8200`.

## Features

- **Multi-user**: name-based sign-in (no password), cookie session
- **Income / Expenses**: CRUD with name, datetime, amount, payment method
- **Dashboard**: monthly totals (income, expense, balance)
- **History**: filter by date range, type, payment method
- **Bilingual**: ES/EN toggle, persisted per user
- **Theme**: light/dark, follows OS preference
- **Mobile-first**: iOS liquid glass UI, bottom tab bar, sheet modals

## Payment Methods

- Cash
- Card
- Zelle

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `kash` | Database name |
| `DB_USER` | `admin_root` | Database user |
| `DB_PASSWORD` | | Database password |
| `SESSION_SECRET` | `dev-secret-change-me` | Cookie signing secret |
| `SESSION_MAX_AGE` | `31536000` (1 year) | Session cookie lifetime |
| `KASH_HOST` | `0.0.0.0` | Bind host |
| `KASH_PORT` | `8200` | Bind port |
| `TZ` | `America/Caracas` | Timezone |
