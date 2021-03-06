from flask import Blueprint, render_template

from monolith.auth import current_user


home = Blueprint('home', __name__)


@home.route('/')
def index():
    '''Manage the homepage of a user.'''
    # check if user is logged in
    if current_user is not None and hasattr(current_user, 'id'):
        # checks if admin
        if current_user.is_admin:
            welcome = 'Logged In as Admin!'
        else:
            welcome = ''
    else:
        welcome = None
    return render_template('index.html', welcome=welcome)
