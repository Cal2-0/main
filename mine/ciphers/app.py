from flask import Flask, render_template, request
import base64
app = Flask(__name__)  # Use default templates folder "templates"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        if action == 'ceaser':
            return render_template("ceaser.html")
        elif action == 'vignere':
            return render_template("vignere.html")
        elif action == 'atbash':
            return render_template("atbash.html")
        elif action == 'bacon':
            return render_template("bacon.html")
        elif action == 'calx':
            return render_template("calx.html")
    return render_template("index.html")

def caesar_shift_char(ch, shift):
    if ch.isalpha():
        base = ord('A') if ch.isupper() else ord('a')
        offset = ord(ch) - base
        shifted = (offset + shift) % 26
        return chr(base + shifted)
    else:
        return ch

def caesar_encode(text, shift):
    return ''.join(caesar_shift_char(ch, shift) for ch in text)

def caesar_decode(text, shift):
    return ''.join(caesar_shift_char(ch, -shift) for ch in text)

def vigenere_encode(text, key):
    l = {chr(i + ord('a')): i for i in range(26)}
    rev = {v: k for k, v in l.items()}
    text = text.lower()
    key = key.lower()
    c = ''
    key_len = len(key)
    key_index = 0
    for char in text:
        if char.isalpha():
            key_char = key[key_index % key_len]
            shifted_index = (l[char] + l[key_char]) % 26
            c += rev[shifted_index]
            key_index += 1
        else:
            c += char
    return c

def vigenere_decode(text, key):
    l = {chr(i + ord('a')): i for i in range(26)}
    rev = {v: k for k, v in l.items()}
    text = text.lower()
    key = key.lower()
    c = ''
    key_len = len(key)
    key_index = 0
    for char in text:
        if char.isalpha():
            key_char = key[key_index % key_len]
            shifted_index = (l[char] - l[key_char]) % 26
            c += rev[shifted_index]
            key_index += 1
        else:
            c += char
    return c

def calx_encode(text, shift, key):
    step1 = caesar_encode(text, shift)
    step2 = vigenere_encode(step1, key)
    # encode to bytes, then base64 encode, finally decode bytes to str
    step3 = base64.b64encode(step2.encode()).decode()
    return step3

def calx_decode(text, shift, key):
    try:
        step1 = base64.b64decode(text).decode()
    except Exception:
        return "Invalid base64 input."
    step2 = vigenere_decode(step1, key)
    step3 = caesar_decode(step2, shift)
    return step3

@app.route("/calx", methods=["GET", "POST"])
def calx():
    output = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        shift_str = request.form.get("shift", "0")
        key = request.form.get("key", "")
        action = request.form.get("action")

        try:
            shift = int(shift_str)
            if shift < 1:
                output = "Shift must be a positive integer."
                return render_template("calx.html", output=output)
        except ValueError:
            output = "Shift must be a number."
            return render_template("calx.html", output=output)

        if not key.isalpha():
            output = "Key must be alphabetic."
            return render_template("calx.html", output=output)

        if action == "encode":
            output = calx_encode(text, shift, key)
        elif action == "decode":
            output = calx_decode(text, shift, key)
        else:
            output = "Invalid action."

    return render_template("calx.html", output=output)

@app.route("/bacons", methods=["GET", "POST"])
def bacons():
    output = ""
    bacon_dict = {
        'a': 'AAAAA', 'b': 'AAAAB', 'c': 'AAABA', 'd': 'AAABB', 'e': 'AABAA',
        'f': 'AABAB', 'g': 'AABBA', 'h': 'AABBB', 'i': 'ABAAA', 'j': 'ABAAA',  # i/j same
        'k': 'ABAAB', 'l': 'ABABA', 'm': 'ABABB', 'n': 'ABBAA', 'o': 'ABBAB',
        'p': 'ABBBA', 'q': 'ABBBB', 'r': 'BAAAA', 's': 'BAAAB', 't': 'BAABA',
        'u': 'BAABB', 'v': 'BAABB', 'w': 'BABAA', 'x': 'BABAB', 'y': 'BABBA',
        'z': 'BABBB'
    }
    rev_bacon = {v: k for k, v in bacon_dict.items()}

    if request.method == "POST":
        text = request.form.get("text", "").lower()
        action = request.form.get("action")

        if action == "encode":
            # Encode each letter to Bacon code, ignore non-alpha
            encoded = []
            for ch in text:
                if ch in bacon_dict:
                    encoded.append(bacon_dict[ch])
                elif ch == ' ':
                    encoded.append(' ')  # preserve spaces
                else:
                    # skip non-letters or you can add something else
                    pass
            output = ' '.join(encoded)

        elif action == "decode":
            # Decode assumes groups of 5 letters A/B separated by spaces
            # Clean input (keep only A, B, and spaces)
            clean_text = ''.join(ch for ch in text.upper() if ch in ['A','B',' '])
            parts = clean_text.split()
            decoded = ''
            for part in parts:
                if len(part) == 5 and part in rev_bacon:
                    decoded += rev_bacon[part]
                else:
                    decoded += '?'  # unknown pattern
            output = decoded

    return render_template("bacon.html", output=output)

@app.route("/ceaser.html", methods=["GET", "POST"])
def ceaser():
    output = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        shift = request.form.get("shift", "0")
        action = request.form.get("action")

        try:
            shift = int(shift)
        except ValueError:
            output = "Shift must be a number."
            return render_template("ceaser.html", output=output)

        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                offset = ord(char) - base
                if action == "encode":
                    shifted = (offset + shift) % 26
                else:  # decode
                    shifted = (offset - shift) % 26
                result += chr(base + shifted)
            else:
                result += char  # keep punctuation/digits unchanged

        output = result

    return render_template("ceaser.html", output=output)
@app.route("/vignere", methods=["GET", "POST"])
def vignere():
    output = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        key = request.form.get("shift", "")  # keyword for Vigenère
        action = request.form.get("action")

        l = {chr(i + ord('a')): i for i in range(26)}
        rev = {v: k for k, v in l.items()}  # reverse mapping

        text = text.lower()
        key = key.lower()

        if not key.isalpha() or len(key) == 0:
            output = "Key must be a non-empty alphabetic string."
            return render_template("vignere.html", output=output)

        c = ''
        key_len = len(key)
        key_index = 0

        for char in text:
            if char.isalpha():
                key_char = key[key_index % key_len]
                if action == "encode":
                    shifted_index = (l[char] + l[key_char]) % 26
                else:  # decode
                    shifted_index = (l[char] - l[key_char]) % 26
                c += rev[shifted_index]
                key_index += 1
            else:
                c += char  # keep punctuation/digits unchanged

        output = c

    return render_template("vignere.html", output=output)

@app.route("/atbash", methods=["GET", "POST"])
def atbash():
    output = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        # Map letters a→z, b→y, ..., z→a
        l = {chr(i + ord('a')): chr(ord('z') - i) for i in range(26)}
        
        result = ""
        for char in text:
            if char.isalpha():
                lower = char.lower()
                converted = l[lower]
                # Preserve case
                result += converted.upper() if char.isupper() else converted
            else:
                result += char  # leave other characters unchanged

        output = result

    return render_template("atbash.html", output=output)



if __name__ == "__main__":
    app.run(debug=True)
