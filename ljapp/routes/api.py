from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from ..models import Entry, Photo, KeyDate

api_bp = Blueprint('api', __name__)


def build_timeline(search=None, type_filter=None, tag=None):
    search = (search or '').strip().lower()
    type_filter = (type_filter or 'all').lower()
    tag = (tag or '').strip().lower()

    def match_text(*parts):
        if not search:
            return True
        blob = ' '.join([p or '' for p in parts]).lower()
        return search in blob

    def match_tag(tags_text):
        if not tag:
            return True
        if not tags_text:
            return False
        tags_list = [t.strip() for t in tags_text.split(',') if t.strip()]
        return tag in tags_list

    include_entry = type_filter in ('all', 'entry', 'text')
    include_photo = type_filter in ('all', 'photo', 'img', 'image')
    include_keydate = type_filter in ('all', 'keydate', 'date', 'anniversary')

    timeline = []

    if include_entry:
        for e in Entry.query.all():
            if not match_tag(e.tags):
                continue
            if match_text(e.content, e.location):
                timeline.append({'type': 'entry', 'timestamp': e.created_at, 'item': e})

    if include_keydate:
        for k in KeyDate.query.all():
            if not match_tag(k.tags):
                continue
            if match_text(k.title, k.location):
                timeline.append({'type': 'keydate', 'timestamp': k.date, 'item': k})

    if include_photo:
        for p in Photo.query.all():
            if not match_tag(p.tags):
                continue
            if match_text(p.caption, p.filename, p.location):
                timeline.append({'type': 'photo', 'timestamp': p.created_at, 'item': p})

    timeline.sort(key=lambda x: x['timestamp'], reverse=True)
    return timeline


@api_bp.get('/timeline')
@login_required
def api_timeline():
    search_query = request.args.get('q', '')
    filter_type = request.args.get('type', 'all')
    selected_tag = request.args.get('tag', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 24

    full_timeline = build_timeline(search_query, filter_type, selected_tag)
    total = len(full_timeline)

    start = (page - 1) * per_page
    end = start + per_page
    page_items = full_timeline[start:end]
    has_more = end < total

    html = render_template('_timeline_rows.html', timeline=page_items, start_index=start)
    return jsonify({'html': html, 'has_more': has_more})
