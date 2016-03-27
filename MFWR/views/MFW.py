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
    elements = session.query(Element).\
                       filter_by(mfw_id=mfw_id).\
                       order_by(Element.order).\
                       all()
    return render_template( 'mfw_view.html', mfw=mfw,
                                             elements=elements )


@app.route('/create/', methods=['GET', 'POST'])
@app.route('/create/<category_names>', methods=['GET', 'POST'])
def mfw_create(category_names=""):
    """page to create a new Mental Framework."""
    form = MFWForm(request.form)
    if 'access_token' not in flask_session:
        return logInRedirect()
    user_id = getUserId( flask_session['email'],
                         flask_session['google_plus_id'] )
    if request.method == "POST": #and form.validate():
        new_mfw = MFW()
        form.populate_obj(new_mfw)
        new_mfw.creator_id = user_id
        duplicate_mfw = session.query(MFW).\
                                filter_by(name = new_mfw.name).\
                                first()
        if duplicate_mfw:
            flash("The name "+new_mfw.name+" already exists.")
            return redirect(url_for("mfw_create", form=form))
        uploaded_image = upload_image(request.files['image_file'])
        if uploaded_image: new_mfw.image_url = uploaded_image

        category_names = str(request.form['category']).split(",")
        for category_name in category_names:
            if not ((category_name == None) or (category_name == "")):
                existing_category = session.query(Category).\
                                            filter_by(name = category_name).\
                                            first()
                if existing_category:
                    new_mfw.categories.append(existing_category)
                else:
                    new_category = Category( name=category_name,
                                             creator_id=user_id )
                    new_mfw.categories.append(new_category)
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
        flash( "new MFW '" + new_mfw.name + "' created!" )
        print "\nnew_mfw POST triggered, name is: ", new_mfw.name
        return redirect(url_for("mfw_browse"))

    else:
        if not ((category_names == None) or (category_names == "")):
            return render_template( 'mfw_create.html',
                                    form=form,
                                    category_names = category_names )
        return render_template( 'mfw_create.html',
                                form=form,
                                category_names = category_names )


@app.route('/<int:mfw_id>/edit/', methods=['GET', 'POST'])
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

    elements = session.query(Element).\
                       filter_by(mfw_id=mfw_id).\
                       order_by(Element.order).\
                       all()
    form = MFWForm( request.form, mfw )

    if request.method == "POST":
        print "\nmfw_edit POST triggered, name is: ", form.name
        old_name = mfw.name
        form.populate_obj(mfw)
        edited_image_file = upload_image(request.files['edited_image_file'])
        if edited_image_file: mfw.image_url = edited_image_file
        pdb.set_trace()

        # edited_categories = request.form['edited_categories'].split(",")
        # for edited_category in edited_categories:
        #     mfw.categories.append(

        edited_category_names = str(request.form['edited_categories']).split(",")
        if edited_category_names:
            for edited_category_name in edited_category_names:
                existing_category = session.query(Category).\
                                            filter_by(name = edited_category_name).\
                                            first()
                if existing_category:
                    mfw.categories.append(existing_category)
                else:
                    category = Category( name=edited_category_name,
                                         creator_id=user_id )
                    mfw.categories.append(category)

        session.commit()
        flash( "item '" +  old_name + "' edited to '" + mfw.name + "'. Jawohl!")
        return redirect( url_for("mfw_view", mfw_id=mfw_id) )

    else:
        return render_template( 'mfw_edit.html', mfw = mfw,
                                                 elements = elements,
                                                 form = form )


@app.route('/<int:mfw_id>/delete/', methods = ['GET', 'POST'])
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
        deleted_mfw = session.query(MFW).filter_by(id = mfw_id).first()
        session.delete(deleted_mfw)
        session.commit()
        flash( "item '" + deleted_mfw.name + "' deleted. Auf Wiedersehen!")
        return redirect(url_for("mfw_browse"))

    else:
        print "/id/delete accessed..."
        return render_template( "mfw_delete.html",
                                mfw = mfw )
