from flask import Flask, render_template, request, send_from_directory
import os
import sys
import importlib.util

app = Flask(__name__, template_folder='templates')


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/sht.html", methods=["GET", "POST"])
def sht():
    return render_template("sht.html")


@app.route("/Assets/<path:filename>")
def assets(filename):
    return send_from_directory('templates/Assets', filename)


if __name__ == "__main__":
    app.run(debug=True)
