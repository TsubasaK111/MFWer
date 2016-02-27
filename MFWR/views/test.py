# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from MFWR import app

# Database Dependencies
from MFWR.models import session, User, MFW, element

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


@app.route('/login_sample')
def login_sample():
    """ gconnect & facebook oauth test."""
    return render_template( 'login.sample.html' )
