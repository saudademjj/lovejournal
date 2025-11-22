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
        # 用逗号分隔的小写标签，如 "旅行,吵架"
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
        db.create_all()  # 如果新增字段（location/tags）报错，需要迁移或重建库

    # ========== Helpers ==========

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

    @app.context_processor
    def inject_helpers():
        def get_days_diff(d):
            """返回 (diff, state)；state: past / future / today"""
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

    tag_pattern = re.compile(r"#([\w\u4e00-\u9fa5]+)")

    def extract_tags(*texts):
        """从多段文本里解析 #标签，全部转小写去重"""
        found = set()
        for t in texts:
            if not t:
                continue
            for m in tag_pattern.findall(t):
                found.add(m.lower())
        return sorted(found)

    def build_tag_index():
        """把所有 Entry/Photo/KeyDate 里的 tags 字段扫一遍，做个标签云"""
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
        """
        混排 Entry / KeyDate / Photo 成时间轴列表
        search: 关键词
        type_filter: all / entry / photo / keydate
        tag: 单个标签过滤
        """
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
    amap_key = os.getenv("AMAP_WEB_KEY", "7432049c00644e7496cd0151d59380c9")

    def parse_coords_from_location(location_text):
        """
        更鲁棒的坐标解析：
        - 支持 '31.23,121.47 Shanghai'
        - 支持 '31.23 121.47'
        - 自动忽略后面的中文或其他文本
        - 如果用户把「经纬度」写反（高德接口返回 lng,lat），自动调整
        """
        if not location_text:
            return None
        text = str(location_text).replace("，", ",")
        nums = coord_number_re.findall(text)
        if len(nums) < 2:
            return None
        try:
            lat = float(nums[0])
            lng = float(nums[1])
            # 如果首个数值不在正常纬度范围，而第二个数值在，则认为用户写反了
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
        """使用高德 Web API 将地点文本转为坐标，缓存结果减少重复请求"""
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
        """
        统一把地点文本转换为 (lat, lng)：
        1. 先尝试从文本中直接解析坐标
        2. 再尝试从缓存里取
        3. 最后同步调用高德地理编码接口
        """
        if not location_text:
            return None

        coords = parse_coords_from_location(location_text)
        if coords:
            return coords

        with geocode_lock:
            if location_text in geocode_cache:
                return geocode_cache[location_text]

        # 缓存里也没有，直接请求一次
        return geocode_location(location_text)

    def resolve_location_async(location_text):
        """
        在请求线程里尽量不阻塞：
        1. 尝试解析坐标或读取缓存
        2. 未命中时把地址放到后台队列，等待异步 geocode_worker 处理
        """
        if not location_text:
            return None

        coords = parse_coords_from_location(location_text)
        if coords:
            return coords

        with geocode_lock:
            if location_text in geocode_cache:
                return geocode_cache[location_text]
            if location_text not in geocode_pending:
                geocode_pending.add(location_text)
                geocode_queue.put(location_text)

        return None

    def build_on_this_day():
        """
        “那年今日”：找出往年同月同日的记录（不包含今年）
        返回按时间倒序的列表（可能多条）
        """
        today = datetime.now()
        full = build_timeline()
        result = []
        for node in full:
            ts = node["timestamp"]
            if ts.month == today.month and ts.day == today.day and ts.year < today.year:
                result.append(node)
        # 最新的在前
        result.sort(key=lambda x: x["timestamp"], reverse=True)
        return result

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

        on_this_day = None
        # 只在“默认视图”下显示那年今日：没有搜索、没有过滤、没有标签
        if not search_query and filter_type == "all" and not selected_tag:
            otd_list = build_on_this_day()
            if otd_list:
                on_this_day = otd_list[0]

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
            on_this_day=on_this_day,
        )

    @app.route("/api/timeline")
    def api_timeline():
        """无限滚动加载更多时间轴行"""
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
        """地图视图 + 热力图"""
        markers = []

        def append_marker(item, kind, label, timestamp, snippet, image=None):
            # 用同步解析，确保立即拿到坐标；否则会被跳过导致地图空白
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
                (e.content or "")[:80],
            )

        for k in KeyDate.query.all():
            append_marker(
                k,
                "keydate",
                k.location,
                k.date.strftime("%Y-%m-%d %H:%M"),
                (k.title or "")[:80],
            )

        for p in Photo.query.all():
            append_marker(
                p,
                "photo",
                p.location,
                p.created_at.strftime("%Y-%m-%d %H:%M"),
                (p.caption or "")[:80],
                image=url_for("uploaded_file", filename=p.filename),
            )

        return render_template("map.html", markers=markers)

    # ====== Create ======

    def merge_location_and_coords(location_text, coords_text):
        """
        把前端写入的地点文本 + coords 拼在一起：
        - coords 为 "lat,lng"
        - 存库格式："lat,lng 北京 三里屯"
        - 若用户没点 AUTO，也尝试后端同步地理编码，避免地图为空
        """
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

        # 没有前端返回的坐标，则用后端同步解析一次
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
                # 删除旧文件
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
