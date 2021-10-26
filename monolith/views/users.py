from flask import Blueprint, redirect, render_template, request

from ..image import save_profile_picture

from monolith.auth import login_required
from monolith.database import User, db
from monolith.forms import UserForm,UserDelForm

from flask_login import current_user

users = Blueprint('users', __name__)


DEFAULT_PROFILE_PIC = "static/profile/default.png"
PROFILE_PIC_PATH = "static/profile/"

@users.route('/users')
@login_required
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)

@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    _user = current_user
    if (request.method == 'GET'):
        return render_template('profile.html', user=_user) 
    elif (request.method == 'POST'):
        if request.method == 'POST':
            # check if image present
            if ('file' not in request.files):
                return redirect(request.url)
            file = request.files['file']
            if (file.filename == ''):
                return redirect(request.url)
            if file:
                filename = PROFILE_PIC_PATH + save_profile_picture(file)
                _user.set_profile_pic(filename)
                db.session.commit()
                return render_template('profile.html', user=_user) 


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
            return redirect('/users')
    elif request.method == 'GET':
        return render_template('create_user.html', form=form)
    else:
        raise RuntimeError('This should not happen!')

@users.route('/delete_user', methods=['POST','GET'])
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
    else:
        raise RuntimeError('This should not happen!')
