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
            mi2 = int(mi_str[6:]) // s2
            ma2 = int(ma_str[6:]) // s2
        except Exception:
            error = "Error parsing frequency markers."
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
                except Exception:
                    decrypted += '?'

    return render_template("decrypt.html", decrypted=decrypted, error=error)
