from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request
import os

app = Flask(__name__)

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

def reverse_geocode(lat, lon):
    geolocator = Nominatim(user_agent="exif_geocoder")
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        return location.address if location else "Address not found"
    except Exception as e:
        return f"Geocoding error: {e}"

def extract_exif(file):
    try:
        image = Image.open(file)
        exif_raw = image._getexif()
    except Exception as e:
        return {'Error': f'Could not open or process image: {e}'}
    if not exif_raw:
        return {'Error': 'No EXIF data found.'}

    exif = {}
    gps_data = {}

    for tag_id, value in exif_raw.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == 'GPSInfo':
            for key in value:
                decoded_key = GPSTAGS.get(key, key)
                gps_data[decoded_key] = value[key]
            exif['GPSInfo'] = gps_data
        else:
            exif[tag] = value

    # Extract and convert GPS decimal coordinates
    if gps_data:
        try:
            lat = to_decimal(gps_data['GPSLatitude'], gps_data['GPSLatitudeRef'])
            lon = to_decimal(gps_data['GPSLongitude'], gps_data['GPSLongitudeRef'])
            exif['GPSLatitudeDecimal'] = lat
            exif['GPSLongitudeDecimal'] = lon
            # Get human-readable address via reverse geocoding
            address = reverse_geocode(lat, lon)
            exif['GPSAddress'] = address
        except Exception:
            exif['GPSDecimalError'] = "GPS data incomplete or invalid, cannot convert to decimal or reverse geocode."

    return exif

@app.route('/', methods=['GET', 'POST'])
def index():
    exif_data = None
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            exif_data = extract_exif(uploaded_file)
    return render_template('index.html', exif_data=exif_data)

if __name__ == '__main__':
    app.run(debug=True)
