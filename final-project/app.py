import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    apology,
    login_required,
    timeconvert,
    dateconvert,
    dayoftheweek,
    validateTime,
    weekNumberToString,
)

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///volunteer.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    userId = session["user_id"]
    current_date = str(datetime.now().date())
    current_date_int = dateconvert(current_date)

    if request.method == "GET":
        # Retrive all the events that the user have already been enrolled

        enrolled_db = db.execute(
            "SELECT *, CAST(strftime('%w', DATETIME(date_int, 'unixepoch')) AS INTEGER) AS DayOfWeek FROM events WHERE date_int >= ? AND event_id IN (SELECT event_id FROM positions WHERE user_id = ? AND deleted = 0)",
            current_date_int,
            userId,
        )

        enrolled_events = []
        for event in enrolled_db:
            enrolled_events.append(
                {
                    "event_id": event["event_id"],
                    "name": event["name"],
                    "date": event["date_"],
                    "weekday": weekNumberToString(event["DayOfWeek"], "PYTHON"),
                    "start": event["start_"],
                    "end": event["end_"],
                    "userFunction": db.execute(
                        "SELECT type_ FROM users WHERE id = ?", userId
                    ),
                }
            )

        print(enrolled_events)

        # Retrive all events that are compatible with the user avaiable time

        # Retrive user avaiability information

        user_time_config_db = db.execute(
            "SELECT * FROM user_time_config WHERE user_id = ?", userId
        )

        # start_time = user_time_config_db[0]["start_int"]
        # end_time = user_time_config_db[0]["end_int"]

        weekdays = []
        for weekday in user_time_config_db:
            weekdays.append(weekday["weekday"])

        print(weekdays)

        compatible_events_db = db.execute(
            "SELECT *, CAST(strftime('%w', DATETIME(date_int, 'unixepoch')) AS INTEGER) AS DayOfWeek FROM events WHERE date_int >= ? AND date_int NOT IN (SELECT date_int FROM user_time_exception WHERE date_int >= ? AND user_id = ?) AND event_id NOT IN (SELECT event_id FROM positions WHERE user_id = ? AND deleted = 0) AND deleted = 0 AND DayOfWeek IN (?)",
            current_date_int,
            current_date_int,
            userId,
            userId,
            weekdays,
        )

        compatible_events = []
        for event in compatible_events_db:
            compatible_events.append(
                {
                    "event_id": event["event_id"],
                    "name": event["name"],
                    "date": event["date_"],
                    "weekday": weekNumberToString(event["DayOfWeek"], "PYTHON"),
                    "start": event["start_"],
                    "end": event["end_"],
                }
            )

    return render_template(
        "index.html", compatibleEvents=compatible_events, enrolledEvents=enrolled_events
    )


@app.route("/event", methods=["GET", "POST"])
@login_required
def event():
    # Check if the user have created a new event, and follows
    if request.method == "POST":
        # Retrive information about the fields
        name = request.form.get("cultname")
        date_ = request.form.get("date")
        date_int = dateconvert(date_)
        start = request.form.get("time_start")
        start_int = timeconvert(start, date_)
        end = request.form.get("time_end")
        end_int = timeconvert(end, date_)

        # Validate if all fields have been fulfilled
        if not name or not date_ or not start or not end:
            return apology("must provide all the information", 400)

        # Validate if the input fields make sense
        if validateTime(start) == False or validateTime(end) == False:
            return apology("must provide a valid start & end time", 400)

        # Save event to data base
        db.execute(
            "INSERT INTO events (name, date_int, date_, start_int, start_, end_int, end_) VALUES (?, ?, ?, ?, ?, ?, ?);",
            name,
            date_int,
            date_,
            start_int,
            start,
            end_int,
            end,
        )

        flash("Successfully Created")
        return redirect("event")

    current_date = str(datetime.now().date())
    current_date_int = dateconvert(current_date)

    events_db = db.execute(
        "SELECT event_id, name, date_, start_, end_ FROM events WHERE date_int >= ? AND deleted = 0 ORDER BY date_int DESC",
        current_date_int,
    )

    events = []

    for event in events_db:
        events.append(
            {
                "event_id": event["event_id"],
                "name": event["name"].title(),
                "date": event["date_"],
                "start": event["start_"],
                "end": event["end_"],
                "weekday": dayoftheweek(event["date_"]),
                "volunteer": db.execute(
                    "SELECT count(user_id) as count FROM positions WHERE event_id = ? AND deleted = 0",
                    event["event_id"],
                ),
            }
        )

    return render_template("event.html", events=events)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/deleteEvent", methods=["POST"])
@login_required
def deleteEvent():
    event_id = int(request.form.get("event_id"))
    db.execute("UPDATE events SET deleted=? WHERE event_id=?", 1, event_id)

    flash("Successfully Deleted")
    return redirect("event")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("email").rstrip()
        name = request.form.get("name").rstrip()
        password = request.form.get("password")
        password_ = request.form.get("password_")

        # Check if username or user password is empty
        if not username or not password or not password_ or not name:
            return apology("must provide all the information", 400)

        # Check if the value of the two password fields are the same
        if password != password_:
            return apology("both passwords fields need to match", 400)

        # Check if username already exists
        checkname = db.execute("SELECT * FROM users WHERE username=?", username)
        if len(checkname) > 0:
            return apology("user name already exists", 400)

        # Hash the user password
        hashPassword = generate_password_hash(password, method="pbkdf2", salt_length=16)

        # Save new user to the data base
        db.execute(
            "INSERT INTO users (username, hash, name) VALUES (?, ?, ?);",
            username,
            hashPassword,
            name,
        )

        flash("Successfully Registered")
        return redirect("/")

    return render_template("register.html")


@app.route("/timeconfig", methods=["GET", "POST"])
@login_required
def timeconfig():
    userId = session["user_id"]

    if request.method == "POST":
        current_datetime = datetime.now()
        # date_ = current_datetime.strftime('%Y-%m-%d')
        # start = request.form.get("time_start")
        # start_int = timeconvert(start, date_)
        # end = request.form.get("time_end")
        # end_int = timeconvert(end, date_)

        weekdays = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        days = []
        c = 0
        for weekday in weekdays:
            if request.form.get(weekday) == "on":
                days.append(c)
            c += 1

        # Clear the previus config of the data base
        db.execute("DELETE FROM user_time_config WHERE user_id = ?;", userId)

        start_int = 1698548460
        start_ = "00:01"
        end_int = 1698634740
        end_ = "23:59"

        # Save event to data base
        for day in days:
            db.execute(
                "INSERT INTO user_time_config (user_id, weekday, start_int, start_, end_int, end_) VALUES (?, ?, ?, ?, ?, ?);",
                userId,
                day,
                start_int,
                start_,
                end_int,
                end_,
            )

        flash("Successfully Updated")
        return redirect("timeconfig")

    # Retrieve user information
    users_db = db.execute("SELECT * FROM users WHERE id = ?", userId)

    if int(users_db[0]["active"]) == 1:
        status_ = "Active"
    else:
        status_ = "inactive"

    users = []
    for person in users_db:
        users.append(
            {
                "user_id": person["id"],
                "name": person["name"],
                "email": person["username"],
                "function": person["type_"],
                "status": status_,
            }
        )

    # Retrive time information
    user_time_config_db = db.execute(
        "SELECT * FROM user_time_config WHERE user_id = ?", userId
    )
    print(user_time_config_db)

    if not user_time_config_db:
        user_time_config_db = [
            {
                "user_id": userId,
                "weekday": 7,
                "start_int": 0,
                "start_": "00:00",
                "end_int": 0,
                "end_": "00:00",
            }
        ]

    time_info = []
    week_info = []
    time_info.append(
        {
            "start": user_time_config_db[0]["start_"],
            "end": user_time_config_db[0]["end_"],
        }
    )

    for weeks in user_time_config_db:
        week_info.append(weeks["weekday"])

    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    weekdata = []

    i = 0
    for weekday in weekdays:
        if i in week_info:
            weekdata.append({"status": True, "weekname": weekday, "weekindex": i})
        else:
            weekdata.append({"status": False, "weekname": weekday, "weekindex": i})
        i += 1

    # Retrive date exception info

    current_date = str(datetime.now().date())
    current_date_int = dateconvert(current_date)

    exception_db = db.execute(
        "SELECT * FROM user_time_exception WHERE user_id = ? AND date_int >= ? ORDER BY date_int DESC",
        userId,
        current_date_int,
    )

    print(time_info[0])
    print(weekdata)

    return render_template(
        "timeconfig.html",
        user=users[0],
        time_info=time_info[0],
        weekdata=weekdata,
        exceptions=exception_db,
    )


@app.route("/exception", methods=["POST"])
@login_required
def exception():
    userId = session["user_id"]
    date_ = request.form.get("exception_date")
    date_int = dateconvert(date_)
    reason = request.form.get("reason").rstrip()

    db.execute(
        "INSERT INTO user_time_exception (user_id, date_int, date_, reason) VALUES (?, ?, ?, ?);",
        userId,
        date_int,
        date_,
        reason,
    )

    flash("Successfully Included")
    return redirect("timeconfig")


@app.route("/deleteException", methods=["POST"])
def deleteException():
    userId = session["user_id"]
    exception = int(request.form.get("exception_id"))

    db.execute(
        "DELETE FROM user_time_exception WHERE user_id = ? AND exception_id = ?;",
        userId,
        exception,
    )

    flash("Successfully Removed")
    return redirect("timeconfig")


@app.route("/eventdetail", methods=["GET"])
@login_required
def eventdetail():
    eventId = request.args.get("event")

    if not eventId:
        return apology("must provide a valid event id", 400)

    # Load basic event info
    event_db = db.execute(
        "SELECT *, CAST(strftime('%w', DATETIME(date_int, 'unixepoch')) AS INTEGER) AS DayOfWeek_int FROM events WHERE event_id = ?",
        eventId,
    )
    event_db[0].update(
        {"weekday": weekNumberToString(event_db[0]["DayOfWeek_int"], "PYTHON")}
    )

    # Load the inscribed users of the event
    volunteers_db = db.execute(
        "SELECT p.event_id, p.user_id, p.role, p.deleted, u.name, u.username FROM positions as p LEFT JOIN users as u ON p.user_id = u.id WHERE event_id = ?",
        eventId,
    )
    eventcount_db = db.execute(
        "SELECT count(event_id) as count FROM positions WHERE event_id = ?", eventId
    )

    return render_template(
        "eventdetail.html",
        event=event_db[0],
        volunteers=volunteers_db,
        eventCount=eventcount_db[0],
    )


@app.route("/subcribeEvent", methods=["GET", "POST"])
def subcribeEvent():
    userId = session["user_id"]
    eventId = int(request.form.get("subscription"))
    userRole = db.execute("SELECT type_ FROM users WHERE id = ?", userId)

    # Check if the user already have voluntaried to the same event
    checkv = db.execute(
        "SELECT event_id, deleted FROM positions WHERE user_id = ? AND event_id = ?",
        userId,
        eventId,
    )

    if len(checkv) != 0 and checkv[0]["deleted"] == 0:
        flash("You already have been subscribed to this event")
    if len(checkv) != 0 and checkv[0]["deleted"] == 1:
        db.execute(
            "UPDATE positions SET deleted = 0 WHERE user_id = ? AND event_id = ?",
            userId,
            eventId,
        )
        flash("Successfully Included")
    if len(checkv) == 0:
        db.execute(
            "INSERT INTO positions (event_id, user_id, role) VALUES (?, ?, ?);",
            eventId,
            userId,
            userRole[0]["type_"],
        )
        flash("Successfully Included")

    return redirect("eventdetail?event=" + str(eventId))


@app.route("/unsubcribeevent", methods=["GET", "POST"])
def unSubcribeEvent():
    userId = session["user_id"]
    eventId = int(request.form.get("confirmCancel"))

    db.execute(
        "UPDATE positions SET deleted=1 WHERE event_id = ? AND user_id = ?",
        eventId,
        userId,
    )

    flash("Successfully Removed")
    return redirect("/")
