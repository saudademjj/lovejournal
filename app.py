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
        # 允许用户自定义时间
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
        content = db.Column(db.Text, nullable=False)

    class KeyDate(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        date = db.Column(db.Date, nullable=False)

    class Photo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        # 允许用户自定义时间
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
            """计算天数差，返回 (数值, 'past'|'future'|'today')"""
            today = date.today()
            if isinstance(d, datetime):
                d = d.date()
            diff = (d - today).days
            if diff < 0: return (abs(diff), 'past')
            if diff > 0: return (diff, 'future')
            return (0, 'today')

        return dict(get_days_diff=get_days_diff)

    # ---- Routes ----

    @app.route("/")
    def index():
        timeline = []

        # 聚合数据
        for e in Entry.query.all():
            timeline.append({"type": "entry", "timestamp": e.created_at, "item": e})
        for k in KeyDate.query.all():
            ts = datetime.combine(k.date, datetime.min.time())
            timeline.append({"type": "keydate", "timestamp": ts, "item": k})
        for p in Photo.query.all():
            timeline.append({"type": "photo", "timestamp": p.created_at, "item": p})

        # 排序
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)

        # 提取年份列表供侧边栏导航使用
        # 格式: { 2025: [12, 11, ...], 2024: [...] } 简化版只取年份
        years = sorted(list(set([t["timestamp"].year for t in timeline])), reverse=True)

        return render_template("index.html", timeline=timeline, years=years)

    @app.route("/anniversaries")
    def anniversaries():
        # 获取所有纪念日并按日期排序
        dates = KeyDate.query.order_by(KeyDate.date).all()
        return render_template("anniversaries.html", dates=dates)

    # ---- Create Actions (Unified Date Logic) ----

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
        custom_date = request.form.get("custom_date")  # 获取自定义日期

        if content:
            dt = parse_datetime(custom_date)
            db.session.add(Entry(content=content, created_at=dt))
            db.session.commit()
        return redirect(url_for("index"))

    @app.post("/add/keydate")
    def add_keydate():
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date", "").strip()

        if title and date_str:
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
                db.session.add(KeyDate(title=title, date=d))
                db.session.commit()
            except ValueError:
                pass

        # 如果来源是纪念日页面，跳回纪念日页，否则跳回主页
        if "anniversaries" in request.referrer:
            return redirect(url_for("anniversaries"))
        return redirect(url_for("index"))

    @app.post("/add/photo")
    def add_photo():
        file = request.files.get("photo")
        caption = request.form.get("caption", "").strip()
        custom_date = request.form.get("custom_date")  # 获取自定义日期

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

    # ---- Update/Delete (Omitted for brevity, same as before but map fields) ----
    # 简化的删除路由
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