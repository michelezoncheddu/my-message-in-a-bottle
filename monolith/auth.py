import functools

from flask_login import LoginManager, current_user

from monolith.database import User

login_manager = LoginManager()

def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        # Checks if the user is an admin
        if not current_user.is_admin:  # TODO: compare with hasattr(id)
            return login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required


def login_required(func):
    @functools.wraps(func)
    def _login_required(*args, **kw):
        # Checks if the user is logged in.
        if not current_user.is_authenticated:  # TODO: compare with hasattr(id)
            return login_manager.unauthorized()
        return func(*args, **kw)
    return _login_required


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True # NOT COVERED
    return user
