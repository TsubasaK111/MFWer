# Webserver Dependencies
from flask import Flask, render_template, request, redirect, url_for,  send_from_directory

from MFWR import app

# Image Upload Dependencies
import os
from werkzeug import secure_filename


def allowed_file(filename):
    return '.' in filename and  \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_IMAGE_EXTENSIONS']


def upload_image(file):
    """ store image to configured location and return url.
        if no file, return nothing. """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.getcwd() + os.path.join( app.config['UPLOAD_FOLDER'],
                                              filename ))
        return url_for('uploaded_image', filename=filename)


@app.route('/uploads/images/<filename>')
def uploaded_image(filename):
    print "uploaded_image triggered!"
    return send_from_directory(os.getcwd() + app.config['UPLOAD_FOLDER'], filename)
