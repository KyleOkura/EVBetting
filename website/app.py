from flask import Flask, render_template, request, jsonify, redirect, url_for
from ..tools.run_sports import run_all
from ..tools.get_sports import get_sports
#from ..tools.run_sports import *
import os
import sqlite3



def get_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database'))
    db_path = os.path.join(root_dir, 'bet_history.db')
    return db_path


def get_db():
    db_path = get_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_all', methods = ['GET', 'POST'])
def run_all():
    if request.method == 'POST':
        return redirect(url_for('current_bets'))
    return render_template('run_all.html')


if __name__ == '__main__':
    app.run(debug=True)