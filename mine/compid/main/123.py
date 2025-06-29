from flask import Flask, render_template
import socket
app = Flask(__name__, template_folder='.')

@app.route("/")
def home():
    host = socket.gethostname()
    return render_template("main.html", result=host)

if __name__ == "__main__":
    app.run(debug=True)
