from flask import Flask, render_template, request
import os

p = 23  # use your prime p here

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

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

        en.append('009901' + str(mi * s))
        en.append('009900' + str(ma * s))

        encrypted_str = ' '.join(en)

    return render_template("encrypt.html", encrypted=encrypted_str)
