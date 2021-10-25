from flask import Blueprint, redirect, render_template, request

from monolith.auth import login_required
from monolith.database import User, db
from monolith.forms import UserForm,UserDelForm

from flask_login import current_user

users = Blueprint('users', __name__)


@users.route('/users')
@login_required
def _users():
    _users = db.session.query(User)
    return render_template("users.html", users=_users)

@users.route('/profile')
@login_required
def profile():
    # old version commented : remember to check for test coverage
    """firstname   = current_user.get_firstname()
    surname     = current_user.get_surname()
    email       = current_user.get_email()"""
    _user = current_user
    return render_template('profile.html', user=_user) 


@users.route('/create_user', methods=['POST', 'GET'])
def create_user():
    form = UserForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            """
            Password should be hashed with some salt. For example if you choose a hash function x, 
            where x is in [md5, sha1, bcrypt], the hashed_password should be = x(password + s) where
            s is a secret key.
            """
            new_user.set_password(form.password.data)
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
