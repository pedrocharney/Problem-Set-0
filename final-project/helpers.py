import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from datetime import datetime

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def timeconvert(time, date):
    time_format = "%H:%M"
    date_format = "%Y-%m-%d"
    # Parse the time string into a time object
    time_obj = datetime.strptime(time, time_format).time()
    # Combine the date and time to form a complete datetime object
    date_obj = datetime.strptime(date, date_format)
    datetime_obj = datetime.combine(date_obj, time_obj)
    # Get the Unix timestamp (in seconds) from the datetime object
    unix_timestamp = datetime_obj.timestamp()
    # Convert to integer (if needed)
    return int(unix_timestamp)


def dateconvert(date):
    date_format = "%Y-%m-%d"
    # Convert the date string to a datetime object
    date_obj = datetime.strptime(date, date_format)
    # Get the Unix timestamp (in seconds) from the datetime object
    unix_timestamp = date_obj.timestamp()
    # Convert to integer (if needed)
    return int(unix_timestamp)


def dayoftheweek(date):
    # Create a datetime object from the date string
    date_obj = datetime.strptime(date, "%Y-%m-%d")

    # Get the day of the week (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
    day_of_week = date_obj.weekday()

    # Convert the numeric representation of the day to its name
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_name = days[day_of_week]
    return day_name


def validateTime(time):
    hour = int(str(time[0]) + str(time[1]))
    minute = int(str(time[3]) + str(time[4]))
    if hour <= 24 and hour >= 0 and minute <= 59 and minute >= 0:
        return True
    else:
        return False


def weekNumberToString(weeknum, type_):
    type2 = type_.upper()
    if type2 == "SQL":
        weekdays = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
    if type2 == "PYTHON":
        weekdays = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

    return weekdays[weeknum]
