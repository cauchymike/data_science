from functools import wraps
from flask import g
from mathsclinicblog.errorpages.handlers import error_404


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return error_404
            return f(*args, **kwargs)
        return decorated_function
    return decorator