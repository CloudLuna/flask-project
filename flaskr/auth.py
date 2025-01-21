import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


## View: Register
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

## View: login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        #  .fetchone() returns 1 row from the query

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            #  check_password_hash hashes the submitted password in the same way as the stored one and securely compares them.
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            #  session is a dict that stores data across requests. In this case user ID is stored in a new session (the data is stored in a cookie that is sent to tyhe browser, and the browser then sends it back in subsecuent requests(flask makes it safer somehow))
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

#Antes que cualquier request: check session (to see if someonne is loged in)
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

#Logout: remove user id from session
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


#Required authentication for others (create/edit/delete blog content)
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
# It  checks if a user is loaded and redirects to the login page otherwise