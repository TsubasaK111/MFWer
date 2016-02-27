# Webserver Dependencies
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify

from MFWR import app

# Database Dependencies
from MFWR.models import session, MFW, element

# Auth Dependencies
from auth import *

# Debugging Dependencies
import pdb, pprint, inspect


@app.route('/MFWs/<int:MFW_id>/new/', methods=['GET', 'POST'])
def newElement(MFW_id):
    """page to create a new menu item."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    MFW = session.query(MFW).filter_by(id = MFW_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not MFW.user_id == user_id:
        flash("Only MFW owners can add new items.")
        return redirect(url_for("publicMenu",MFW_id = MFW_id))

    if request.method == "POST":
        new_name = request.form['new_name']
        print "\nnewElement POST triggered, name is: ", new_name
        newElement = element( name=new_name, MFW_id=MFW.id )
        session.add(newElement)
        session.commit()
        flash( "new item '" + new_name + "' created!")
        print "POST worked!"
        return redirect(url_for("showMenu", MFW_id=MFW.id))

    else:
        return render_template('newElement.html', MFW = MFW)


@app.route('/MFWs/<int:MFW_id>/public')
def publicMenu(MFW_id):
    """ displays all menu items for a MFW id, read-only."""

    MFW = session.query(MFW).filter_by(id = MFW_id).first()
    elements = session.query(element).filter_by(MFW_id = MFW_id)
    creator = getUserInfo(MFW.user_id)

    return render_template( 'publicMenu.html',
                            elements = elements,
                            MFW = MFW,
                            creator= creator )


@app.route('/MFWs/<int:MFW_id>/')
def showMenu(MFW_id):
    """ displays all menu items for a MFW id, with all CRUD options."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    MFW = session.query(MFW).filter_by(id = MFW_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not MFW.user_id == user_id:
        return redirect(url_for("publicMenu",MFW_id = MFW_id))

    elements = session.query(element).filter_by(MFW_id = MFW_id)
    creator = getUserInfo(MFW.user_id)

    return render_template( 'showMenu.html',
                            MFW = MFW,
                            elements = elements,
                            creator = creator )


@app.route('/MFWs/<int:MFW_id>/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editelement(MFW_id, menu_id):
    """page to edit a menu item."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    MFW = session.query(MFW).filter_by(id = MFW_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not MFW.user_id == user_id:
        return redirect(url_for("publicMenu",MFW_id = MFW_id))
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
        return redirect(url_for("showMenu", MFW_id=MFW_id))

    else:
        element = session.query(element).filter_by(id = menu_id).first()
        return render_template('editelement.html',
                                  MFW = MFW,
                                  element = element )


@app.route('/MFWs/<int:MFW_id>/<int:menu_id>/delete/', methods=["GET","POST"])
def deleteelement(MFW_id, menu_id):
    """page to delete a menu item."""

    if 'access_token' not in flask_session:
        return logInRedirect()
    MFW = session.query(MFW).filter_by(id = MFW_id).first()
    user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
    if not MFW.user_id == user_id:
        flash("Only MFW owners can delete items.")
        return redirect(url_for("publicMenu",MFW_id = MFW_id))

    if request.method == "POST":
        print "\ndeleteelement POST triggered!, menu_id is: ", menu_id
        deletedelement = session.query(element).filter_by(id = menu_id).first()
        session.delete(deletedelement)
        session.commit()
        flash( "item '" + deletedelement.name + "' deleted. Auf Wiedersehen!")
        return redirect(url_for("showMenu", MFW_id=MFW_id))

    else:
        print "MFWs/delete accessed..."
        element = session.query(element).filter_by(id = menu_id).first()
        return render_template( 'deleteelement.html',
                                   element = element,
                                   MFW = MFW )
