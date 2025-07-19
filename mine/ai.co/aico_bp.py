# main.py

from flask import Flask, render_template, request
from aichat import aichat_bp
from movai import movai_bp
from holi import holi_bp
import os

aico_bp =Flask(__name__)
a.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret')

# Register blueprint
aico_bp.register_blueprint(aichat_bp)
aico_bp.register_blueprint(movai_bp)
aico_bp.register_blueprint(holi_bp)

@aico_bp.route("/", methods=["GET", "POST"])
def aico():
    return render_template("aico.html")

if __name__ == "__main__":
    aico_bp.run(debug=True)
