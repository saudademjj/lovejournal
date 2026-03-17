English | [简体中文](README.md)

# LoveJournal


`LoveJournal` is a Flask-based web app for preserving relationship memories through journal entries, photos, anniversaries, map views, and a combined timeline. Compared with `LoveJournal New`, this repository keeps the more traditional all-in-one web architecture.

## Core Features

- Journal management with Markdown content and tag extraction
- Photo upload, editing, deletion, and gallery display
- Anniversary tracking with countdown and elapsed-day views
- Aggregated timeline across multiple content types
- Map view based on place names or coordinates
- Authentication powered by `Flask-Login`

## Tech Stack

- Backend: `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-Login`
- Database: `SQLite` by default, switchable to `PostgreSQL`
- Frontend: `Jinja2` templates plus plain HTML, CSS, and JavaScript
- Maps: AMap geocoding APIs

## Quick Start

```bash
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal
python -m venv .venv
source .venv/bin/activate
pip install flask flask-sqlalchemy flask-migrate flask-login bleach markdown requests
flask --app app.py db upgrade
flask --app app.py create-user
flask --app app.py run
```

Default URL: `http://127.0.0.1:5000`

## Useful CLI Commands

```bash
flask --app app.py create-user
flask --app app.py import-sqlite /path/to/old.sqlite
```

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
