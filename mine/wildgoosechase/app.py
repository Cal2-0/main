from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__, template_folder='')  # HTMLs in same folder

SECRET_CODE =os.getenv("key")
numb2=os.getenv("c")
numb3=os.getenv("d")
numb4=os.getenv("e")

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("1.html")

@app.route("/follow-the-white-rabbit.html", methods=["GET", "POST"])
def follow_the_white_rabbit():
    return render_template("follow-the-white-rabbit.html")

@app.route("/the-gate.html", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == SECRET_CODE:
            return render_template("the-lock.html")
        else:
            return render_template("the-gate.html", error="Incorrect code. Try again.")
    return render_template("the-gate.html")

@app.route("/the-lock.html", methods=["GET", "POST"])
def lock():
    return render_template("the-lock.html")

@app.route("/deltasignal.html", methods=["GET", "POST"])
def deltasignal():
    return render_template("deltasignal.html")

@app.route("/next.html", methods=["GET", "POST"])
def next():
    return render_template("next.html")

@app.route("/mystery.html", methods=["GET", "POST"])
def mystery():
    return render_template("mystery.html")

@app.route("/finale.html", methods=["GET", "POST"])
def finale():
    return render_template("finale.html")

@app.route("/complexity.html", methods=["GET", "POST"])
def complexity():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb4:
            return render_template("finale.html")
        else:
            return render_template("complexity.html", error="Incorrect code. Try again.")
    return render_template("complexity.html")

@app.route("/JoshuaOppenheimer.html", methods=["GET", "POST"])
def joshuaoppenheimer():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb3:
            return render_template("next.html")
        else:
            return render_template("JoshuaOppenheimer.html", error="Incorrect code. Try again.")
    return render_template("JoshuaOppenheimer.html")

@app.route("/c.html", methods=["GET", "POST"])
def c():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb2:
            return render_template("deltasignal.html")
        else:
            return render_template("c.html", error="Incorrect code. Try again.")
    return render_template("c.html")

if __name__ == "__main__":
    app.run(debug=True)
