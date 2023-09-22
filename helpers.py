import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import requests
import json
import time
import random
import os

from flask import redirect, render_template, session
from functools import wraps

API_KEY = 'RGAPI-0bd95d20-6ad3-46bd-9548-1bf6bdb4946a'
MATCH_SIZE = 213


def get_match(puuid):
    get_match_url = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/'
    match_detail_url = 'https://asia.api.riotgames.com/lol/match/v5/matches/'

    # get match id from puuid
    idx = random.randint(1, 100)
    match_url = "{}{}/ids?start={}&count=1&api_key={}".format(get_match_url, puuid, idx, API_KEY)
    info = requests.get(match_url)
    match = info.json()[0]

    # get match detail from match id
    match_url = "{}{}?api_key={}".format(match_detail_url, match, API_KEY)
    info = requests.get(match_url)
    match_detail = info.json()
    if info.status_code != 200:
        #handle rate limit: get local matches.json
        idx = random.randint(1, MATCH_SIZE)
        with open(os.path.join('matches', "match{}.json".format(idx)), "r") as file:
            data = json.load(file)
            return data
    if match_detail['info']['queueId'] == 420:
        return match_detail
    else:
        get_match(puuid)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
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



def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
