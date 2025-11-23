from datetime import datetime
from urllib.parse import urlparse
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_user, logout_user, current_user, login_required

from ..models import User
from .. import db

auth_bp = Blueprint('auth', __name__)


def choose_next_url():
    next_url = request.args.get('next')
    if not next_url:
        return url_for('main.index')
    parsed = urlparse(next_url)
    if parsed.scheme or parsed.netloc:
        return url_for('main.index')
    return next_url


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(choose_next_url())

    error = None
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            error = '用户名或密码错误'
        else:
            user.last_login_at = datetime.now()
            db.session.commit()
            login_user(user)
            return redirect(choose_next_url())

    return render_template('login.html', error=error, page_id='login')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
