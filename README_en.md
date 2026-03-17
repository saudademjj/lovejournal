<div align="center">
  English | <a href="./README.md">简体中文</a>
</div>

# LoveJournal v1 (Classic Flask Life Record System)

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 is the initial technical iteration of this life recording system. Built with the classic **Flask** framework and a Server-Side Rendering (SSR) approach, it provides a stable and warm platform for individual or couple memories. As the architectural origin for the subsequent high-performance async version (Lovejournal-New), this project preserves early engineering practices in data persistence, media asset management, and responsive design.

## 🏛️ Core Design & Functional Practices

### 1. Sequential Timeline Modeling
Utilizes **Flask-SQLAlchemy** for efficient orchestration of record entries.
- **Layered Logic**: Employs a Model-View separation pattern to ensure clear business logic.
- **Chronological Retrieval**: Backend query optimizations enable deep sorting by timestamp, providing users with an intuitive path for historical memory retrieval.

### 2. Traditional SSR & Responsive Views
- **Jinja2 Template Engineering**: Leverages template inheritance and modular components to reduce HTML redundancy and ensure high view-layer reusability.
- **Bootstrap 5 Grid System**: Strictly follows Mobile-First principles, ensuring consistent visual appeal across various mobile devices and desktop browsers.

### 3. Basic Media Asset Governance
- **Upload Pipeline**: Implements a file upload pipeline including safe filename sanitization, type validation, and automated renaming.
- **Physical Storage**: Tiered storage based on the local filesystem, providing a logical interface for future migrations to object storage (e.g., S3).

## 📂 Project Structure

```text
lovejournal/
├── ljapp/              # Core application logic
│   ├── models.py       # DB entity definitions (SQLAlchemy)
│   └── views.py        # Route handlers and business controllers
├── static/             # Static assets: Global CSS, Vanilla JS, and UI images
├── templates/          # Jinja2 HTML component pool
├── migrations/         # Structured DB migration history
├── instance/           # Local SQLite data files for testing
├── app.py              # Application bootstrap, plugin init, and entry point
└── README.md           # Technical specs and development standards
```

## Successor Recommendation
This project is currently in maintenance mode as the **v1 Initial Version**. For a modern interactive experience and peak performance, please see the successor:
👉 **[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)** (FastAPI + React 19 + AMap)

## License
MIT License
