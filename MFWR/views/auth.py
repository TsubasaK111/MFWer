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

# Debugging Dependencies
import pdb, pprint, inspect


@app.route('/login/')
def login():
    """ login page.
        * generates a random "state" string and
        * pushes state when authorizing with OAuth (google_connect)."""
    def random_string():
        return ( random.choice(string.ascii_uppercase + string.digits)
            for x in xrange(32) )
    print random_string()
    state = ''.join(random_string())
    flask_session['state'] = state
    return render_template( 'login.html',
                              state = flask_session['state'] )


def logInRedirect():
    """redirect routes to the login page."""
    thisFunction = inspect.stack()[1][3]
    flash("It appears you're not logged in. Log in to access " + thisFunction + ".")
    return redirect('/login')


def createUser(flask_session):
    newUser = User( name = flask_session['username'],
                    picture = flask_session['picture'],
                    link = flask_session['link'],
                    email = flask_session['email'],
                    google_plus_id = flask_session['google_plus_id'] )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(google_plus_id = flask_session['google_plus_id']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def getUserId(email, google_plus_id):
    try:
        user_id = getUserIdFromEmail(email)
    except:
        try:    user_id = getUserIdFromGooglePlusID(google_plus_id)
        except: user_id = None
    return user_id


def getUserIdFromEmail(email):
    user = session.query(User).filter_by(email = email).one()
    return user.id


def getUserIdFromGooglePlusID(google_plus_id):
    user= session.query(User).filter_by(google_plus_id = google_plus_id).one()
    return user.id
