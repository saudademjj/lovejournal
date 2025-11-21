from flask import (
    Flask, render_template, request, redirect,
    url_for, send_from_directory, abort
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.utils import secure_filename
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # 生产环境建议改成你自己随机生成的秘:
    # python -c "import secrets; print(secrets.token_hex(32))"
    app.config.from_mapping(
        SECRET_KEY="change-this-to-a-random-secret",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "lovejournal.sqlite"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        MAX_CONTENT_LENGTH=4 * 1024 * 1024,  # 4 MB 小照片
        ALLOWED_EXTENSIONS={"png", "jpg", "jpeg", "gif", "webp"},
    )

    # 确保 instance / uploads 目录存在
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # ---- 数据模型 ----
    class Entry(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        content = db.Column(db.Text, nullable=False)

    class KeyDate(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        date = db.Column(db.Date, nullable=False)

    class Photo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        caption = db.Column(db.String(255))

    with app.app_context():
        db.create_all()

    # ---- 小工具 ----
    def allowed_file(filename: str) -> bool:
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
        )

    @app.context_processor
    def inject_helpers():
        def days_diff(d: date) -> int:
            """正数: 还有多少天；负数: 已经过了多少天"""
            today = date.today()
            return (d - today).days

        return dict(days_diff=days_diff)

    # ---- 路由 ----

    @app.route("/", methods=["GET"])
    def index():
        today = date.today()

        timeline = []

        for entry in Entry.query.all():
            timeline.append({
                "type": "entry",
                "timestamp": entry.created_at,
                "item": entry,
            })

        for kd in KeyDate.query.all():
            timeline.append({
                "type": "keydate",
                "timestamp": datetime.combine(kd.date, datetime.min.time()),
                "item": kd,
            })

        for photo in Photo.query.all():
            timeline.append({
                "type": "photo",
                "timestamp": photo.uploaded_at,
                "item": photo,
            })

        timeline.sort(key=lambda node: node["timestamp"], reverse=True)

        return render_template(
            "index.html",
            timeline=timeline,
            today=today,
        )

    @app.post("/entries")
    def add_entry():
        content = (request.form.get("content") or "").strip()
        if not content:
            return ("", 204)

        entry = Entry(content=content)
        db.session.add(entry)
        db.session.commit()

        # HTMX 请求：只返回单条 HTML 片段
        if request.headers.get("HX-Request") == "true":
            return render_template("_entry_item.html", entry=entry)

        return redirect(url_for("index"))

    @app.post("/keydates")
    def add_keydate():
        title = (request.form.get("title") or "").strip()
        date_str = (request.form.get("date") or "").strip()

        if not title or not date_str:
            return ("", 204)

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return ("Invalid date", 400)

        kd = KeyDate(title=title, date=d)
        db.session.add(kd)
        db.session.commit()

        if request.headers.get("HX-Request") == "true":
            return render_template("_date_item.html", d=kd, today=date.today())

        return redirect(url_for("index"))

    @app.post("/photos")
    def upload_photo():
        file = request.files.get("photo")
        caption = (request.form.get("caption") or "").strip()

        if not file or file.filename == "":
            return ("", 204)

        if not allowed_file(file.filename):
            return ("File type not allowed", 400)

        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        upload_folder = app.config["UPLOAD_FOLDER"]

        # 避免重名覆盖
        i = 1
        save_name = filename
        while os.path.exists(os.path.join(upload_folder, save_name)):
            save_name = f"{base}_{i}{ext}"
            i += 1

        file.save(os.path.join(upload_folder, save_name))

        photo = Photo(filename=save_name, caption=caption or None)
        db.session.add(photo)
        db.session.commit()

        if request.headers.get("HX-Request") == "true":
            return render_template("_photo_item.html", photo=photo)

        return redirect(url_for("index"))

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        # 简单保护
        if ".." in filename or filename.startswith("/"):
            abort(404)
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app


app = create_app()
