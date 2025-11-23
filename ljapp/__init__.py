import os
import sqlite3
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import click
from sqlalchemy import text

from .utils import (GeoHelper, allowed_file, render_markdown, register_filters,
                    get_days_diff)

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.setdefault("TEMPLATES_AUTO_RELOAD", True)
    app.jinja_env.auto_reload = True

    default_db_uri = "sqlite:///" + os.path.join(app.instance_path, "lovejournal.sqlite")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "your-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", default_db_uri),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        ALLOWED_EXTENSIONS={"png", "jpg", "jpeg", "gif", "webp"},
    )
    app.config.from_pyfile("config.py", silent=True)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = None

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # filters
    register_filters(app)

    @app.context_processor
    def inject_helpers():
        return dict(get_days_diff=get_days_diff, render_markdown=render_markdown)

    # Geo helper
    geo_helper = GeoHelper(os.getenv("AMAP_WEB_KEY", "fd67dbc2f43a792a5a2aa190e3a49d92"))
    geo_helper.start_worker()
    app.extensions["geo_helper"] = geo_helper

    # Blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    register_cli(app)

    return app


def register_cli(app):
    from .models import Entry, Photo, KeyDate

    @app.cli.command("create-user")
    @click.option("--username", prompt=True, help="用户名")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="登录密码")
    def create_user_cmd(username, password):
        """Create or update a login user."""
        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(password)
            user.last_login_at = datetime.now()
            action = "已更新密码"
        else:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            action = "已创建用户"

        db.session.commit()
        click.echo(f"[OK] {action}: {username}")

    @app.cli.command("import-sqlite")
    @click.argument("sqlite_path")
    def import_sqlite(sqlite_path):
        """Import existing SQLite data into the current database."""
        if not os.path.exists(sqlite_path):
            click.echo(f"[ERR] 找不到文件: {sqlite_path}")
            return

        from .models import Entry, Photo, KeyDate

        if Entry.query.first() or Photo.query.first() or KeyDate.query.first():
            click.echo("[ERR] 目标数据库已存在数据，避免重复导入。请先确认。")
            return

        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        def parse_dt(val):
            if not val:
                return None
            for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(val, fmt)
                except Exception:
                    continue
            try:
                return datetime.fromisoformat(val)
            except Exception:
                return datetime.now()

        def fetch_rows(table):
            cur.execute(f"SELECT * FROM {table}")
            return [dict(row) for row in cur.fetchall()]

        try:
            entries = fetch_rows("entry")
            photos = fetch_rows("photo")
            key_dates = fetch_rows("key_date")
        except Exception as exc:
            click.echo(f"[ERR] 读取 SQLite 失败: {exc}")
            conn.close()
            return

        for row in entries:
            db.session.add(
                Entry(
                    id=row.get("id"),
                    created_at=parse_dt(row.get("created_at")) or datetime.now(),
                    content=row.get("content") or "",
                    location=row.get("location"),
                    tags=row.get("tags"),
                )
            )

        for row in photos:
            db.session.add(
                Photo(
                    id=row.get("id"),
                    filename=row.get("filename"),
                    created_at=parse_dt(row.get("created_at")) or datetime.now(),
                    caption=row.get("caption"),
                    location=row.get("location"),
                    tags=row.get("tags"),
                )
            )

        for row in key_dates:
            db.session.add(
                KeyDate(
                    id=row.get("id"),
                    title=row.get("title") or "",
                    date=parse_dt(row.get("date")) or datetime.now(),
                    location=row.get("location"),
                    tags=row.get("tags"),
                )
            )

        db.session.commit()

        if db.engine.dialect.name == "postgresql":
            for table in ("entry", "photo", "key_date", "users"):
                db.session.execute(
                    text(
                        f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1), true)"
                    )
                )
            db.session.commit()

        conn.close()
        click.echo("[OK] 导入完成")
