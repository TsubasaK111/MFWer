# Webserver Dependencies
from flask import (Flask, render_template, request, redirect, url_for, flash,
                  jsonify, send_from_directory)
from MFWR import app

# Database Dependencies
from MFWR.models import session, Category, MFW, Element

from MFWR.forms import * # WTForm Dependencies
from auth import *       # Auth Dependencies
from upload import *     # Image Upload Dependencies

# Debugging Dependencies
import pdb
from sqlalchemy import inspect


@app.route('/')
def landing():
    """landing page for everybody!"""
    return render_template( 'landing.html' )


@app.route('/mfw/browse/')
def mfw_browse():
    """tile styled page to display and browse MFWs"""
    mfws = session.query(MFW).all()
    return render_template( 'mfw_browse.html', mfws=mfws )


@app.route('/mfw/<int:mfw_id>/view/')
def mfw_view(mfw_id):
    """view the full details of a MFW"""
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    return render_template( 'mfw_view.html', mfw=mfw, elements=mfw.elements )


@app.route('/mfw/create/', methods=['GET', 'POST'])
@app.route('/mfw/create/<category_name>', methods=['GET', 'POST'])
def mfw_create(category_name=""):
    """page to create a new Mental Framework."""
    #guard clauses:
    if 'access_token' not in flask_session:
        return logInRedirect()
    user_id = getUserId( flask_session['email'],
                         flask_session['google_plus_id'] )
    #form initialization
    mfwForm = MFWForm(request.form)

    if request.method == "POST": #and mfwForm.validate():
        mfw = MFW()
        mfwForm.populate_obj(mfw)
        mfw.creator_id = user_id
        duplicate_mfw = session.query(MFW).\
                                filter_by(name = mfw.name).\
                                first()
        if duplicate_mfw:
            flash("The name "+mfw.name+" already exists.")
            return redirect(url_for("mfw_create", form=mfwForm))
        try:
            uploaded_image = upload_image(request.files['image_file'])
        except:
            uploaded_image = False
        if uploaded_image: mfw.image_url = uploaded_image

        mfw = parse_categories(mfw, request.form['category'])
        session.add( mfw )
        session.commit()

        # add elements to mfw object from numbered element form fields
        i = 0
        while i < 20:
            try:
                element = Element(
                    letter = request.form['element'+str(i)+'-letter'],
                    description = request.form['element'+str(i)+'-description'],
                    order =       i,
                    mfw_id = mfw.id
                    )
                session.add(element)
                i = i + 1
            except:
                break
        session.commit()
        flash( "new MFW '" + mfw.name + "' created!" )
        print "\nmfw POST triggered, name is: ", mfw.name
        return redirect(url_for("mfw_browse"))

    else:
        return render_template( 'mfw_create.html',
                                mfwForm = mfwForm,
                                category_name = category_name )


@app.route('/mfw/<int:mfw_id>/edit/', methods=['GET', 'POST'])
def mfw_edit(mfw_id):
    """page to edit a MFW. (authorized only for creators)"""
    # guard clauses:
    if 'access_token' not in flask_session:
        return logInRedirect()
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not mfw.creator_id == user_id:
        return redirect(url_for("mfw_view", mfw_id = mfw_id))
        flash("Only the creator of a MFW can edit items.")

    # form initialization
    mfwForm = MFWForm( request.form, mfw )
    elementForms = []
    for element in mfw.elements:
        elementForm = ElementForm( None , element )
        elementForms.append(elementForm)

    if request.method == "POST":
        print "\nmfw_edit POST triggered, name is: ", mfwForm.name.data
        old_name = mfw.name
        mfwForm.populate_obj(mfw)

        # populate elements of the mfw object from numbered element form fields
        i = 0
        while i < 20:
            try:
                elementForm = ElementForm(
                    id = int(request.form['element'+str(i)+'-id']),
                    letter = request.form['element'+str(i)+'-letter'],
                    description = request.form['element'+str(i)+'-description'],
                    order =       i
                    )
                elementForm.populate_obj(mfw.elements[i])
                i = i + 1
            except:
                break

        try:
            edited_image_file = upload_image(request.files['edited_image_file'])
        except:
            edited_image_file = False
        if edited_image_file: mfw.image_url = edited_image_file

        mfw = parse_categories(mfw, request.form['edited_categories'])

        session.add(mfw)
        session.commit()
        flash( "item '" +  old_name + "' edited to '" + mfw.name + "'. Jawohl!")
        return redirect( url_for("mfw_view", mfw_id=mfw_id) )

    else:
        # prep 'categories' field and serve page
        category_names = ""
        for category in mfw.categories:
            if category_names == "": category_names = category.name
            category_names = category_names + ", " + category.name
        return render_template( 'mfw_edit.html',
                                mfwForm = mfwForm,
                                elementForms = elementForms,
                                category_names = category_names )


@app.route('/mfw/<int:mfw_id>/delete/', methods = ['GET', 'POST'])
def mfw_delete(mfw_id):
    """page to delete a MFW (authorized only for creators)."""
    # guard clauses:
    if 'access_token' not in flask_session:
        return logInRedirect()
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not mfw.creator_id == user_id:
        flash("Only MFW owners can delete MFWs.")
        return redirect(url_for("mfw_view", mfw_id = mfw_id))

    if request.method == "POST":
        print "\nmfw_delete POST triggered!"
        session.delete(mfw)
        session.commit()
        flash( "item '" + mfw.name + "' deleted. Auf Wiedersehen!")
        return redirect(url_for("mfw_browse"))

    else:
        print "/id/delete accessed..."
        return render_template( "mfw_delete.html", mfw = mfw )


def parse_categories(mfw, category_names):
    """ * parse 'categories' form field by proper splitting and stripping.
        * checks if each category already exists.
        * if it doesn not exist, create new category in session.
        * append category to mfw. """

    user_id = getUserId( flask_session['email'],
                         flask_session['google_plus_id'] )

    category_names = str(category_names).split(",")
    for category_name in category_names:
        category_name = category_name.strip()
        if not ((category_name == None) or (category_name == "")):
            existing_category = session.query(Category).\
                                    filter_by(name = category_name).\
                                    first()
            try:
                if existing_category:
                    mfw.categories.append(existing_category)
                else:
                    new_category = Category( name=category_name,
                                         creator_id=user_id )
                    mfw.categories.append(new_category)
            except:
                mfw.categories.append(existing_category)
    return mfw
