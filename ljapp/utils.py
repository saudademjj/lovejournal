import os
import queue
import re
import threading
from datetime import datetime

import bleach
import requests
from markdown import markdown as md_render

markdown_tags = set(bleach.sanitizer.ALLOWED_TAGS).union(
    {"p", "pre", "code", "hr", "br", "h1", "h2", "h3", "h4", "h5", "h6"}
)
markdown_attrs = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title"],
}
markdown_exts = ["fenced_code", "tables", "sane_lists", "nl2br"]


def render_markdown(text):
    if not text:
        return ""
    html = md_render(text, extensions=markdown_exts)
    return bleach.clean(html, tags=markdown_tags, attributes=markdown_attrs, strip=True)


def allowed_file(filename: str, allowed=None) -> bool:
    allowed = allowed or set()
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def register_filters(app):
    @app.template_filter("clean_geo")
    def clean_geo_filter(value):
        if not value:
            return ""
        pattern = r'^.*?(-?\d+)(?:\.\d+)?[,，\s]+(-?\d+)(?:\.\d+)?\s*(.*)$'
        match = re.match(pattern, str(value).strip())
        if match:
            lat_int = match.group(1)
            lng_int = match.group(2)
            rest_text = match.group(3)
            coord_part = f"{lat_int} {lng_int}"
            if rest_text:
                return f"{coord_part} {rest_text}"
            return coord_part
        return value


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


def parse_datetime(value):
    if not value:
        return datetime.now()
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except ValueError:
        return datetime.now()


tag_pattern = re.compile(r"#([\w\u4e00-\u9fa5]+)")


def extract_tags(*texts):
    found = set()
    for t in texts:
        if not t:
            continue
        for m in tag_pattern.findall(t):
            found.add(m.lower())
    return sorted(found)


class GeoHelper:
    def __init__(self, amap_key: str):
        self.amap_key = amap_key
        self.coord_number_re = re.compile(r"(-?\d+(?:\.\d+)?)")
        self.geocode_cache = {}
        self.geocode_lock = threading.Lock()
        self.geocode_queue: queue.Queue[str] = queue.Queue()
        self.geocode_pending = set()

    def parse_coords_from_location(self, location_text):
        if not location_text:
            return None
        text = str(location_text).replace("，", ",")
        nums = self.coord_number_re.findall(text)
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

    def geocode_location(self, location_text):
        if not location_text:
            return None
        with self.geocode_lock:
            if location_text in self.geocode_cache:
                return self.geocode_cache[location_text]

        result = None
        try:
            resp = requests.get(
                "https://restapi.amap.com/v3/geocode/geo",
                params={"key": self.amap_key, "address": location_text},
                timeout=4,
            )
            data = resp.json()
            if data.get("status") == "1":
                geocodes = data.get("geocodes") or []
                if geocodes:
                    loc = geocodes[0].get("location", "")
                    nums = self.coord_number_re.findall(loc)
                    if len(nums) >= 2:
                        lng, lat = float(nums[0]), float(nums[1])
                        result = (lat, lng)
        except Exception:
            result = None

        with self.geocode_lock:
            self.geocode_cache[location_text] = result
        return result

    def geocode_worker(self):
        while True:
            location_text = self.geocode_queue.get()
            try:
                if not location_text:
                    continue
                with self.geocode_lock:
                    if location_text in self.geocode_cache:
                        continue
                self.geocode_location(location_text)
            finally:
                with self.geocode_lock:
                    self.geocode_pending.discard(location_text)
                self.geocode_queue.task_done()

    def start_worker(self):
        threading.Thread(target=self.geocode_worker, daemon=True).start()

    def resolve_location(self, location_text):
        if not location_text:
            return None
        coords = self.parse_coords_from_location(location_text)
        if coords:
            return coords
        with self.geocode_lock:
            if location_text in self.geocode_cache:
                return self.geocode_cache[location_text]
        return self.geocode_location(location_text)

    def merge_location_and_coords(self, location_text, coords_text):
        location_text = (location_text or "").strip()
        coords_text = (coords_text or "").strip()

        def parse_coords_text(text):
            nums = self.coord_number_re.findall(text.replace("，", ","))
            if len(nums) < 2:
                return None
            try:
                return (float(nums[0]), float(nums[1]))
            except ValueError:
                return None

        coords_pair = parse_coords_text(coords_text) if coords_text else None
        if not coords_pair and location_text:
            coords_pair = self.resolve_location(location_text)

        if coords_pair:
            lat, lng = coords_pair
            coords_str = f"{lat:.6f},{lng:.6f}"
            if location_text:
                return f"{coords_str} {location_text}"
            return coords_str

        return location_text or None
