from flask import Flask, render_template, request, redirect, send_file
from PIL import Image
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
p = 23  # Prime for DH key exchange

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def steg_write(image_path, message, output_path='edited_image.png', spacing=10):
    img = Image.open(image_path)
    pixel_array = np.array(img)

    message_values = [ord(char) for char in message]
    image_shape = pixel_array.shape
    pixel_list = pixel_array.flatten().tolist()
    
    if len(message_values) * spacing > len(pixel_list):
        raise ValueError("Message too long")

    idx_list = [i * spacing for i in range(len(message_values))]
    for idx, val in zip(idx_list, message_values):
        pixel_list[idx] = val

    edited_array = np.array(pixel_list).reshape(image_shape).astype(np.uint8)
    Image.fromarray(edited_array).save(output_path)
    return len(message_values) 

def steg_read(image_path, message_length, spacing=10):
    img = Image.open(image_path)
    pixel_array = np.array(img)
    pixel_list = pixel_array.flatten().tolist()

    idx_list = [i * spacing for i in range(message_length)]
    hidden_values = [pixel_list[i] for i in idx_list]
    return ''.join(chr(v) for v in hidden_values)

def encr(message, priv, other_pub):
    s = pow(other_pub, priv, p)
    freq_map = {i: message.count(i) for i in message if i != ' '}
    mi = min(freq_map.values())
    ma = max(freq_map.values())
    factor = mi * ma * s

    result = []
    for i in message:
        result.append('-1' if i == ' ' else str(ord(i) * factor))
    result.append('009901' + str(mi * s))
    result.append('009900' + str(ma * s))
    return ' '.join(result)

def decr(encoded, priv, sender_pub):
    vals = encoded.strip().split()
    s = pow(sender_pub, priv, p)
    mi = int(vals[-2][6:]) // s
    ma = int(vals[-1][6:]) // s
    factor = mi * ma * s

    decrypted = ''
    for val in vals[:-2]:
        decrypted += ' ' if val == '-1' else chr(int(val) // factor)
    return decrypted

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hide", methods=["GET", "POST"])
def hide():
    if request.method == "POST":
        msg = request.form["message"]
        priv = int(request.form["priv"])
        pub = int(request.form["other_pub"])

        uploaded_file = request.files["image"]
        if not uploaded_file or not uploaded_file.filename.lower().endswith('.png'):
            return render_template("hide.html", success=False, error="Only PNG files are allowed.")

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(input_path)

        encrypted = encr(msg, priv, pub)
        msg_length=steg_write(input_path, encrypted, "edited_image.png")
        return render_template("hide.html", success=True,message_length=msg_length)

    return render_template("hide.html", success=False)

@app.route("/reveal", methods=["GET", "POST"])
def reveal():
    if request.method == "POST":
        length = int(request.form["msg_len"])
        priv = int(request.form["priv2"])
        pub = int(request.form["sender_pub"])

        uploaded_file = request.files.get("image")
        if not uploaded_file or not uploaded_file.filename.lower().endswith('.png'):
            return render_template("reveal.html", message=None, error="Please upload a valid PNG image.")

        filename = secure_filename(uploaded_file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(input_path)

        try:
            hidden = steg_read(input_path, length)
            decrypted = decr(hidden, priv, pub)
        except Exception as e:
            return render_template("reveal.html", message=None, error=f"Error during reveal: {str(e)}")

        return render_template("reveal.html", message=decrypted, error=None)

    return render_template("reveal.html", message=None)


if __name__ == "__main__":
    app.run(debug=True)
