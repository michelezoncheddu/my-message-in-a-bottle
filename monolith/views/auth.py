from flask import Blueprint, redirect, render_template, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from monolith.auth import login_required
from monolith.database import User, db
from monolith.forms import LoginForm


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    '''Manage the login of a user

       GET:  Returns the login page form
       POST: Takes the input from the form, if the login is correct invokes the login_user()
             function that inizialize the user session and redirect to the index page,
             shows an error o.w.
    '''
    form = LoginForm()
    if request.method == 'POST':
        result = form.validate_on_submit()
        # if ok user logged in
        if result[0]:
            email= form.data['email']
            user = db.session.query(User).filter(User.email==email, User.is_active).first()
            login_user(user)
            return redirect('/')
        # shows an error o.w.
        error = result[1]
        return render_template('login.html', form=form, error=error), 409
    # GET
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    '''Manage the logout of the logged in user.'''
    logout_user()
    return redirect('/')


@auth.route('/unregister', methods=['GET', 'POST'])
@login_required
def unregister():
    '''Manage the unregistration

    GET:  Returns the unregister page form where the account password is asked.
    POST: Takes the input from the form, if the password is correct unregister user,
          shows an error page o.w.
    '''
    if request.method == 'GET':
        return render_template('unregister.html')

    # POST
    password = current_user.get_password_hash()
    inserted_password = request.form['password']
    if check_password_hash(password, inserted_password):
        # unregistration confirmed
        unregister_user = User.query.filter_by(email=current_user.get_email()).first()
        unregister_user.is_active = False
        db.session.commit()
        # unregistered user gets redirected to main page as anonymous
        logout_user()
        return redirect('/')
    # try again (password does not match)
    error = 'Password does not match, try again'
    return render_template('/error.html', error=error), 400
