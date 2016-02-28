# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

from MFWR import app

# Database Dependencies
from MFWR.models import session, MFW, element

# Auth Dependencies
from auth import *

# Debugging Dependencies
import pdb, pprint, inspect


@app.route('/')
@app.route('/landing')
def landing():
    """landing page for errbody!"""
    return render_template( 'landing.html' )

@app.route('/browse/')
def MFW_browse():
    """tile styled page to display and browse MFWs"""
    MFWs = session.query(MFW).all()
    return render_template( 'MFW_browse.html', MFWs=MFWs )


@app.route('/<int:MFW_id>/view/')
def MFW_view(MFW_id):
    """view the full details of a MFW"""
    thisMFW = session.query(MFW).filter_by(id = MFW_id).first()

    return render_template( 'MFW_view.html', MFW=thisMFW )


@app.route('/new/', methods=['GET', 'POST'])
def MFW_new():
    """page to create a new Mental Framework."""

    if request.method == "POST":
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])

        new_name = request.form['new_name']
        print "\nMFW_new POST triggered, name is: ", new_name
        MFW_new = MFW( name=new_name, creator_id = user_id )
        session.add(MFW_new)
        session.commit()
        flash( "new MFW '" + new_name + "' created!")
        print "POST worked!"

        return redirect(url_for("MFW_browse"))

    else:
        return render_template('MFW_new.html')


@app.route('/<int:MFW_id>/edit/', methods=['GET', 'POST'])
def MFW_edit(MFW_id):
    """page to edit a MFW. (authorized only for creators)"""

    if 'access_token' not in flask_session:
        return logInRedirect()
    thisMFW = session.query(MFW).filter_by(id = MFW_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not thisMFW.creator_id == user_id:
        return redirect(url_for("MFW_view", MFW_id = MFW_id))
        flash("Only the creator of a MFW can edit items.")

    if request.method == "POST":
        edited_name = request.form['edited_name']
        print "\nMFW_edit POST triggered, name is: ", edited_name
        old_name = session.query(MFW).filter_by(id = MFW_id).first().name

        result = session.execute(""" UPDATE MFW
                                     SET name=:edited_name
                                     WHERE id=:MFW_id; """,
                                 { "edited_name": edited_name,
                                   "MFW_id": menu_id }
                                 )
        session.commit()
        flash( "item '" +  old_name + "' edited to '" + edited_name + "'. Jawohl!")
        return redirect( url_for("showMenu", MFW_id=MFW_id) )

    else:
        elements = session.query(element).filter_by(id = MFW_id).all()
        return render_template( 'MFW_edit.html',
                                MFW = MFW,
                                elements = elements )


@app.route('/<int:MFW_id>/delete/', methods = ['GET', 'POST'])
def MFW_delete(MFW_id):
    """page to delete a MFW (authorized only for creators)."""

    if 'access_token' not in flask_session:
        return logInRedirect()

    thisMFW = session.query(MFW).filter_by(id = MFW_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])

    if not thisMFW.creator_id == user_id:
        flash("Only MFW owners can delete MFWs.")
        return redirect(url_for("MFW_view",MFW_id = MFW_id))

    if request.method == "POST":
        print "\nMFW_delete POST triggered!"
        deletedMFW = session.query(MFW).filter_by(id = MFW_id).first()
        session.delete(deletedMFW)
        session.commit()
        flash( "item '" + deletedMFW.name + "' deleted. Auf Wiedersehen!")
        return redirect(url_for("MFW_browse"))

    else:
        print "/id/delete accessed..."
        return render_template( "MFW_delete.html",
                                MFW = thisMFW )
