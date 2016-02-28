"""
This is a simple cheatsheet webapp.
"""
import os

from flask import Flask, send_from_directory

DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.join(DIR, 'docs', 'build', 'html')

app = Flask(__name__)

@app.route('/<path:path>')
def static_proxy(path):
    """Static files proxy"""
    return send_from_directory(ROOT, path)

@app.route('/')
def index_redirection():
    """Redirecting index file"""
    return send_from_directory(ROOT, 'index.html')

if __name__ == "__main__":
    print DIR, ROOT
    app.run(debug=True)
