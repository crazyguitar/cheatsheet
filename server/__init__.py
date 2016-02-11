"""
This module is cheatsheet website backend.
"""
import os

from flask import Flask, abort, render_template
from flask_sslify import SSLify

app = Flask(__name__)
if 'DYNO' in os.environ:
    sslify = SSLify(app)


@app.route('/', methods=['GET'])
def index():
    """ Index page API """
    return render_template('index.html')


@app.route('/<string:page>', methods=['GET'])
def cheatsheet(page):
    """ Cheat sheet API """
    try:
        return render_template('cheatsheet/{0}.html'.format(page))
    except:
        abort(404)
