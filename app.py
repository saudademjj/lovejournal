#
from flask import (
    Flask, render_template, request, redirect,
    url_for, send_from_directory
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True

    app.config.from_mapping(
        SECRET_KEY="your-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "lovejournal.sqlite"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        ALLOWED_EXTENSIONS={"png", "jpg", "jpeg", "gif", "webp"},
    )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # ---- Models ----
    class Entry(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
        content = db.Column(db.Text, nullable=False)

    class KeyDate(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        # [Fix]: 改为 DateTime 以记录具体时间 (HH:MM)
        date = db.Column(db.DateTime, nullable=False)

    class Photo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
        caption = db.Column(db.String(255))

    with app.app_context():
        db.create_all()

    # ---- Helpers ----
    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    @app.context_processor
    def inject_helpers():
        def get_days_diff(d):
            today = datetime.now()  # 使用 datetime 比较更精确，或者保留 date()
            target = d
            if isinstance(d, datetime):
                # 如果只需要计算天数差，忽略时分秒影响天数判断，可转为 date
                # 但为了保留"今天"的精确感，这里保留 datetime 逻辑
                pass

                # 简单的天数计算逻辑
            diff = (target.date() - today.date()).days
            if diff < 0: return (abs(diff), 'past')
            if diff > 0: return (diff, 'future')
            return (0, 'today')

        return dict(get_days_diff=get_days_diff)

    # ---- Routes ----

    @app.route("/")
    def index():
        timeline = []

        for e in Entry.query.all():
            timeline.append({"type": "entry", "timestamp": e.created_at, "item": e})
        for k in KeyDate.query.all():
            # KeyDate 现在已经是 DateTime 对象，不需要 combine
            timeline.append({"type": "keydate", "timestamp": k.date, "item": k})
        for p in Photo.query.all():
            timeline.append({"type": "photo", "timestamp": p.created_at, "item": p})

        # 排序：最新的在前面
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        years = sorted(list(set([t["timestamp"].year for t in timeline])), reverse=True)

        return render_template("index.html", timeline=timeline, years=years)

    @app.route("/anniversaries")
    def anniversaries():
        dates = KeyDate.query.order_by(KeyDate.date).all()
        return render_template("anniversaries.html", dates=dates)

    # ---- Create Actions ----

    def parse_datetime(date_str):
        """解析前端传入的 datetime-local 字符串，如果空则返回现在"""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return datetime.now()

    @app.post("/add/entry")
    def add_entry():
        content = request.form.get("content", "").strip()
        custom_date = request.form.get("custom_date")
        if content:
            dt = parse_datetime(custom_date)
            db.session.add(Entry(content=content, created_at=dt))
            db.session.commit()
        return redirect(url_for("index"))

    @app.post("/add/keydate")
    def add_keydate():
        title = request.form.get("title", "").strip()
        # [Fix]: 获取完整的时间字符串 (YYYY-MM-DDTHH:MM)
        date_str = request.form.get("date", "").strip()

        if title:
            # [Fix]: 使用统一的 parse_datetime，保留具体时间
            dt = parse_datetime(date_str)
            db.session.add(KeyDate(title=title, date=dt))
            db.session.commit()

        if "anniversaries" in request.referrer:
            return redirect(url_for("anniversaries"))
        return redirect(url_for("index"))

    @app.post("/add/photo")
    def add_photo():
        file = request.files.get("photo")
        caption = request.form.get("caption", "").strip()
        custom_date = request.form.get("custom_date")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            count = 1
            save_name = filename
            while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], save_name)):
                save_name = f"{base}_{count}{ext}"
                count += 1

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], save_name))

            dt = parse_datetime(custom_date)
            db.session.add(Photo(filename=save_name, caption=caption, created_at=dt))
            db.session.commit()
        return redirect(url_for("index"))

    @app.post("/delete/<type>/<int:id>")
    def delete_item(type, id):
        model = {"entry": Entry, "keydate": KeyDate, "photo": Photo}.get(type)
        if model:
            item = db.get_or_404(model, id)
            db.session.delete(item)
            db.session.commit()
        return redirect(request.referrer or url_for("index"))

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")