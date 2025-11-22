import os
import queue
import re
import threading
from datetime import datetime
import requests

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.jinja_env.auto_reload = True

    app.config.from_mapping(
        SECRET_KEY="your-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(
            app.instance_path, "lovejournal.sqlite"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(app.instance_path, "uploads"),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        ALLOWED_EXTENSIONS={"png", "jpg", "jpeg", "gif", "webp"},
    )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    # ========== Models ==========

    class Entry(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
        content = db.Column(db.Text, nullable=False)
        location = db.Column(db.String(255))
        tags = db.Column(db.String(255))

    class KeyDate(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        date = db.Column(db.DateTime, nullable=False, index=True)
        location = db.Column(db.String(255))
        tags = db.Column(db.String(255))

    class Photo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, nullable=False, default=datetime.now, index=True)
        caption = db.Column(db.String(255))
        location = db.Column(db.String(255))
        tags = db.Column(db.String(255))

    with app.app_context():
        db.create_all()

    # ========== Helpers ==========

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    @app.context_processor
    def inject_helpers():
        def get_days_diff(d):
            if not isinstance(d, datetime):
                return (0, "today")
            today = datetime.now().date()
            diff_days = (d.date() - today).days
            if diff_days < 0:
                return (-diff_days, "past")
            if diff_days > 0:
                return (diff_days, "future")
            return (0, "today")

        return dict(get_days_diff=get_days_diff)

    # 【修复重点】增强的坐标过滤器
    # 无论输入是 "36.6,101.7 西宁" 还是 "36.6 101.7 西宁"，都能提取 "36 101 西宁"
    @app.template_filter('clean_geo')
    def clean_geo_filter(value):
        if not value:
            return ""

        # 匹配逻辑：
        # 1. 第一组数字 (整数部分)
        # 2. 中间忽略小数、逗号、空格
        # 3. 第二组数字 (整数部分)
        # 4. 剩余文本
        # 这个正则非常宽容，只要开头有两个数字组，就能识别
        pattern = r'^.*?(-?\d+)(?:\.\d+)?[,，\s]+(-?\d+)(?:\.\d+)?\s*(.*)$'
        match = re.match(pattern, value.strip())

        if match:
            lat_int = match.group(1)
            lng_int = match.group(2)
            rest_text = match.group(3)

            # 组合成 "36 101" 风格
            coord_part = f"{lat_int} {lng_int}"

            # 如果后面还有地名，就拼上去
            if rest_text:
                return f"{coord_part} {rest_text}"
            return coord_part

        return value

    tag_pattern = re.compile(r"#([\w\u4e00-\u9fa5]+)")

    def extract_tags(*texts):
        found = set()
        for t in texts:
            if not t:
                continue
            for m in tag_pattern.findall(t):
                found.add(m.lower())
        return sorted(found)

    def build_tag_index():
        all_tags = set()
        for model in (Entry, Photo, KeyDate):
            for item in model.query.all():
                if not getattr(item, "tags", None):
                    continue
                for t in item.tags.split(","):
                    t = t.strip()
                    if t:
                        all_tags.add(t)
        return sorted(all_tags)

    def build_timeline(search=None, type_filter=None, tag=None):
        search = (search or "").strip().lower()
        type_filter = (type_filter or "all").lower()
        tag = (tag or "").strip().lower()

        def match_text(*parts):
            if not search:
                return True
            blob = " ".join([p or "" for p in parts]).lower()
            return search in blob

        def match_tag(tags_text):
            if not tag:
                return True
            if not tags_text:
                return False
            tags_list = [t.strip() for t in tags_text.split(",") if t.strip()]
            return tag in tags_list

        include_entry = type_filter in ("all", "entry", "text")
        include_photo = type_filter in ("all", "photo", "img", "image")
        include_keydate = type_filter in ("all", "keydate", "date", "anniversary")

        timeline = []

        if include_entry:
            for e in Entry.query.all():
                if not match_tag(e.tags):
                    continue
                if match_text(e.content, e.location):
                    timeline.append({"type": "entry", "timestamp": e.created_at, "item": e})

        if include_keydate:
            for k in KeyDate.query.all():
                if not match_tag(k.tags):
                    continue
                if match_text(k.title, k.location):
                    timeline.append({"type": "keydate", "timestamp": k.date, "item": k})

        if include_photo:
            for p in Photo.query.all():
                if not match_tag(p.tags):
                    continue
                if match_text(p.caption, p.filename, p.location):
                    timeline.append({"type": "photo", "timestamp": p.created_at, "item": p})

        timeline.sort(key=lambda x: x["timestamp"], reverse=True)
        return timeline

    def extract_years(timeline):
        return sorted({node["timestamp"].year for node in timeline}, reverse=True)

    def parse_datetime(value):
        if not value:
            return datetime.now()
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M")
        except ValueError:
            return datetime.now()

    coord_number_re = re.compile(r"(-?\d+(?:\.\d+)?)")
    amap_key = os.getenv("AMAP_WEB_KEY", "fd67dbc2f43a792a5a2aa190e3a49d92")

    def parse_coords_from_location(location_text):
        if not location_text:
            return None
        text = str(location_text).replace("，", ",")
        nums = coord_number_re.findall(text)
        if len(nums) < 2:
            return None
        try:
            lat = float(nums[0])
            lng = float(nums[1])
            if abs(lat) > 90 and abs(lat) <= 180 and abs(lng) <= 90:
                lat, lng = lng, lat
            return lat, lng
        except ValueError:
            return None

    geocode_cache = {}
    geocode_lock = threading.Lock()
    geocode_queue: queue.Queue[str] = queue.Queue()
    geocode_pending = set()

    def geocode_location(location_text):
        if not location_text:
            return None

        with geocode_lock:
            if location_text in geocode_cache:
                return geocode_cache[location_text]

        result = None
        try:
            resp = requests.get(
                "https://restapi.amap.com/v3/geocode/geo",
                params={"key": amap_key, "address": location_text},
                timeout=4,
            )
            data = resp.json()
            if data.get("status") == "1":
                geocodes = data.get("geocodes") or []
                if geocodes:
                    loc = geocodes[0].get("location", "")
                    nums = coord_number_re.findall(loc)
                    if len(nums) >= 2:
                        lng, lat = float(nums[0]), float(nums[1])
                        result = (lat, lng)
        except Exception:
            result = None

        with geocode_lock:
            geocode_cache[location_text] = result
        return result

    def geocode_worker():
        while True:
            location_text = geocode_queue.get()
            try:
                if not location_text:
                    continue
                with geocode_lock:
                    if location_text in geocode_cache:
                        continue
                geocode_location(location_text)
            finally:
                with geocode_lock:
                    geocode_pending.discard(location_text)
                geocode_queue.task_done()

    threading.Thread(target=geocode_worker, daemon=True).start()

    def resolve_location(location_text):
        if not location_text:
            return None
        coords = parse_coords_from_location(location_text)
        if coords:
            return coords
        with geocode_lock:
            if location_text in geocode_cache:
                return geocode_cache[location_text]
        return geocode_location(location_text)

    # ========== Routes ==========

    @app.route("/")
    def index():
        search_query = request.args.get("q", "")
        filter_type = request.args.get("type", "all")
        selected_tag = request.args.get("tag", "").strip().lower()
        page = request.args.get("page", 1, type=int)
        per_page = 24

        full_timeline = build_timeline(search_query, filter_type, selected_tag)
        years = extract_years(full_timeline)

        total = len(full_timeline)
        start = (page - 1) * per_page
        end = start + per_page
        page_items = full_timeline[start:end]
        has_more = end < total

        all_tags = build_tag_index()

        return render_template(
            "index.html",
            timeline=page_items,
            years=years,
            search_query=search_query,
            filter_type=filter_type,
            selected_tag=selected_tag,
            all_tags=all_tags,
            page=page,
            has_more=has_more,
            start_index=start,
        )

    @app.route("/api/timeline")
    def api_timeline():
        search_query = request.args.get("q", "")
        filter_type = request.args.get("type", "all")
        selected_tag = request.args.get("tag", "").strip().lower()
        page = request.args.get("page", 1, type=int)
        per_page = 24

        full_timeline = build_timeline(search_query, filter_type, selected_tag)
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
        markers = []

        def append_marker(item, kind, label, timestamp, snippet, image=None):
            coords = resolve_location(getattr(item, "location", None))
            if not coords:
                coords = resolve_location(label)
            if not coords:
                return

            lat, lng = coords
            markers.append(
                {
                    "id": item.id,
                    "kind": kind,
                    "lat": lat,
                    "lng": lng,
                    "label": label or "",
                    "timestamp": timestamp,
                    "snippet": snippet,
                    "image": image,
                }
            )

        for e in Entry.query.all():
            append_marker(
                e,
                "entry",
                e.location,
                e.created_at.strftime("%Y-%m-%d %H:%M"),
                (e.content or "")[:120],
            )

        for k in KeyDate.query.all():
            append_marker(
                k,
                "keydate",
                k.location,
                k.date.strftime("%Y-%m-%d %H:%M"),
                (k.title or "")[:120],
            )

        for p in Photo.query.all():
            append_marker(
                p,
                "photo",
                p.location,
                p.created_at.strftime("%Y-%m-%d %H:%M"),
                (p.caption or "")[:120],
                image=url_for("uploaded_file", filename=p.filename),
            )

        return render_template("map.html", markers=markers)

    # ====== Create ======

    def merge_location_and_coords(location_text, coords_text):
        location_text = (location_text or "").strip()
        coords_text = (coords_text or "").strip()

        def parse_coords_text(text):
            nums = coord_number_re.findall(text.replace("，", ","))
            if len(nums) < 2:
                return None
            try:
                return (float(nums[0]), float(nums[1]))
            except ValueError:
                return None

        coords_pair = parse_coords_text(coords_text) if coords_text else None

        if not coords_pair and location_text:
            coords_pair = resolve_location(location_text)

        if coords_pair:
            lat, lng = coords_pair
            coords_str = f"{lat:.6f},{lng:.6f}"
            if location_text:
                return f"{coords_str} {location_text}"
            return coords_str

        return location_text or None

    @app.post("/add/entry")
    def add_entry():
        content = request.form.get("content", "").strip()
        custom_date = request.form.get("custom_date")
        location_text = request.form.get("location", "")
        coords_text = request.form.get("location_coords", "")

        if content:
            dt = parse_datetime(custom_date)
            location = merge_location_and_coords(location_text, coords_text)
            tags_list = extract_tags(content, location)
            tags_str = ",".join(tags_list) if tags_list else None

            db.session.add(
                Entry(
                    content=content,
                    created_at=dt,
                    location=location,
                    tags=tags_str,
                )
            )
            db.session.commit()
        return redirect(url_for("index"))

    @app.post("/add/keydate")
    def add_keydate():
        title = request.form.get("title", "").strip()
        date_str = request.form.get("date") or request.form.get("custom_date")
        location_text = request.form.get("location", "")
        coords_text = request.form.get("location_coords", "")

        if title:
            dt = parse_datetime(date_str)
            location = merge_location_and_coords(location_text, coords_text)
            tags_list = extract_tags(title, location)
            tags_str = ",".join(tags_list) if tags_list else None

            db.session.add(
                KeyDate(
                    title=title,
                    date=dt,
                    location=location,
                    tags=tags_str,
                )
            )
            db.session.commit()

        if "anniversaries" in (request.referrer or ""):
            return redirect(url_for("anniversaries"))
        return redirect(url_for("index"))

    @app.post("/add/photo")
    def add_photo():
        file = request.files.get("photo")
        caption = request.form.get("caption", "").strip()
        custom_date = request.form.get("custom_date")
        location_text = request.form.get("location", "")
        coords_text = request.form.get("location_coords", "")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            save_name = filename
            count = 1
            while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], save_name)):
                save_name = f"{base}_{count}{ext}"
                count += 1

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], save_name))

            dt = parse_datetime(custom_date)
            location = merge_location_and_coords(location_text, coords_text)
            tags_list = extract_tags(caption, location)
            tags_str = ",".join(tags_list) if tags_list else None

            db.session.add(
                Photo(
                    filename=save_name,
                    caption=caption,
                    created_at=dt,
                    location=location,
                    tags=tags_str,
                )
            )
            db.session.commit()
        return redirect(url_for("index"))

    # ====== Edit & Delete ======

    @app.post("/edit/<type>/<int:item_id>")
    def edit_item(type, item_id):
        model_map = {"entry": Entry, "keydate": KeyDate, "photo": Photo}
        model = model_map.get(type)
        if not model:
            return redirect(request.referrer or url_for("index"))

        item = db.get_or_404(model, item_id)

        location_text = request.form.get("location", "")
        coords_text = request.form.get("location_coords", "")
        new_location = merge_location_and_coords(location_text, coords_text)

        if type == "entry":
            content = request.form.get("content", "").strip()
            custom_date = request.form.get("custom_date")
            if content:
                item.content = content
            item.created_at = parse_datetime(custom_date)
            item.location = new_location
            tags_list = extract_tags(content, new_location)
            item.tags = ",".join(tags_list) if tags_list else None

        elif type == "keydate":
            title = request.form.get("title", "").strip()
            date_str = request.form.get("date") or request.form.get("custom_date")
            if title:
                item.title = title
            item.date = parse_datetime(date_str)
            item.location = new_location
            tags_list = extract_tags(title, new_location)
            item.tags = ",".join(tags_list) if tags_list else None

        elif type == "photo":
            caption = request.form.get("caption", "").strip()
            custom_date = request.form.get("custom_date")
            file = request.files.get("photo")
            if caption:
                item.caption = caption
            item.created_at = parse_datetime(custom_date)
            item.location = new_location

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                base, ext = os.path.splitext(filename)
                save_name = filename
                count = 1
                while os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], save_name)):
                    save_name = f"{base}_{count}{ext}"
                    count += 1
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], save_name))
                old_path = os.path.join(app.config["UPLOAD_FOLDER"], item.filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except OSError:
                        pass
                item.filename = save_name

            tags_list = extract_tags(caption, new_location)
            item.tags = ",".join(tags_list) if tags_list else None

        db.session.commit()

        if "anniversaries" in (request.referrer or ""):
            return redirect(url_for("anniversaries"))
        return redirect(request.referrer or url_for("index"))

    @app.post("/delete/<type>/<int:item_id>")
    def delete_item(type, item_id):
        model_map = {"entry": Entry, "keydate": KeyDate, "photo": Photo}
        model = model_map.get(type)
        if not model:
            return redirect(request.referrer or url_for("index"))
        item = db.get_or_404(model, item_id)

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
