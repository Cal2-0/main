from flask import Flask, render_template, request
import os

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        user_input = request.form.get("inputText", "")
        # Convert input text to a number, e.g. sum of ASCII codes
        number = sum(ord(c) for c in user_input)
        # Calculate (5 ** number) % 23
        result = pow(5, number, 23)  # pow(base, exp, mod) is efficient mod exp
        output = f"Public Key: {result}"
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
