<div align="center">
  English | <a href="./README.md">简体中文</a>
</div>

# LoveJournal v1 -- Classic Flask Life Recording System

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 is the initial technical iteration of this life recording system. Built on the classic Flask framework with server-side rendering (SSR), it provides a robust and intimate private memory archiving platform. As the architectural origin of the subsequent high-performance async version [Lovejournal-New](https://github.com/saudademjj/Lovejournal-New), this project fully preserves the early engineering practices in data persistence, media asset management, and responsive layout.

## Core Features

### Multi-dimensional Memory Management
- Rich Markdown journals with text and images
- Lossless image gallery upload and browsing
- Day-precise anniversary tracking and countdown reminders
- Unified management interface for multiple data types

### Global Timeline View
- Aggregates all data streams (journals, photos, anniversaries) into a unified chronological timeline
- Supports paginated browsing and full-text search
- Deep timestamp-based sorting providing intuitive historical retrospection paths

### Geographic Footprint
- Integrated AMap (Gaode Maps) geocoding service
- Visual display of spatial coordinates for each record
- Linked browsing between map markers and memory entries

### Security & Privacy
- Flask-Login based session management
- User authentication and access control
- Ensures private memories are not accessed without authorization

## Technical Architecture

### Backend

- Flask 3.0: Classic Python web micro-framework
- Flask-SQLAlchemy: ORM data models and query building
- Flask-Login: User session management and authentication
- Flask-Migrate / Alembic: Database migration version control

### Frontend (SSR)

- Jinja2 Template Engine: Template inheritance and component-based design, reducing HTML redundancy and improving view layer reusability
- Bootstrap 5.3: Mobile-first responsive grid system ensuring consistent visual experience across all devices
- Vanilla JavaScript: DOM interactions and dynamic effects

### Data & Storage

- SQLAlchemy ORM: Model-View separation design pattern with clear business logic
- File Upload Pipeline: Includes filename sanitization, type validation, and automatic renaming
- Local Filesystem Hierarchical Storage: Logical interfaces reserved for future object storage migration

### Geographic Services

- AMap Geocoding API: Address text to coordinate conversion
- Map Marker Rendering: Visualization based on coordinate data

## Directory Structure

```text
lovejournal/
├── app.py                  # Flask application entry point
├── ljapp/                  # Main application package
│   ├── __init__.py         # Application factory and extension initialization
│   ├── models/             # SQLAlchemy model definitions
│   │   └── ...             # Journal, photo, anniversary data models
│   ├── views/              # Route handlers / blueprints
│   │   └── ...             # Auth, journal, gallery, timeline views
│   ├── templates/          # Jinja2 templates (with inheritance)
│   │   ├── base.html       # Base layout template
│   │   └── ...             # Feature page templates
│   └── static/             # CSS, JS, uploaded media files
├── migrations/             # Alembic / Flask-Migrate database migrations
├── instance/               # Instance-level config (not version controlled)
└── README.md
```

## Quick Start

### Prerequisites

- Python >= 3.10
- SQLite (default) or PostgreSQL

### 1. Clone and Setup Environment

```bash
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file or configure in the `instance/` directory:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/app.db  # Or PostgreSQL connection string
AMAP_API_KEY=your-amap-key              # AMap API key
```

### 3. Database Initialization

```bash
flask db upgrade
```

### 4. Launch Application

```bash
flask run
```

Visit `http://localhost:5000` to use the application.

## Relationship to LoveJournal-New

This project is the v1 version of the life recording system, which has since evolved into a high-performance async architecture based on FastAPI + React:

| Dimension | v1 (This Project) | v2 (Lovejournal-New) |
|-----------|-------------------|----------------------|
| Backend | Flask (synchronous) | FastAPI (asynchronous) |
| Frontend | Jinja2 SSR + Bootstrap | React SPA + Tailwind CSS |
| Database | Flask-SQLAlchemy | SQLAlchemy 2.0 Async + asyncpg |
| Maps | Basic geocoding | Deep interaction + clustering + GIST indexing |
| Rendering | Server-side rendering | Client-side rendering + API separation |

The v1 version is fully preserved as the architectural origin, suitable for learning Flask full-stack development patterns and SSR engineering practices.

## License

MIT License
