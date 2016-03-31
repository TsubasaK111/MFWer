# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from MFWR import app

# Database Dependencies
from MFWR.models import session, User

# Authentication Dependencies
from flask import session as flask_session
import random, string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from auth_google_connect import *

# Debugging Dependencies
import pdb, pprint, inspect


@app.route('/login/')
def login():
    """ login page.
        * generates a random "state" string and
        * pushes state when authorizing with OAuth (google_connect)."""
    flask_session['state'] = newState()
    return render_template( 'login.html',
                            state = flask_session['state'] )


def newState():
    def random_string():
        return ( random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32) )
    return "".join(random_string())


@app.route('/logout/')
def logout():
    """ logout page.
        * Refreshes 'state'
        * Calls each OAuth Provider's *_disconnect route."""
    response = google_disconnect()
    # parse response packet and display message if 400 err
    if response.status_code == 400:
        jsonString = response.get_data()
        print jsonString
        flash(jsonString)
    if response.status_code == 200:
        print "User logged out"
        flash("You are now logged out. See you again! <3")
        # flask_session['state'] = newState()
    return redirect(url_for("landing"))


def logInRedirect():
    """redirect routes to the login page."""
    thisFunction = inspect.stack()[1][3]
    flash("It appears you're not logged in. Log in to access " + thisFunction + ".")
    return redirect('/login')

@app.route('/logbutton')
def logInOrOut():
    """"""
    if 'access_token' not in flask_session:
        return "Sign In"
    else:
        return "Sign Out"
