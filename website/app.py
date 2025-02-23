from flask import Flask, render_template, request, jsonify
from ..tools.bet_history import *
from ..tools.run_sports import *

import sqlite3

app = Flask(__name__)


def get_db():
    conn = sqlite3.connect('bet_history.db')
    return conn

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_bets', methods = ['POST', 'GET'])
def get_bets():
    if request.method == 'POST':
        bets = run_all()
