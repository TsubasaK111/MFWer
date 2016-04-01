# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from MFWR import app

# Database Dependencies
from MFWR.models import session, User, MFW, Element, Category

#A first attempt at an API endpoint (GET Req)
@app.route('/mfw/<int:mfw_id>/json/')
def mfw_json(mfw_id):
    mfw = session.query(MFW).filter_by(id = mfw_id).one()
    elements = mfw.elements
    return jsonify(mfw = mfw.serialize, elements = [element.serialize for element in elements])

#Another attempt at an API endpoint (GET Req)
@app.route('/category/<int:category_id>/json/')
def category_json(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    mfws = category.mfws
    return jsonify(category = category.serialize, mfws = [mfw.serialize for mfw in category.mfws])
