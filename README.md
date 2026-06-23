# Airport Hub API

A REST API for an airline ticket booking system. Built on Django + DRF.
Manages countries, airports, airlines, airplanes, flights, tickets, and
orders, with a custom `User` model for booking.

## Features

- Custom `User` model with email login and role (`admin` / `user`)
- Domain models for `Country`, `Airport`, `Airline`, `Airplane`,
  `Flight`, `Ticket`, and `Order`
- Flight status tracking (`scheduled`, `boarding`, `departed`,
  `delayed`, `cancelled`)
- Ticket status tracking (`pending`, `paid`, `cancelled`, `used`)
- Order-based booking: reserve one or more seats on a flight as a single
  order, with a reservation deadline, then pay or cancel
- Unique active seat per flight (`UniqueConstraint` on `flight` +
  `seat_number`, excluding `cancelled` tickets)
- Background expiry of unpaid orders via a scheduled Celery task
- Django admin panel for all models
- OpenAPI schema and Swagger UI via `drf-spectacular`
- Config via `.env` (`os.getenv`), PostgreSQL as the database

## Tech Stack

- Python 3.11+
- Django 6.0
- Django REST Framework 3.17
- drf-spectacular 0.29
- PostgreSQL (psycopg2)
- Celery (with django-celery-beat) and Redis as the broker

## Installation

Common steps for both options below:

```bash
git clone https://github.com/example.git
cd airporthub

cp .env.example .env
# fill in SECRET_KEY and database credentials
```

Then pick **one** of the options.

### Option A — Docker (recommended)

Requires Docker and Docker Compose. Point the service hosts at the compose
network in `.env`:

```env
DB_HOST=db
DB_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

Build and start the full stack — PostgreSQL, Redis, the backend, and the
Celery worker + beat:

```bash
docker compose up --build
```

The `backend` service applies migrations on startup. Create an admin user in
a separate terminal:

```bash
docker compose exec backend python manage.py createsuperuser
```

### Option B — Local (virtualenv)

Requires Python 3.11+ and a running PostgreSQL. Keep `DB_HOST=localhost` in
`.env`.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/api/.

## Project Structure

```
config/         Django project settings (settings, urls, Celery app)
users/          Custom User model and admin
airports/       Geography and flights (Country, Airport, Airline,
                Airplane, Flight)
tickets/        Ticket model and read-only ticket endpoints
orders/         Order booking, payment, and Celery expiry task
```

## Environment Variables

Configured via `.env` (not committed). See `.env.example` for the
template.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key. Generate a new one for production. |
| `DEBUG` | `true` for development, `false` for production. |
| `ALLOWED_HOSTS` | JSON array of allowed hostnames, e.g. `["127.0.0.1","localhost"]`. |
| `DB_NAME` | PostgreSQL database name. |
| `DB_USER` | Database user. |
| `DB_PASSWORD` | Database password. |
| `DB_HOST` | Database host (`localhost` locally, `db` under Docker). |
| `DB_PORT` | Database port (default `5432`). |
| `CELERY_BROKER_URL` | Redis broker URL, e.g. `redis://redis:6379/0`. |
| `CELERY_RESULT_BACKEND` | Redis result backend URL, e.g. `redis://redis:6379/0`. |

## Code Style

The project uses **flake8**, **black**, and **isort**. Configs live in
`.flake8` (flake8) and `pyproject.toml` (black + isort).

Run from the project root:

```bash
# lint
flake8 .

# format
black .

# sort imports
isort .
```
