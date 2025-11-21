from flask import (
    Flask, render_template, request, redirect,
    url_for, send_from_directory, jsonify
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
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
        content = db.Column(db.Text, nullable=False)
        # 新增：地点文本（可写“上海 徐家汇”或“31.23,121.47 Shanghai”）
        location = db.Column(db.String(255))

    class KeyDate(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        # 记录完整日期+时间
        date = db.Column(db.DateTime, nullable=False, index=True)
        location = db.Column(db.String(255))

    class Photo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
        caption = db.Column(db.String(255))
        location = db.Column(db.String(255))

    with app.app_context():
        db.create_all()  # 如已有数据且要新增字段，建议用迁移工具或手动 ALTER

    # ---- Helpers ----
    def allowed_file(filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    @app.context_processor
    def inject_helpers():
        def get_days_diff(d):
            """返回 (diff, state)；state: past / future / today"""
            today = datetime.now()
            target = d
            if isinstance(d, datetime):
                pass
            diff = (target.date() - today.date()).days
            if diff < 0:
                return (abs(diff), "past")
            if diff > 0:
                return (diff, "future")
            return (0, "today")

        return dict(get_days_diff=get_days_diff)

    # ---- Query Helpers ----

    def build_timeline(search=None, type_filter=None):
        """
        将 Entry / KeyDate / Photo 混排为统一时间轴，并支持关键词 & 类型过滤
        """
        search = (search or "").strip().lower()
        type_filter = (type_filter or "all").lower()

        def match_text(*parts):
            if not search:
                return True
            blob = " ".join([p or "" for p in parts]).lower()
            return search in blob

        include_entry = type_filter in ("all", "entry", "text")
        include_photo = type_filter in ("all", "photo", "img", "image")
        include_keydate = type_filter in ("all", "keydate", "date", "anniversary")

        timeline = []

        if include_entry:
            for e in Entry.query.all():
                if match_text(e.content, e.location):
                    timeline.append({"type": "entry", "timestamp": e.created_at, "item": e})

        if include_keydate:
            for k in KeyDate.query.all():
                if match_text(k.title, k.location):
                    timeline.append({"type": "keydate", "timestamp": k.date, "item": k})

        if include_photo:
            for p in Photo.query.all():
                if match_text(p.caption, p.filename, p.location):
                    timeline.append({"type": "photo", "timestamp": p.created_at, "item": p})

        # 最新在前
        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline

    def extract_years(timeline):
        return sorted({t["timestamp"].year for t in timeline}, reverse=True)

    def parse_datetime(date_str):
        """解析前端传入的 datetime-local 字符串，如果空则返回现在"""
        if not date_str:
            return datetime.now()
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return datetime.now()

    def parse_coords_from_location(location_text):
        """
        从 location 文本中尝试解析出 "lat,lng" 浮点数对；
        例如：'31.2304,121.4737 Shanghai' -> (31.2304, 121.4737)
        """
        if not location_text:
            return None
        txt = location_text.replace("，", ",")
        # 只看前两个逗号分隔字段
        parts = [p.strip() for p in txt.split(",")[:2]]
        if len(parts) < 2:
            return None
        try:
            lat = float(parts[0])
            lng = float(parts[1])
            return (lat, lng)
        except ValueError:
            return None

    # ---- Routes ----

    @app.route("/")
    def index():
        # 搜索 & 类型过滤
        search_query = request.args.get("q", "")
        filter_type = request.args.get("type", "all")
        page = request.args.get("page", 1, type=int)
        per_page = 24

        full_timeline = build_timeline(search_query, filter_type)
        total = len(full_timeline)

        start = (page - 1) * per_page
        end = start + per_page
        page_items = full_timeline[start:end]
        has_more = end < total

        years = extract_years(full_timeline)

        return render_template(
            "index.html",
            timeline=page_items,
            years=years,
            search_query=search_query,
            filter_type=filter_type,
            page=page,
            has_more=has_more,
            start_index=start,
        )

    @app.route("/api/timeline")
    def api_timeline():
        """无限加载使用：返回新增的时间轴 HTML 片段"""
        search_query = request.args.get("q", "")
        filter_type = request.args.get("type", "all")
        page = request.args.get("page", 1, type=int)
        per_page = 24

        full_timeline = build_timeline(search_query, filter_type)
        total = len(full_timeline)

        start = (page - 1) * per_page
        end = start + per_page
        page_items = full_timeline[start:end]
        has_more = end < total

        html = render_template("_timeline_rows.html", timeline=page_items, start_index=start)
        return jsonify({"html": html, "has_more": has_more})

    @app.route("/anniversaries")
    def anniversaries():
        dates = KeyDate.query.order_by(KeyDate.date).all()
        return render_template("anniversaries.html", dates=dates)

    @app.route("/map")
    def map_view():
        """地图视图：把带经纬度的 location 渲染到地图上"""
        markers = []

        for e in Entry.query.filter(Entry.location.isnot(None)).all():
            coords = parse_coords_from_location(e.location)
            if not coords:
                continue
            markers.append(
                {
                    "id": e.id,
                    "kind": "entry",
                    "lat": coords[0],
                    "lng": coords[1],
                    "label": e.location,
                    "timestamp": e.created_at.strftime("%Y-%m-%d %H:%M"),
                    "snippet": (e.content or "")[:80],
                }
            )

        for k in KeyDate.query.filter(KeyDate.location.isnot(None)).all():
            coords = parse_coords_from_location(k.location)
            if not coords:
                continue
            markers.append(
                {
                    "id": k.id,
                    "kind": "keydate",
                    "lat": coords[0],
                    "lng": coords[1],
                    "label": k.location,
                    "timestamp": k.date.strftime("%Y-%m-%d %H:%M"),
                    "snippet": (k.title or "")[:80],
                }
            )

        for p in Photo.query.filter(Photo.location.isnot(None)).all():
            coords = parse_coords_from_location(p.location)
            if not coords:
                continue
            markers.append(
                {
                    "id": p.id,
                    "kind": "photo",
                    "lat": coords[0],
                    "lng": coords[1],
                    "label": p.location,
                    "timestamp": p.created_at.strftime("%Y-%m-%d %H:%M"),
                    "snippet": (p.caption or "")[:80],
                    "image": url_for("uploaded_file", filename=p.filename),
                }
            )

        return render_template("map.html", markers=markers)

    # ---- Create Actions ----

    @app.post("/add/entry")
    def add_entry():
        content = request.form.get("content", "").strip()
        custom_date = request.form.get("custom_date")
        location = request.form.get("location", "").strip() or None

        if content:
            dt = parse_datetime(custom_date)
            db.session.add(Entry(content=content, created_at=dt, location=location))
            db.session.commit()
        return redirect(url_for("index"))

    @app.post("/add/keydate")
    def add_keydate():
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date", "").strip()
        location = request.form.get("location", "").strip() or None

        if title:
            dt = parse_datetime(date_str)
            db.session.add(KeyDate(title=title, date=dt, location=location))
            db.session.commit()

        if "anniversaries" in (request.referrer or ""):
            return redirect(url_for("anniversaries"))
        return redirect(url_for("index"))

    @app.post("/add/photo")
    def add_photo():
        file = request.files.get("photo")
        caption = request.form.get("caption", "").strip()
        custom_date = request.form.get("custom_date")
        location = request.form.get("location", "").strip() or None

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
            db.session.add(Photo(filename=save_name, caption=caption, created_at=dt, location=location))
            db.session.commit()
        return redirect(url_for("index"))

    # ---- Edit & Delete ----

    @app.post("/edit/<type>/<int:id>")
    def edit_item(type, id):
        """统一编辑入口：Entry / KeyDate / Photo"""
        model_map = {"entry": Entry, "keydate": KeyDate, "photo": Photo}
        model = model_map.get(type)
        if not model:
            return redirect(request.referrer or url_for("index"))

        item = db.get_or_404(model, id)

        # 通用地点
        location = request.form.get("location", "").strip()
        if hasattr(item, "location"):
            item.location = location or None

        if type == "entry":
            content = request.form.get("content", "").strip()
            if content:
                item.content = content
            custom_date = request.form.get("custom_date")
            item.created_at = parse_datetime(custom_date)

        elif type == "keydate":
            title = request.form.get("title", "").strip()
            if title:
                item.title = title
            date_str = request.form.get("date") or request.form.get("custom_date")
            item.date = parse_datetime(date_str)

        elif type == "photo":
            caption = request.form.get("caption", "").strip()
            item.caption = caption
            custom_date = request.form.get("custom_date")
            item.created_at = parse_datetime(custom_date)

            file = request.files.get("photo")
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                count = 1
                save_name = filename
                while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], save_name)):
                    save_name = f"{base}_{count}{ext}"
                    count += 1

                file.save(os.path.join(app.config["UPLOAD_FOLDER"], save_name))

                # 删除旧文件（忽略失败）
                old_path = os.path.join(app.config["UPLOAD_FOLDER"], item.filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass
                item.filename = save_name

        db.session.commit()

        if "anniversaries" in (request.referrer or ""):
            return redirect(url_for("anniversaries"))
        return redirect(request.referrer or url_for("index"))

    @app.post("/delete/<type>/<int:id>")
    def delete_item(type, id):
        model = {"entry": Entry, "keydate": KeyDate, "photo": Photo}.get(type)
        if model:
            item = db.get_or_404(model, id)
            # 顺便清理图片文件
            if type == "photo":
                img_path = os.path.join(app.config["UPLOAD_FOLDER"], item.filename)
                if os.path.exists(img_path):
                    try:
                        os.remove(img_path)
                    except OSError:
                        pass
            db.session.delete(item)
            db.session.commit()
        return redirect(request.referrer or url_for("index"))

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
