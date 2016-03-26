# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from MFWR import app

# Database Dependencies
from MFWR.models import session, User, MFW, Element

#A first attempt at an API endpoint (GET Req)
@app.route('/MFWs/<int:mfw_id>/JSON/')
def mfw_JSON(mfw_id):
    MFW = session.query(MFW).filter_by(id = mfw_id).one()
    elements = session.query(element).filter_by(mfw_id = mfw_id).all()
    return jsonify(elements = [element.serialize for element in elements])

#Another attempt at an API endpoint (GET Req)
@app.route('/MFWs/<int:mfw_id>/element/<int:menu_id>/JSON/')
def element_JSON(mfw_id, element_id):
    MFW = session.query(MFW).filter_by(id = mfw_id).one()
    element = session.query(element).filter_by(mfw_id = mfw_id).filter_by(id = menu_id).one()
    return jsonify(element = element.serialize)
