"""
This module is cheatsheet website backend.
"""

from flask import Flask, abort, render_template

app = Flask(__name__)


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

@app.route('/78FA73EC439FE689CE23876A72F75D5A.txt')
def ssl_hash():
    """ ssl has file """
    try:
        return render_template('78FA73EC439FE689CE23876A72F75D5A.txt')
    except:
        abort(404)
