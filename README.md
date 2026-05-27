# Airport Hub API

A REST API for an airline ticket booking system. Built on Django + DRF.
Manages countries, airports, airlines, airplanes, flights, and tickets,
with a custom `User` model for booking.

## Features

- Custom `User` model with email login and role (`admin` / `user`)
- Domain models for `Country`, `Airport`, `Airline`, `Airplane`,
  `Flight`, and `Ticket`
- Flight status tracking (`scheduled`, `boarding`, `departed`,
  `delayed`, `cancelled`)
- Ticket status tracking (`booked`, `paid`, `cancelled`, `used`)
- Unique seat per flight (`unique_together` on `flight` + `seat_number`)
- Django admin panel for all models
- OpenAPI schema and Swagger UI via `drf-spectacular`
- Config via `.env` (`os.getenv`), PostgreSQL as the database

## Tech Stack

- Python 3.11+
- Django 6.0
- Django REST Framework 3.17
- drf-spectacular 0.29
- PostgreSQL (psycopg2)

## Installation

```bash
git clone https://github.com/example.git
cd airporthub

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

cp .env.example .env
# fill in SECRET_KEY and database credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API will be available at http://127.0.0.1:8000/api/.

## Project Structure

```
config/         Django project settings (settings, urls)
users/          Custom User model and admin
airports/       Domain app (Country, Airport, Airline, Airplane,
                Flight, Ticket)
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
| `DB_HOST` | Database host (usually `localhost`). |
| `DB_PORT` | Database port (default `5432`). |

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
