from functools import wraps
from flask import session, redirect, jsonify


def team_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if session.get("role") != "team":
            return redirect("/team/login.html")

        return function(*args, **kwargs)

    return wrapper


def admin_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if session.get("role") != "admin":
            return redirect("/admin/login.html")

        return function(*args, **kwargs)

    return wrapper
