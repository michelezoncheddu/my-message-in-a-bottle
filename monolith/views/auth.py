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
    if request.method == 'POST':
        result = form.validate_on_submit()
        if result[0]:
            email= form.data['email']
            user = db.session.query(User).filter(User.email==email, User.is_active == True).first()
            login_user(user)
            return redirect('/')
        else: 
            error = result[1]
            return render_template('login.html', form=form, error=error),409
    elif request.method == 'GET':
        return render_template('login.html', form=form)


@auth.route('/logout')
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
        if check_password_hash(password, inserted_password):
            unregister_user = User.query.filter_by(email=current_user.get_email()).first()
            unregister_user.is_active = False
            db.session.commit()
            # unregistered user gets redirected to main page as anonymous
            logout_user()
            return redirect('/')
        # try again (password does not match)
        else:
            return {'msg': 'Password does not match, try again'}, 400
