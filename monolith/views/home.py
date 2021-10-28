from flask import Blueprint, render_template,session

from monolith.auth import current_user

home = Blueprint('home', __name__)


@home.route('/')
def index():
    if current_user is not None and hasattr(current_user, 'id'):
        if current_user.is_admin:
            welcome = "Logged In as Admin!"
        else:
            welcome = "Logged In!"
    else:
        welcome = None
        session['draft_id']=None
        session['chosen_recipient']=[]
    return render_template("index.html", welcome=welcome)
