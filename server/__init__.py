"""
This module is cheatsheet website backend.
"""

from flask import Flask, abort, render_template
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

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
