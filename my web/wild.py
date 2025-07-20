from flask import Flask, render_template, request,Blueprint
import os
from dotenv import load_dotenv
load_dotenv()


wild_bp=Blueprint('1', __name__,)  # HTMLs in same folder

SECRET_CODE =os.getenv("key")
numb2=os.getenv("c")
numb3=os.getenv("d")
numb4=os.getenv("e")
numb5=os.getenv("f")

@wild_bp.route("/1.html", methods=["GET", "POST"])
def home():
    return render_template("1.html")

@wild_bp.route("/follow-the-white-rabbit.html", methods=["GET", "POST"])
def follow_the_white_rabbit():
    return render_template("follow-the-white-rabbit.html")

@wild_bp.route("/the-gate.html", methods=["GET", "POST"])
def gate():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == SECRET_CODE:
            return render_template("the-lock.html")
        else:
            return render_template("the-gate.html", error="Incorrect code. Try again.")
    return render_template("the-gate.html")

@wild_bp.route("/the-lock.html", methods=["GET", "POST"])
def lock():
    return render_template("the-lock.html")

@wild_bp.route("/deltasignal.html", methods=["GET", "POST"])
def deltasignal():
    return render_template("deltasignal.html")

@wild_bp.route("/next.html", methods=["GET", "POST"])
def next():
    return render_template("next.html")

@wild_bp.route("/mystery.html", methods=["GET", "POST"])
def mystery():
    print(numb5)
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb5:
            return render_template("complexity.html")
        else:
            return render_template("mystery.html", error="Incorrect code. Try again.")
    return render_template("mystery.html")

@wild_bp.route("/finale.html", methods=["GET", "POST"])
def finale():
    return render_template("finale.html")

@wild_bp.route("/complexity.html", methods=["GET", "POST"])
def complexity():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb4:
            return render_template("finale.html")
        else:
            return render_template("complexity.html", error="Incorrect code. Try again.")
    return render_template("complexity.html")

@wild_bp.route("/JoshuaOppenheimer.html", methods=["GET", "POST"])
def joshuaoppenheimer():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb3:
            return render_template("next.html")
        else:
            return render_template("JoshuaOppenheimer.html", error="Incorrect code. Try again.")
    return render_template("JoshuaOppenheimer.html")

@wild_bp.route("/c.html", methods=["GET", "POST"])
def c():
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        if user_input == numb2:
            return render_template("deltasignal.html")
        else:
            return render_template("c.html", error="Incorrect code. Try again.")
    return render_template("c.html")

if __name__ == "__main__":
    wild_bp.run(debug=True)
