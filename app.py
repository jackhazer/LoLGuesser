import os
import random
import csv
import time

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required,  usd, get_match
from datetime import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# preopen the file
with open("puuid.csv", "r") as file:
    puuid_csv = list(csv.reader(file))

score = 0
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lolguesser.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """homepage"""
    return render_template("welcome.html")


@app.route("/play", methods=["GET", "POST"])
def play():
    global score
    """Playing the game"""
    if request.method == "POST":

        win = request.form.get('side')=='True'

        if win:
            score = score + 1
        else:
            if session.get('user_id'):
                current_time = datetime.now()
                date = current_time.strftime("%Y-%m-%d %H:%M:%S")
                db.execute(
                    "INSERT INTO history (person_id,score,date) VALUES(?,?,?)",
                    session["user_id"],
                    score,
                    date,
                )
            score = 0
    else:
        if score and session.get('user_id'):
            current_time = datetime.now()
            date = current_time.strftime("%Y-%m-%d %H:%M:%S")
            db.execute(
                "INSERT INTO history (person_id,score,date) VALUES(?,?,?)",
                session["user_id"],
                score,
                date,
            )
        score = 0

    match = {}
    while not match:
        puuid = random.choice(puuid_csv)
        match = get_match(puuid[0])
        time.sleep(0.2)
    win = 'blue' if match['info']["participants"][0]['win'] else 'red'

    return render_template("play.html",match = match, score = score ,win = win)

@app.route("/history")
@login_required
def history():
    """Show stats"""
    history = db.execute("SELECT * FROM history WHERE person_id=?", session["user_id"])
    return render_template("history.html", history=history)


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
        session['score'] = 0

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


@app.route("/help", methods=["GET"])
def help():
    """Show Instructions"""
    return render_template("help.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password:
            return apology("CANNOT LEAVE BLANK")
        for result in db.execute("SELECT username from users"):
            if username == result['username']:
                return apology("USERNAME ALREADY EXISTS")
        if password != confirmation:
            return apology("PASSWORDS DO NOT MATCH")

        password = generate_password_hash(password, method="pbkdf2", salt_length=16)
        db.execute(
            "INSERT INTO users (username,hash,cash) VALUES(?,?,?)",
            username,
            password,
            10000,
        )
        return redirect("/")
    else:
        return render_template("register.html")


