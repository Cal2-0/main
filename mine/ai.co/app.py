# main.py

from flask import Flask, render_template, request
from aichat import aichat_bp
from movai import movai_bp
from holi import holi_bp
import os

app = Flask(__name__,)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret')

# Register blueprint
app.register_blueprint(aichat_bp)
app.register_blueprint(movai_bp)
app.register_blueprint(holi_bp)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
