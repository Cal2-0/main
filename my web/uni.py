from flask import Flask, render_template, request, send_file, session, redirect, url_for,Blueprint, flash, send_from_directory
import base64
import os
import io
import base64
import numpy as np
import yt_dlp
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
import uuid
import json



uni_bp=Blueprint('uni', __name__)


@uni_bp.route("/", methods=["GET", "POST"])
def uni_root():
    if request.method == "POST":
        action = request.form.get("action")
        if action == 'pic':
            return render_template("pic.html")
        elif action == 'yt':
            return render_template("yt.html")
    return render_template("uni.html")

@uni_bp.route("/uni.html", methods=["GET", "POST"])
def uni():
    if request.method == "POST":
        action = request.form.get("action")
        if action == 'pic':
            return render_template("pic.html")
        elif action == 'yt':
            return render_template("yt.html")
    return render_template("uni.html")

@uni_bp.route("/yt", methods=["GET", "POST"])
def yt():
    output = ""
    info_data = {}
    url = ""  # Always initialize url
    download_filename = None

    if request.method == "POST":
        url = request.form.get("inputText", "").strip()
        action = request.form.get("action", "view")  # Default to view (info only)

        try:
            os.makedirs('downloads', exist_ok=True)
            ydl_opts = {
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'quiet': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if action == 'view':
                    info_data = {
                        "title": info.get("title", "Unknown"),
                        "views": info.get("view_count", "Unknown"),
                        "duration": info.get("duration", 0),
                        "upload_date": info.get("upload_date", ""),
                        "channel": info.get("uploader", "Unknown"),
                        "channel_url": info.get("uploader_url", "#"),
                        "description": (info.get("description", "")[:300] + "...") if info.get("description") else "No description",
                        "thumbnail": info.get("thumbnail", "")
                    }
                    output = "✅ Video information retrieved successfully."
                elif action == "MP4":
                    ydl.download([url])
                    filename = ydl.prepare_filename(info)
                    if os.path.exists(filename):
                        session['yt_download_file'] = filename
                        download_filename = filename
                        output = "✅ Download ready! Click the button below to get your video."
                    else:
                        output = f"❌ Downloaded file not found: {filename}"
        except Exception as e:
            output = f"❌ An error occurred: {str(e)}"

    # If coming from POST, show download button if available
    if 'yt_download_file' in session:
        download_filename = session['yt_download_file']

    return render_template("yt.html", output=output, info=info_data, url=url, download_filename=download_filename)


@uni_bp.route('/yt/download')
def yt_download():
    filename = request.args.get('file') or session.get('yt_download_file')
    if filename and os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    return 'File not found', 404


def apply_sepia(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
    arr = np.array(img)
    tr = 0.393 * arr[..., 0] + 0.769 * arr[..., 1] + 0.189 * arr[..., 2]
    tg = 0.349 * arr[..., 0] + 0.686 * arr[..., 1] + 0.168 * arr[..., 2]
    tb = 0.272 * arr[..., 0] + 0.534 * arr[..., 1] + 0.131 * arr[..., 2]
    arr[..., 0] = np.clip(tr, 0, 255)
    arr[..., 1] = np.clip(tg, 0, 255)
    arr[..., 2] = np.clip(tb, 0, 255)
    return Image.fromarray(arr.astype('uint8'))

def apply_pixelate(img, pixel_size=10):
    w, h = img.size
    img_small = img.resize((max(1, w // pixel_size), max(1, h // pixel_size)), resample=Image.NEAREST)
    return img_small.resize((w, h), Image.NEAREST)

def apply_noise(img, amount=30):
    arr = np.array(img.convert('RGB'))
    noise = np.random.randint(-amount, amount+1, arr.shape, dtype='int16')
    arr = np.clip(arr + noise, 0, 255)
    return Image.fromarray(arr.astype('uint8'))

def channel_only(img, channel):
    arr = np.array(img.convert('RGB'))
    zeros = np.zeros_like(arr)
    if channel == 0:
        zeros[..., 0] = arr[..., 0]
    elif channel == 1:
        zeros[..., 1] = arr[..., 1]
    elif channel == 2:
        zeros[..., 2] = arr[..., 2]
    return Image.fromarray(zeros)

def add_border(img, border=20, color='black'):
    return ImageOps.expand(img, border=border, fill=color)

# Configure upload folder for MelkIt
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def to_decimal(dms, ref):
    """Convert GPS coordinates from DMS or float to decimal degrees."""
    # If already a float or int, just return it
    if isinstance(dms, float) or isinstance(dms, int):
        decimal = dms
    # If tuple of floats (like (25.251167, 0.0, 0.0)), use the first value
    elif isinstance(dms, tuple) and all(isinstance(x, float) for x in dms):
        decimal = dms[0]
    # Standard DMS rational tuple
    else:
        degrees = dms[0][0] / dms[0][1]
        minutes = dms[1][0] / dms[1][1]
        seconds = dms[2][0] / dms[2][1]
        decimal = degrees + minutes / 60 + seconds / 3600
    return -decimal if ref in ['S', 'W'] else decimal

def extract_exif(file_path):
    try:
        image = Image.open(file_path)
        exif_raw = image._getexif()
    except Exception as e:
        return {'Error': f'Could not open or process image: {e}'}
    if not exif_raw:
        return {'Error': 'No EXIF data found.'}

    exif = {}
    gps_data = {}

    def convert_to_serializable(obj):
        """Convert non-serializable objects to strings"""
        if hasattr(obj, 'numerator') and hasattr(obj, 'denominator'):
            # Handle IFDRational objects
            return f"{obj.numerator}/{obj.denominator}"
        elif isinstance(obj, (tuple, list)):
            return [convert_to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: convert_to_serializable(value) for key, value in obj.items()}
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return obj

    for tag_id, value in exif_raw.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'GPSInfo':
            for key in value:
                decoded_key = GPSTAGS.get(key, key)
                gps_data[decoded_key] = convert_to_serializable(value[key])
            exif['GPSInfo'] = gps_data
        else:
            exif[tag] = convert_to_serializable(value)

    # Extract and convert GPS decimal coordinates
    return exif

@uni_bp.route('/pic', methods=['GET', 'POST'])
def pic():
    image_data = None
    output = ''
    filename = ''
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        action = request.form.get('action')
        base64_image = request.form.get('image_data')
        if uploaded_file and uploaded_file.filename:
            filename = uploaded_file.filename
            img = Image.open(uploaded_file.stream)
        elif base64_image:
            img_bytes = io.BytesIO(base64.b64decode(base64_image))
            img = Image.open(img_bytes)
            filename = 'edited_image.png'
        else:
            img = None
        if img:
                if action == 'Sharpen':
                    img = img.filter(ImageFilter.SHARPEN)
                    output = '🖼️ Image sharpened.'
                elif action == 'Enhances':
                    img = img.filter(ImageFilter.DETAIL)
                    output = '🖼️ Image Enhanced.'
                elif action == 'Enhance':
                        img = img.filter(ImageFilter.DETAIL)
                        output = '🖼️ Details enhanced.'
                elif action == 'Blur':
                    img = img.filter(ImageFilter.BLUR)
                    output = '💧 Blurred.'
                elif action == 'Contour':
                    img = img.filter(ImageFilter.CONTOUR)
                    output = '🖊️ Contour applied.'
                elif action == 'Edge':
                    img = img.filter(ImageFilter.EDGE_ENHANCE)
                    output = '🗡️ Edge enhanced.'
                elif action == 'Emboss':
                    img = img.filter(ImageFilter.EMBOSS)
                    output = '🪨 Embossed.'
                elif action == 'Smooth':
                    img = img.filter(ImageFilter.SMOOTH)
                    output = '🧈 Smoothed.'
                elif action == 'AutoContrast':
                    img = ImageOps.autocontrast(img)
                    output = '🪞 Auto contrast.'
                elif action == 'Equalize':
                    img = ImageOps.equalize(img)
                    output = '⚖️ Equalized.'
                elif action == 'Grayscale':
                    img = ImageOps.grayscale(img)
                    output = '⚫ Grayscale applied.'
                elif action == 'Invert':
                    img = ImageOps.invert(img.convert('RGB'))
                    output = '🎨 Colors inverted.'
                elif action == 'Brighten':
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(1.5)
                    output = '☀️ Brightened.'
                elif action == 'Darken':
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(0.7)
                    output = '🌑 Darkened.'
                elif action == 'ContrastUp':
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.5)
                    output = '⬆️ Contrast increased.'
                elif action == 'ContrastDown':
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(0.7)
                    output = '⬇️ Contrast decreased.'
                elif action == 'Saturate':
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(1.5)
                    output = '🌈 Saturation increased.'
                elif action == 'Desaturate':
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(0.5)
                    output = '🌫️ Saturation decreased.'
                elif action == 'Posterize':
                    img = ImageOps.posterize(img.convert('RGB'), 3)
                    output = '🖼️ Posterized.'
                elif action == 'Solarize':
                    img = ImageOps.solarize(img.convert('RGB'), threshold=128)
                    output = '🌞 Solarized.'
                elif action == 'Sepia':
                    img = apply_sepia(img)
                    output = '📸 Sepia applied.'
                elif action == 'Gamma':
                    img = ImageOps.gamma(img, 1.5)
                    output = '📈 Gamma corrected.'
                elif action == 'RotateLeft':
                    img = img.rotate(90, expand=True)
                    output = '↩️ Rotated left.'
                elif action == 'RotateRight':
                    img = img.rotate(-90, expand=True)
                    output = '↪️ Rotated right.'
                elif action == 'Rotate45':
                    img = img.rotate(45, expand=True)
                    output = '⟳ Rotated 45°.'
                elif action == 'FlipH':
                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    output = '↔️ Flipped horizontally.'
                elif action == 'FlipV':
                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                    output = '↕️ Flipped vertically.'
                elif action == 'Mirror':
                    img = ImageOps.mirror(img)
                    output = '🪞 Mirrored.'
                elif action == 'ResizeHalf':
                    w, h = img.size
                    img = img.resize((w // 2, h // 2))
                    output = '🔽 Resized to 50%.'
                elif action == 'ResizeDouble':
                    w, h = img.size
                    img = img.resize((w * 2, h * 2))
                    output = '🔼 Resized to 200%.'
                elif action == 'CropCenter':
                    w, h = img.size
                    left = w // 4
                    top = h // 4
                    right = left + w // 2
                    bottom = top + h // 2
                    img = img.crop((left, top, right, bottom))
                    output = '✂️ Center cropped.'
                elif action == 'Pixelate':
                    img = apply_pixelate(img)
                    output = '🟪 Pixelated.'
                elif action == 'Noise':
                    img = apply_noise(img)
                    output = '🌫️ Noise added.'
                elif action == 'ChannelR':
                    img = channel_only(img, 0)
                    output = '🔴 Red channel.'
                elif action == 'ChannelG':
                    img = channel_only(img, 1)
                    output = '🟢 Green channel.'
                elif action == 'ChannelB':
                    img = channel_only(img, 2)
                    output = '🔵 Blue channel.'
                elif action == 'Border':
                    img = add_border(img)
                    output = '⬛ Border added.'
                elif action== 'London':
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.5)
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(1.5)
                    img = img.filter(ImageFilter.SMOOTH)
                    img = img.filter(ImageFilter.DETAIL)
                    img = img.filter(ImageFilter.SHARPEN)
                    output = 'Filter added.'
                elif action == 'Paris':
                    enhancer = ImageEnhance.Color(img)
                    img = enhancer.enhance(1.8)
                    img = img.filter(ImageFilter.SMOOTH)
                    img = img.filter(ImageFilter.DETAIL)
                    output = '🌸 Paris filter applied.'

                elif action == 'Milan':
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.2)
                    img = ImageOps.grayscale(img)
                    img = ImageOps.equalize(img)
                    output = '🖤 Milan filter applied.'

                elif action == 'Tokyo':
                    enhancer = ImageEnhance.Brightness(img)
                    img = enhancer.enhance(1.4)
                    img = ImageOps.solarize(img.convert("RGB"), threshold=100)
                    output = '🌃 Tokyo filter applied.'

                elif action == 'Oslo':
                    img = img.convert("L")  # grayscale
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.3)
                    img = img.filter(ImageFilter.SMOOTH)
                    output = '❄️ Oslo filter applied.'

                else:
                    output = '✅ File uploaded.'
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                image_data = base64.b64encode(buf.read()).decode('utf-8')
                return render_template('pic.html', image_data=image_data, output=output, filename=filename)
    return render_template('pic.html', image_data=None, output=output, filename=filename)
@uni_bp.route('/pic/download/<filename>', methods=['POST'])
def download(filename):
    base64_image = request.form.get('file')
    action = request.form.get('action')
    if base64_image:
        img_bytes = io.BytesIO(base64.b64decode(base64_image))
        img = Image.open(img_bytes)
        if action == 'Sharpen':
            img = img.filter(ImageFilter.SHARPEN)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png', as_attachment=True, download_name='edited_' + filename)
    return '', 400

# MelkIt routes
@uni_bp.route('/home23')
def home23():
    """Home page with upload form"""
    return render_template('home23.html')

@uni_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to results"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('home23'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('home23'))
    
    if file:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file
        file.save(file_path)
        
        # Extract EXIF data
        exif_data = extract_exif(file_path)
        
        # Store data in session
        session['filename'] = filename
        session['exif_data'] = exif_data
        
        return redirect(url_for('index23'))

@uni_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@uni_bp.route('/index23')
def index23():
    """Display results page"""
    filename = session.get('filename')
    exif_data = session.get('exif_data')
    
    if not filename:
        flash('No image data available')
        return redirect(url_for('home23'))
    
    return render_template('index23.html', filename=filename, exif_data=exif_data)

if __name__ == "__main__":
    uni_bp.run(debug=True)
