from flask import Flask, render_template, request, jsonify
from .tools.bet_history import *
from .tools.run_sports import *

import sqlite3

app = Flask(__name__)


def get_all_bets():
