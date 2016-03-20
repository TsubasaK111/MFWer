# Webserver Dependencies
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory

from MFWR import app

# Database Dependencies
from MFWR.models import session, Category, MFW, Element

# WTForm Dependencies
from MFWR.forms import *

# Auth Dependencies
from auth import *

# Image Upload Dependencies
from upload import *

# Debugging Dependencies
import pdb, inspect


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
    theseElements = session.query(Element).filter_by(MFW_id=MFW_id).order_by(Element.order).all()
    return render_template( 'MFW_view.html',
                            MFW=thisMFW,
                            elements=theseElements )


@app.route('/create/', methods=['GET', 'POST'])
def MFW_create():
    """page to create a new Mental Framework."""
    form = MFWForm(request.form)
    # if request.method == "POST" and form.validate():
    if request.method == "POST":
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId(
                      flask_session['email'],flask_session['google_plus_id'] )
        MFW_name = request.form['MFW_name']
        MFW_description = request.form['MFW_description']
        image_url = request.form['image_url']
        reference_url = request.form['reference_url']
        new_MFW = MFW( name = MFW_name,
                       description = MFW_description,
                       creator_id = user_id,
                       image_url = image_url,
                       reference_url = reference_url )
        # store image to configured location and return url.
        # if no file, keep user input image_url.
        uploaded_image = upload_image(request.files['image_file'])
        if uploaded_image:
            new_MFW.image_url = uploaded_image
        session.add( new_MFW )
        session.commit()

        new_elements = []
        i = 0
        while i < 20:
            try:
                new_elements.append(
                  { 'letter':      request.form['element'+str(i)+'-letter'],
                    'description': request.form['element'+str(i)+'-description'],
                    'order':       i
                  })
                i = i + 1
            except:
                break

        for new_element in new_elements:
            element = Element( letter=new_element['letter'],
                               description=new_element['description'],
                               order=new_element['order'],
                               MFW_id=new_MFW.id )
            session.add(element)
        session.commit()
        flash( "new MFW '" + MFW_name + "' created!" )
        print "\nnew_MFW POST triggered, name is: ", MFW_name
        return redirect(url_for("MFW_browse"))

    else:
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId(
                      flask_session['email'],flask_session['google_plus_id'] )
        return render_template('MFW_create.html')


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
        edited_description = request.form['edited_description']
        print "\nMFW_edit POST triggered, name is: ", edited_name

        old_name = session.query(MFW).filter_by(id = MFW_id).first().name

        result = session.execute(""" UPDATE MFW
                                     SET name=:edited_name
                                         description=:edited_description
                                     WHERE id=:MFW_id; """,
                                 { "edited_name": edited_name,
                                   "edited_description": edited_description,
                                   "MFW_id": MFW_id }
                                 )
        session.commit()
        flash( "item '" +  old_name + "' edited to '" + edited_name + "'. Jawohl!")
        return redirect( url_for("MFW_view", MFW_id=MFW_id) )

    else:
        elements = session.query(Element).filter_by(id = MFW_id).all()
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
        return redirect(url_for("MFW_view", MFW_id = MFW_id))

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
