<div align="center">
  English | <a href="./README.md">简体中文</a>
</div>

# LoveJournal v1 (Classic Flask Life Record System)

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 is the initial technical iteration of this life recording system. Built with the classic **Flask** framework and a Server-Side Rendering (SSR) approach, it provides a stable and warm platform for individual or couple memories. As the architectural origin for the subsequent high-performance async version (Lovejournal-New), this project preserves early engineering practices in data persistence, media asset management, and responsive design.

## ✨ Core Feature Highlights

- **Multi-dimensional Memories**: Supports Markdown-based diaries with rich text, lossless photo uploads in a gallery view, and precise anniversary tracking.
- **Unified Timeline Vision**: Aggregates all types of data streams (diaries, photos, anniversaries) chronologically, featuring built-in pagination and full-text search.
- **Geographic Footprints**: Integrates with AMAP (Gaode Map) geocoding to intuitively display the spatial coordinates of each memory record.
- **Security & Privacy**: Employs `Flask-Login` for robust session management, ensuring your private moments remain safe from unauthorized access.

## 🏛️ Core Design & Functional Practices

### 1. Sequential Timeline Modeling
Utilizes **Flask-SQLAlchemy** for the efficient orchestration of record entries.
- **Layered Logic**: Employs a strict Model-View separation pattern to maintain clear and maintainable business logic.
- **Chronological Retrieval**: Backend query optimizations enable deep sorting by timestamp, providing an intuitive historical memory retrieval path.

### 2. Traditional SSR & Responsive Views
- **Jinja2 Template Engineering**: Leverages template inheritance and modular components to reduce HTML redundancy and ensure high view-layer reusability.
- **Bootstrap 5 Grid System**: Strictly follows Mobile-First principles, guaranteeing consistent visual appeal across mobile devices and desktop browsers.

### 3. Media Asset Governance
- **Upload Pipeline**: Implements a secure file upload pipeline that includes safe filename sanitization, MIME-type validation, and automated renaming.
- **Physical Storage**: Features tiered local filesystem storage, providing a clean logical interface for potential future migrations to object storage (e.g., S3).

## 🚀 Quick Start Deployment

### 1. Clone & Environment Setup
```bash
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt  # Or manually install Flask, SQLAlchemy, etc.
```

### 2. Database & Application Initialization
```bash
flask --app app.py db upgrade
flask --app app.py create-user  # Follow the prompts to create your admin account
```

### 3. Run Locally
```bash
flask --app app.py run
```
The application will default to running at `http://127.0.0.1:5000`. You can log in using the admin account you just created.

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

## ⚠️ Successor Recommendation
This project is currently in maintenance mode as the **v1 Initial Version**, primarily serving as a technical archive. For a modern interactive experience and peak performance (e.g., React 19, FastAPI, asynchronous design), please see the next-generation evolution of this project:
👉 **[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)**

## 📄 License
This project is open-sourced under the MIT License.