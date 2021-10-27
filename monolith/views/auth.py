from flask import Blueprint, redirect, render_template, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from monolith.auth import login_required
from monolith.database import User, db
from monolith.forms import LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect('/')
    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@auth.route('/unregister', methods=['GET', 'POST'])
@login_required
def unregister():
    if request.method == 'GET':
        return render_template('unregister.html')
    elif request.method == 'POST':
        password = current_user.get_password_hash()
        inserted_password = request.form['password']
        # unregistration confirmed
        if (check_password_hash(password, inserted_password)):
            unregister_user = User.query.filter_by(firstname=current_user.get_firstname()).first()
            db.session.delete(unregister_user)
            db.session.commit()
            return redirect('/')
        # try again (password does not match)
        else:
            error = "Wrong password, try again"
            return {'msg': 'Password does not match, try again'}, 400
