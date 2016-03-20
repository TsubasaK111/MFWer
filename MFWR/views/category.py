# Webserver Dependencies
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory

from MFWR import app

# Database Dependencies
from MFWR.models import session, MFW, Element, Category

# WTForm Dependencies
from MFWR.forms import *

# Auth Dependencies
from auth import *

# Debugging Dependencies
import pdb, pprint, inspect

@app.route('/categories/')
@app.route('/categories/browse/')
def category_browse():
    """tile styled page to display and browse categories"""
    categories = session.query(Category).all()
    return render_template( 'category_browse.html', categories = categories )


@app.route('/categories/<int:category_id>/view/')
def category_view(category_id):
    """view the MFWs in a category"""
    thisCategory = session.query(Category).filter_by(id = category_id).first()
    theseMFWs = session.query(MFW).filter_by(category_id=category_id).order_by(MFW.id).all()
    return render_template( 'category_view.html',
                            category=thisCategory,
                            MFWs=theseMFWs )


@app.route('/categories/create/', methods=['GET', 'POST'])
def category_create():
    """page to create a new Mental Framework."""
    form = CategoryForm(request.form)
    # if request.method == "POST" and form.validate():
    if request.method == "POST":
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId(
                      flask_session['email'],flask_session['google_plus_id'] )
        category_name = request.form['category_name']
        category_description = request.form['category_description']
        new_category = Category( name = category_name,
                                   creator_id = user_id )
        session.add(new_category)
        session.commit()

        flash( "new Category '" + category_name + "' created!" )
        print "\nnew_category POST triggered, name is: ", category_name
        return redirect(url_for("category_browse"))

    else:
        if 'access_token' not in flask_session:
            return logInRedirect()
        user_id = getUserId(
                      flask_session['email'], flask_session['google_plus_id'] )
        return render_template('category_create.html')


# @app.route('/<int:category_id>/edit/', methods=['GET', 'POST'])
# def MFW_edit(category_id):
#     """page to edit a MFW. (authorized only for creators)"""
#
#     if 'access_token' not in flask_session:
#         return logInRedirect()
#     thisMFW = session.query(MFW).filter_by(id = category_id).first()
#     user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
#     if not thisMFW.creator_id == user_id:
#         return redirect(url_for("MFW_view", category_id = category_id))
#         flash("Only the creator of a MFW can edit items.")
#
#     if request.method == "POST":
#         edited_name = request.form['edited_name']
#         edited_description = request.form['edited_description']
#         print "\nMFW_edit POST triggered, name is: ", edited_name
#
#         old_name = session.query(MFW).filter_by(id = category_id).first().name
#
#         result = session.execute(""" UPDATE MFW
#                                      SET name=:edited_name
#                                          description=:edited_description
#                                      WHERE id=:category_id; """,
#                                  { "edited_name": edited_name,
#                                    "edited_description": edited_description,
#                                    "category_id": category_id }
#                                  )
#         session.commit()
#         flash( "item '" +  old_name + "' edited to '" + edited_name + "'. Jawohl!")
#         return redirect( url_for("MFW_view", category_id=category_id) )
#
#     else:
#         elements = session.query(Element).filter_by(id = category_id).all()
#         return render_template( 'MFW_edit.html',
#                                 MFW = MFW,
#                                 elements = elements )
#
#
# @app.route('/<int:category_id>/delete/', methods = ['GET', 'POST'])
# def MFW_delete(category_id):
#     """page to delete a MFW (authorized only for creators)."""
#
#     if 'access_token' not in flask_session:
#         return logInRedirect()
#
#     thisMFW = session.query(MFW).filter_by(id = category_id).first()
#     user_id = getUserId(flask_session['email'],flask_session['google_plus_id'])
#
#     if not thisMFW.creator_id == user_id:
#         flash("Only MFW owners can delete MFWs.")
#         return redirect(url_for("MFW_view", category_id = category_id))
#
#     if request.method == "POST":
#         print "\nMFW_delete POST triggered!"
#         deletedMFW = session.query(MFW).filter_by(id = category_id).first()
#         session.delete(deletedMFW)
#         session.commit()
#         flash( "item '" + deletedMFW.name + "' deleted. Auf Wiedersehen!")
#         return redirect(url_for("MFW_browse"))
#
#     else:
#         print "/id/delete accessed..."
#         return render_template( "MFW_delete.html",
#                                 MFW = thisMFW )
