# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from leRestaurant import app

# Database Dependencies
from leRestaurant.models import session, User, Restaurant, MenuItem

# Authentication Dependencies
from flask import session as flask_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from auth import *

# Debugging Dependencies
import pdb, pprint, inspect



@app.route('/facebook_connect', methods=['POST'])
def facebook_connect():
    """ responds to /login/'s login attempt with OAuth (facebook connect).
        * checks if 'state' is concurrent.
        * kicks you out if not concurrent.
        * attempts to upgrade/exchange 'authorization code'(aka secrets) with credentials object, which has access token. """

    if request.args.get('state') != flask_session['state']:
        response = make_response(json.dumps('Invalid state detected!'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    print "access token received %s " % access_token

    # Open json file containing secrets obtained from Facebook and
    # store the client ID (aka app ID) inside. CLIENT_ID and other secrets generated at:
    # https://developers.facebook.com/apps/523665454488045/settings/
    app_id = json.loads(
                open("leRestaurant/client_secrets_facebook.json", "r").read()
                )["web"]["client_id"]
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    flask_session['provider'] = 'facebook'
    flask_session['username'] = data["name"]
    flask_session['email'] = data["email"]
    flask_session['facebook_id'] = data["id"]

    # The token must be stored in the flask_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    flask_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    flask_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(flask_session['email'])
    if not user_id:
        user_id = createUser(flask_session)
    flask_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += flask_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += flask_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % flask_session['username'])
    return output


@app.route('/facebook_disconnect')
def facebook_disconnect():
    facebook_id = flask_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = flask_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"
