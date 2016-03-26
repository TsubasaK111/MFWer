# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

from MFWR import app

# Database Dependencies
from MFWR.models import session, MFW, Element

# Auth Dependencies
from auth import *

# Debugging Dependencies
import pdb, pprint, inspect


@app.route('/MFWs/<int:mfw_id>/new/', methods=['GET', 'POST'])
def newElement(mfw_id):
    """page to create a new menu item."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not mfw.user_id == user_id:
        flash("Only MFW owners can add new items.")
        return redirect(url_for("publicMenu",mfw_id = mfw_id))

    if request.method == "POST":
        mfw_name = request.form['mfw_name']
        print "\nnewElement POST triggered, name is: ", mfw_name
        newElement = element( name=mfw_name, mfw_id=mfw.id )
        session.add(newElement)
        session.commit()
        flash( "new item '" + mfw_name + "' created!")
        print "POST worked!"
        return redirect(url_for("showMenu", mfw_id=mfw.id))

    else:
        return render_template('newElement.html', mfw = mfw )


@app.route('/MFWs/<int:mfw_id>/public')
def publicMenu(mfw_id):
    """ displays all menu items for a MFW id, read-only."""

    mfw = session.query(mfw).filter_by(id = mfw_id).first()
    elements = session.query(element).filter_by(mfw_id = mfw_id)
    creator = getUserInfo(mfw.user_id)

    return render_template( 'publicMenu.html',
                            elements = elements,
                            mfw = mfw,
                            creator= creator )


@app.route('/MFWs/<int:mfw_id>/')
def showMenu(mfw_id):
    """ displays all menu items for a MFW id, with all CRUD options."""

    if 'access_token' not in flask_session:
        return logInRedirect()

    mfw = session.query(mfw).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])

    if not mfw.user_id == user_id:
        return redirect( url_for("publicMenu",mfw_id = mfw_id) )

    elements = session.query(element).filter_by(mfw_id = mfw_id)
    creator = getUserInfo(mfw.user_id)

    return render_template( 'showMenu.html',
                            mfw = mfw,
                            elements = elements,
                            creator = creator )


@app.route('/MFWs/<int:mfw_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editelement(mfw_id, menu_id):
    """page to edit a menu item."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not mfw.user_id == user_id:
        return redirect(url_for("publicMenu",mfw_id = mfw_id))
        flash("Only MFW owners can edit items.")

    if request.method == "POST":
        edited_name = request.form['edited_name']
        print "\neditelement POST triggered, name is: ", edited_name
        old_name = session.query(element).filter_by(id = menu_id).first().name

        result = session.execute(""" UPDATE menu_item
                                     SET name=:edited_name
                                     WHERE id=:edited_menu_item_id; """,
                                 { "edited_name": edited_name,
                                   "edited_menu_item_id": menu_id}
                                 )
        session.commit()
        flash( "item '" +  old_name + "' edited to '" + edited_name + "'. Jawohl!")
        return redirect(url_for("showMenu", mfw_id=mfw_id))

    else:
        element = session.query(element).filter_by(id = menu_id).first()
        return render_template('editelement.html',
                                  mfw = mfw,
                                  element = element )


@app.route('/MFWs/<int:mfw_id>/<int:menu_id>/delete/', methods=["GET","POST"])
def deleteelement(mfw_id, menu_id):
    """page to delete a menu item."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    mfw = session.query(MFW).filter_by(id = mfw_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not mfw.user_id == user_id:
        flash("Only MFW owners can delete items.")
        return redirect(url_for("publicMenu",mfw_id = mfw_id))

    if request.method == "POST":
        print "\ndeleteelement POST triggered!, menu_id is: ", menu_id
        deletedelement = session.query(element).filter_by(id = menu_id).first()
        session.delete(deletedelement)
        session.commit()
        flash( "item '" + deletedelement.name + "' deleted. Auf Wiedersehen!")
        return redirect(url_for("showMenu", mfw_id=mfw_id))

    else:
        print "MFWs/delete accessed..."
        element = session.query(element).filter_by(id = menu_id).first()
        return render_template( 'deleteelement.html',
                                   element = element,
                                   mfw = mfw )
