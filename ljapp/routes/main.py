import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename

from .. import db
from ..models import Entry, KeyDate, Photo
from ..utils import (
    allowed_file,
    extract_tags,
    parse_datetime,
)

main_bp = Blueprint('main', __name__)


def build_tag_index():
    all_tags = set()
    for model in (Entry, Photo, KeyDate):
        for item in model.query.all():
            if not getattr(item, 'tags', None):
                continue
            for t in item.tags.split(','):
                t = t.strip()
                if t:
                    all_tags.add(t)
    return sorted(all_tags)


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


def extract_years(timeline):
    return sorted({node['timestamp'].year for node in timeline}, reverse=True)


@main_bp.route('/')
@login_required
def index():
    search_query = request.args.get('q', '')
    filter_type = request.args.get('type', 'all')
    selected_tag = request.args.get('tag', '').strip().lower()
    page = request.args.get('page', 1, type=int)
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
        'index.html',
        page_id='index',
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


@main_bp.route('/anniversaries')
@login_required
def anniversaries():
    dates = KeyDate.query.order_by(KeyDate.date).all()
    return render_template('anniversaries.html', dates=dates, page_id='anniversaries')


@main_bp.route('/map')
@login_required
def map_view():
    geo_helper = current_app.extensions.get('geo_helper')
    markers = []

    def resolve_location(text):
        if not geo_helper:
            return None
        return geo_helper.resolve_location(text)

    def append_marker(item, kind, label, timestamp, snippet, image=None):
        coords = resolve_location(getattr(item, 'location', None))
        if not coords and label:
            coords = resolve_location(label)
        if not coords:
            return
        lat, lng = coords
        markers.append(
            {
                'id': item.id,
                'kind': kind,
                'lat': lat,
                'lng': lng,
                'label': label or '',
                'timestamp': timestamp,
                'snippet': snippet,
                'image': image,
            }
        )

    for e in Entry.query.all():
        append_marker(
            e,
            'entry',
            e.location,
            e.created_at.strftime('%Y-%m-%d %H:%M'),
            (e.content or '')[:120],
        )

    for k in KeyDate.query.all():
        append_marker(
            k,
            'keydate',
            k.location,
            k.date.strftime('%Y-%m-%d %H:%M'),
            (k.title or '')[:120],
        )

    for p in Photo.query.all():
        append_marker(
            p,
            'photo',
            p.location,
            p.created_at.strftime('%Y-%m-%d %H:%M'),
            (p.caption or '')[:120],
            image=url_for('main.uploaded_file', filename=p.filename),
        )

    return render_template('map.html', markers=markers, page_id='map')


@main_bp.post('/add/entry')
@login_required
def add_entry():
    geo_helper = current_app.extensions.get('geo_helper')
    content = request.form.get('content', '').strip()
    custom_date = request.form.get('custom_date')
    location_text = request.form.get('location', '')
    coords_text = request.form.get('location_coords', '')

    if content:
        dt = parse_datetime(custom_date)
        location = geo_helper.merge_location_and_coords(location_text, coords_text) if geo_helper else location_text
        tags_list = extract_tags(content, location)
        tags_str = ','.join(tags_list) if tags_list else None

        db.session.add(
            Entry(
                content=content,
                created_at=dt,
                location=location,
                tags=tags_str,
            )
        )
        db.session.commit()
    return redirect(url_for('main.index'))


@main_bp.post('/add/keydate')
@login_required
def add_keydate():
    geo_helper = current_app.extensions.get('geo_helper')
    title = request.form.get('title', '').strip()
    date_str = request.form.get('date') or request.form.get('custom_date')
    location_text = request.form.get('location', '')
    coords_text = request.form.get('location_coords', '')

    if title:
        dt = parse_datetime(date_str)
        location = geo_helper.merge_location_and_coords(location_text, coords_text) if geo_helper else location_text
        tags_list = extract_tags(title, location)
        tags_str = ','.join(tags_list) if tags_list else None

        db.session.add(
            KeyDate(
                title=title,
                date=dt,
                location=location,
                tags=tags_str,
            )
        )
        db.session.commit()

    if 'anniversaries' in (request.referrer or ''):
        return redirect(url_for('main.anniversaries'))
    return redirect(url_for('main.index'))


@main_bp.post('/add/photo')
@login_required
def add_photo():
    geo_helper = main_bp.app.extensions.get('geo_helper') if hasattr(main_bp, 'app') else None
    file = request.files.get('photo')
    caption = request.form.get('caption', '').strip()
    custom_date = request.form.get('custom_date')
    location_text = request.form.get('location', '')
    coords_text = request.form.get('location_coords', '')

    if file and allowed_file(file.filename, current_app.config.get('ALLOWED_EXTENSIONS', set())):
        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        save_name = filename
        count = 1
        upload_folder = current_app.config['UPLOAD_FOLDER']
        while os.path.exists(os.path.join(upload_folder, save_name)):
            save_name = f"{base}_{count}{ext}"
            count += 1

        file.save(os.path.join(upload_folder, save_name))

        dt = parse_datetime(custom_date)
        location = geo_helper.merge_location_and_coords(location_text, coords_text) if geo_helper else location_text
        tags_list = extract_tags(caption, location)
        tags_str = ','.join(tags_list) if tags_list else None

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
    return redirect(url_for('main.index'))


@main_bp.post('/edit/<type>/<int:item_id>')
@login_required
def edit_item(type, item_id):
    geo_helper = current_app.extensions.get('geo_helper')
    model_map = {'entry': Entry, 'keydate': KeyDate, 'photo': Photo}
    model = model_map.get(type)
    if not model:
        return redirect(request.referrer or url_for('main.index'))

    item = db.get_or_404(model, item_id)

    location_text = request.form.get('location', '')
    coords_text = request.form.get('location_coords', '')
    new_location = geo_helper.merge_location_and_coords(location_text, coords_text) if geo_helper else location_text

    if type == 'entry':
        content = request.form.get('content', '').strip()
        custom_date = request.form.get('custom_date')
        if content:
            item.content = content
        item.created_at = parse_datetime(custom_date)
        item.location = new_location
        tags_list = extract_tags(content, new_location)
        item.tags = ','.join(tags_list) if tags_list else None

    elif type == 'keydate':
        title = request.form.get('title', '').strip()
        date_str = request.form.get('date') or request.form.get('custom_date')
        if title:
            item.title = title
        item.date = parse_datetime(date_str)
        item.location = new_location
        tags_list = extract_tags(title, new_location)
        item.tags = ','.join(tags_list) if tags_list else None

    elif type == 'photo':
        caption = request.form.get('caption', '').strip()
        custom_date = request.form.get('custom_date')
        file = request.files.get('photo')
        if caption:
            item.caption = caption
        item.created_at = parse_datetime(custom_date)
        item.location = new_location

        if file and allowed_file(file.filename, current_app.config.get('ALLOWED_EXTENSIONS', set())):
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            save_name = filename
            count = 1
            upload_folder = current_app.config['UPLOAD_FOLDER']
            while os.path.exists(os.path.join(upload_folder, save_name)):
                save_name = f"{base}_{count}{ext}"
                count += 1
            file.save(os.path.join(upload_folder, save_name))
            old_path = os.path.join(upload_folder, item.filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except OSError:
                    pass
            item.filename = save_name

        tags_list = extract_tags(caption, new_location)
        item.tags = ','.join(tags_list) if tags_list else None

    db.session.commit()

    if 'anniversaries' in (request.referrer or ''):
        return redirect(url_for('main.anniversaries'))
    return redirect(request.referrer or url_for('main.index'))


@main_bp.post('/delete/<type>/<int:item_id>')
@login_required
def delete_item(type, item_id):
    model_map = {'entry': Entry, 'keydate': KeyDate, 'photo': Photo}
    model = model_map.get(type)
    if not model:
        return redirect(request.referrer or url_for('main.index'))
    item = db.get_or_404(model, item_id)

    if type == 'photo':
        img_path = os.path.join(current_app.config['UPLOAD_FOLDER'], item.filename)
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass

    db.session.delete(item)
    db.session.commit()
    return redirect(request.referrer or url_for('main.index'))


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
