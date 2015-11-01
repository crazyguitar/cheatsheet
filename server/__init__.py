from flask import Flask, abort, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/<string:page>', methods=['GET'])
def cheatsheet(page):
    try:
        return render_template('cheatsheet/{0}.html'.format(page))
    except:
        abort(404)
