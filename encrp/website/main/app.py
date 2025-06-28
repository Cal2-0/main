from flask import Flask, render_template, redirect, url_for, request
import os

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

p = 23  # use your prime p here

def get_public_key(priv):
    return pow(5, priv, 23)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/encrypt", methods=["GET", "POST"])
def encrypt():
    encrypted_str = ""
    if request.method == "POST":
        x = request.form.get("message", "")
        priv = int(request.form.get("priv", 0))
        other_pub = int(request.form.get("other_pub", 0))
        s = pow(other_pub, priv, p)  # shared key using DH
        freq_map = {}
        for i in x:
            if i != ' ':
                freq_map[i] = x.count(i)
        mi = min(freq_map.values()) if freq_map else 1
        ma = max(freq_map.values()) if freq_map else 1
        factor = (mi * ma) * s
        en = []
        for i in x:
            if i == ' ':
                en.append('-1')  # space marker
            else:
                val = (ord(i) * factor)
                en.append(str(val))
        en.append('009901' + str(int(mi * s)))
        en.append('009900' + str(int(ma * s)))
        encrypted_str = ' '.join(en)
    return render_template("encrypt.html", encrypted=encrypted_str)

@app.route("/decrypt", methods=["GET", "POST"])
def decrypt():
    decrypted = ""
    error = ""
    if request.method == "POST":
        encrypted_message = request.form.get("encrypted", "")
        priv2 = int(request.form.get("priv2", 0))
        sender_pub = int(request.form.get("sender_pub", 0))
        s2 = pow(sender_pub, priv2, p)  # shared key
        ex1 = encrypted_message.split()
        if len(ex1) < 2:
            error = "Invalid encrypted message format."
            return render_template("decrypt.html", decrypted=decrypted, error=error)
        mi_str = ex1[-2]
        ma_str = ex1[-1]
        if not (mi_str.startswith('009901') and ma_str.startswith('009900')):
            error = "Error: Invalid encryption format."
            return render_template("decrypt.html", decrypted=decrypted, error=error)
        try:
            mi2 = int(round(int(mi_str[6:]) / s2))
            ma2 = int(round(int(ma_str[6:]) / s2))
        except Exception as e:
            error = f"Error parsing frequency markers: {e}"
            return render_template("decrypt.html", decrypted=decrypted, error=error)
        factor2 = (mi2 * ma2) * s2
        encrypted_values = ex1[:-2]
        for val in encrypted_values:
            if val == '-1':  # space marker
                decrypted += ' '
            else:
                try:
                    num = int(val)
                    original_ord = num // factor2
                    if 0 <= original_ord <= 1114111:
                        decrypted += chr(original_ord)
                    else:
                        decrypted += '?'
                except Exception as e:
                    decrypted += '?'
    return render_template("decrypt.html", decrypted=decrypted, error=error)

@app.route("/publickey", methods=["GET", "POST"])
def public_key():
    output = ""
    if request.method == "POST":
        try:
            priv = int(request.form.get("priv", 0))
            result = get_public_key(priv)
            output = f"Public Key: {result}"
        except Exception as e:
            output = f"Error: {e}"
    return render_template("index.html", output=output)

@app.route("/quit")
def quit_app():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Server shutting down..."

if __name__ == "__main__":
    app.run(debug=True)
