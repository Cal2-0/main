from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
import os
import uuid
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/')
@app.route('/home')
def home():
    """Home page with upload form"""
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redirect to results"""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('home'))
    
    if file:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file
        file.save(file_path)
        
        # Extract EXIF data
        exif_data = extract_exif(file_path)
        
        # Store data in session
        session['filename'] = filename
        session['exif_data'] = exif_data
        
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/index')
def index():
    """Display results page"""
    filename = session.get('filename')
    exif_data = session.get('exif_data')
    
    if not filename:
        flash('No image data available')
        return redirect(url_for('home'))
    
    return render_template('index.html', filename=filename, exif_data=exif_data)

if __name__ == '__main__':
    app.run(debug=True)
