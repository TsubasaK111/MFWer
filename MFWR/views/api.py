# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from MFWR import app

# Database Dependencies
from MFWR.models import session, User, MFW, element

#A first attempt at an API endpoint (GET Req)
@app.route('/MFWs/<int:MFW_id>/JSON/')
def MFW_JSON(MFW_id):
    MFW = session.query(MFW).filter_by(id = MFW_id).one()
    elements = session.query(element).filter_by(MFW_id = MFW_id).all()
    return jsonify(elements = [element.serialize for element in elements])

#Another attempt at an API endpoint (GET Req)
@app.route('/MFWs/<int:MFW_id>/element/<int:menu_id>/JSON/')
def element_JSON(MFW_id, element_id):
    MFW = session.query(MFW).filter_by(id = MFW_id).one()
    element = session.query(element).filter_by(MFW_id = MFW_id).filter_by(id = menu_id).one()
    return jsonify(element = element.serialize)
