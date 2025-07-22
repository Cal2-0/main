from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
import os
import sys
import importlib.util

# Simple import since uni.py is now in the main directory
from uni import uni_bp
from server import chat_bp, init_socketio
from test import comp_bp
from encrp import encrp_bp
from wild import wild_bp
from movie import movie_bp
from cipher import cip_bp
from aico import aico_bp

app = Flask(__name__, template_folder='templates')
app.config["SECRET_KEY"] = "hjhjsdahhds"

# Initialize SocketIO
socketio = SocketIO(app)

# Initialize SocketIO handlers
init_socketio(socketio)

app.register_blueprint(uni_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(comp_bp)
app.register_blueprint(encrp_bp)
app.register_blueprint(wild_bp)
app.register_blueprint(movie_bp)
app.register_blueprint(cip_bp, url_prefix='/cipher')
app.register_blueprint(aico_bp)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/sht.html", methods=["GET", "POST"])
def sht():
    return render_template("sht.html")



@app.route("/Assets/<path:filename>")
def assets(filename):
    return send_from_directory('templates/Assets', filename)


@app.route("/static/css/<path:filename>")
def static_css(filename):
    return send_from_directory('css', filename)


if __name__ == "__main__":
    socketio.run(app, debug=True)
