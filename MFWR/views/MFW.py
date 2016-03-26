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
def mfw_browse():
    """tile styled page to display and browse MFWs"""
    mfws = session.query(MFW).all()
    return render_template( 'mfw_browse.html', mfws=mfws )


@app.route('/<int:mfw_id>/view/')
def mfw_view(mfw_id):
    """view the full details of a MFW"""
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    elements = session.query(Element).filter_by(mfw_id=mfw_id).order_by(Element.order).all()
    return render_template( 'mfw_view.html',
                            mfw=mfw,
                            elements=elements )


@app.route('/create/', methods=['GET', 'POST'])
@app.route('/create/<category_name>', methods=['GET', 'POST'])
def mfw_create(category_name=""):
    """page to create a new Mental Framework."""
    form = MFWForm(request.form)
    # if request.method == "POST" and form.validate():
    if request.method == "POST":
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId( flask_session['email'],
                             flask_session['google_plus_id'] )
        mfw_name        = request.form['mfw_name']
        mfw_description = request.form['mfw_description']
        image_url       = request.form['image_url']
        reference_url   = request.form['reference_url']
        new_mfw = MFW( name = mfw_name,
                       description = mfw_description,
                       creator_id = user_id,
                       image_url = image_url,
                       reference_url = reference_url )
        # store image to configured location and return url.
        # if no file, keep user input image_url.
        uploaded_image = upload_image(request.files['image_file'])
        if uploaded_image:
            new_mfw.image_url = uploaded_image

        category_name = request.form['category']
        category = Category( name = category_name,
                             creator_id = user_id )
        new_mfw.categories.append(category)

        session.add( new_mfw )
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
                               mfw_id=new_mfw.id )
            session.add(element)
        session.commit()
        flash( "new MFW '" + mfw_name + "' created!" )
        print "\nnew_mfw POST triggered, name is: ", mfw_name
        return redirect(url_for("mfw_browse"))

    else:
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId(
                      flask_session['email'],flask_session['google_plus_id'] )
        if not ((category_name == None) or (category_name == "")):
            return render_template( 'mfw_create.html',
                                    category_name = category_name )
        return render_template('mfw_create.html')


@app.route('/<int:mfw_id>/edit/', methods=['GET', 'POST'])
def mfw_edit(mfw_id):
    """page to edit a MFW. (authorized only for creators)"""

    if 'access_token' not in flask_session:
        return logInRedirect()
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    elements = session.query(Element).filter_by(mfw_id=mfw_id).order_by(Element.order).all()
    categories = mfw.categories
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not mfw.creator_id == user_id:
        return redirect(url_for("mfw_view", mfw_id = mfw_id))
        flash("Only the creator of a MFW can edit items.")

    if request.method == "POST":
        edited_name = request.form['edited_name']
        edited_description = request.form['edited_description']
        print "\nmfw_edit POST triggered, name is: ", edited_name

        old_name = session.query(MFW).filter_by(id = mfw_id).first().name
        pdb.set_trace()
        result = session.execute(""" UPDATE mfw
                                     SET name=:edited_name,
                                         description=:edited_description
                                     WHERE id=:mfw_id; """,
                                 { "edited_name": edited_name,
                                   "edited_description": edited_description,
                                   "mfw_id": mfw_id }
                                 )
        session.commit()
        flash( "item '" +  old_name + "' edited to '" + edited_name + "'. Jawohl!")
        return redirect( url_for("mfw_view", mfw_id=mfw_id) )

    else:
        return render_template( 'mfw_edit.html',
                                mfw = mfw,
                                elements = elements )


@app.route('/<int:mfw_id>/delete/', methods = ['GET', 'POST'])
def mfw_delete(mfw_id):
    """page to delete a MFW (authorized only for creators)."""

    if 'access_token' not in flask_session:
        return logInRedirect()

    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])

    if not mfw.creator_id == user_id:
        flash("Only MFW owners can delete MFWs.")
        return redirect(url_for("mfw_view", mfw_id = mfw_id))

    if request.method == "POST":
        print "\nmfw_delete POST triggered!"
        deleted_mfw = session.query(MFW).filter_by(id = mfw_id).first()
        session.delete(deleted_mfw)
        session.commit()
        flash( "item '" + deleted_mfw.name + "' deleted. Auf Wiedersehen!")
        return redirect(url_for("mfw_browse"))

    else:
        print "/id/delete accessed..."
        return render_template( "mfw_delete.html",
                                mfw = mfw )
