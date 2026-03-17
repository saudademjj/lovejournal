<div align="center">
  English | <a href="./README.md">简体中文</a>
</div>

# LoveJournal v1 (Classic Flask Life Record System)

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 is the initial technical iteration of this record system. Built with the classic **Flask** framework and Server-Side Rendering (SSR) approach, it provides a robust and warm archiving platform for individual or couple memories. As the architectural origin for the subsequent high-performance async version (Lovejournal-New), this project preserves the design thinking and engineering practices of the early development stages.

## Core Design & Functional Practices

### 1. Linear Timeline Modeling
Utilizes **Flask-SQLAlchemy** to orchestrate record entries. The system performs deep sorting of timestamps on the backend, providing users with an intuitive path for historical memory retrieval.

### 2. Responsive View Rendering
- **Jinja2 Templates**: Employs a decoupled template inheritance mechanism to ensure high reusability of the view layer.
- **Bootstrap 5 Styling**: Combined with a grid system to achieve seamless adaptation across mobile and desktop devices, delivering a consistent sensory experience.

### 3. Basic Media Asset Governance
Implements structured local file upload validation, renaming, and persistence mechanisms, ensuring the security and uniqueness of static resources at the physical storage level.

## Technical Stack Overview

- **Backend Core**: Flask (Python 3.x).
- **Persistence Layer**: Flask-SQLAlchemy (Supporting SQLite/PostgreSQL).
- **Styling Framework**: Bootstrap 5.
- **File Security**: Werkzeug (For secure filename parsing and upload handling).

## Project Structure

```text
lovejournal/
├── ljapp/              # Core application logic (Views and Blueprints)
├── static/             # Static assets (CSS, JavaScript, Images)
├── templates/          # HTML view components based on Jinja2
├── migrations/         # Database migration history
├── instance/           # Instance directory containing SQLite DB files
├── app.py              # Application entry and environment initialization
└── README.md           # Technical documentation
```

## Successor Recommendation
This project is now in the maintenance phase as **v1 Initial Edition**. For interactive animations based on React 19, async performance via FastAPI, and deep AMap spatial integration, please see: **[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)**.

## License
This project follows the MIT License protocol.
