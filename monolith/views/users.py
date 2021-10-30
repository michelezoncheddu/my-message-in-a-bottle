from flask import Blueprint, redirect, render_template, request

from ..image import allowed_file, save_image

from werkzeug.utils import secure_filename
from monolith.auth import login_required, admin_required
from monolith.database import User, db
from monolith.forms import UserForm,UserDelForm

from flask_login import current_user

users = Blueprint('users', __name__)

# GLOBALS
DEFAULT_PROFILE_PIC = "static/profile/default.png"
PROFILE_PIC_PATH = "monolith/static/profile/"

# utility function for applying an action: Ban, Unban, Report, Reject (a report request)
def moderateAction(email, action):
    u = db.session.query(User).filter(User.email == email)
    _user = u.first()
    if (_user is None):
        raise RuntimeError('Reported user not found in DB, this should not happen!')
    
    # if ban
    if (action == "Ban" and not _user.is_banned):
        _user.set_banned(True)
        _user.set_reported(False)
        db.session.commit()
    # if unban
    elif (action == "Unban" and _user.is_banned):
        _user.set_banned(False)
        db.session.commit()
    # if reject
    elif (action == "Reject"):
        _user.set_reported(False)
        db.session.commit()
    # if report
    elif (action == "Report" and not _user.is_reported):
        _user.set_reported(True)
        db.session.commit()


@login_required
def get_users():
    return db.session.query(User)


@users.route('/users', methods=['POST', 'GET'])
@login_required
def _users():
    isAdmin = current_user.is_admin
    _users = db.session.query(User)
    # if admin : show Ban button
    if (isAdmin): 
        action_template = "Ban"
    # if user : show Report button
    else:
        action_template = "Report"
    
    if (request.method == 'GET'):
        return render_template("users.html", users=_users, action=action_template)
    elif (request.method == 'POST'):
        # retrieve action and target user email
        action_todo = request.form["action"]
        email = request.form.get("email")
        moderateAction(email, action_todo) # apply action
        if (action_todo == "Report"):
            return {'msg': 'User successfully reported'}, 200
        elif (action_todo == "Ban" or action_todo == "Unban"):
            return render_template("users.html", users=_users, action=action_template)


@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    _user = current_user
    if (request.method == 'GET'):
        return render_template('profile.html', user=_user)
    # change profile picture
    elif (request.method == 'POST'):
        # image not present : error
        if ('file' not in request.files):
            return {'msg': 'No selected file'}, 400
        file = request.files['file']
        # image present : get file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_image(file, PROFILE_PIC_PATH) # store
            filename = 'static/profile/' + filename
            _user.set_profile_pic(filename)
            db.session.commit()
            return render_template('profile.html', user=_user)
        else:
            return {'msg': 'Invalid file format: <png>, <jpg> and <jpeg> allowed'}, 400


@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            new_user.set_password(form.password.data)
            new_user.set_profile_pic(DEFAULT_PROFILE_PIC)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)

@users.route('/reported_users', methods=['POST', 'GET'])
@login_required
@admin_required
def moderate():
    _users = db.session.query(User)    
    if (request.method == 'GET'):
        return render_template("reported_users.html", users=_users)
    elif (request.method == 'POST'):
        # retrieve action and target user email
        action = request.form["action"]
        email = request.form.get("email")
        moderateAction(email, action) # apply action
        return render_template("reported_users.html", users=_users)

@users.route('/delete_user', methods=['POST','GET'])
@login_required
@admin_required
def delete_user():
    form = UserDelForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            del_user = User.query.filter_by(firstname=form.firstname.data).first()
            db.session.delete(del_user)
            db.session.commit()
            db.session.commit()

            return redirect('/users')
    elif request.method == 'GET':
        return render_template('delete_user.html', form=form)
