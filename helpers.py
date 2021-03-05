import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code):
    """Render message as an apology to user."""
    message2 = message.upper() + "!"
    return render_template("apology.html", top=code, bottom=message2), code


def unpunctuate(string):

    punctuations = '''!()-[]{};:'"\<>./?@#$%^&*_~'''

    for x in string.lower():
        if x in punctuations:
            string = string.replace(x, "")

    return string
