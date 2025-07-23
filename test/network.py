from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import sys
import os

def to_decimal(dms, ref):
    """Convert GPS coordinates from DMS to decimal."""
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    decimal = degrees + minutes / 60 + seconds / 3600
    return -decimal if ref in ['S', 'W'] else decimal

def ext(filepath):
    if not os.path.isfile(filepath):
        print("❌ File does not exist.")
        return

    try:
        image = Image.open(filepath)
        exif_raw = image._getexif()
    except Exception as e:
        print("❌ Could not open or process image:", e)
        return

    if not exif_raw:
        print("⚠️ No EXIF data found.")
        return

    exif = {}
    gps_data = {}

    # Map and collect EXIF tags
    for tag_id, value in exif_raw.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value

    # Filter only key EXIF tags
    key_tags = [
        "Make", "Model", "Software", "DateTimeOriginal", "ExposureTime",
        "FNumber", "ISOSpeedRatings", "FocalLength", "ExposureProgram",
        "WhiteBalance", "MeteringMode", "Flash", "Orientation",
        "ColorSpace", "ExifVersion", "ImageDescription"
    ]

    print("\n📸 Photo Metadata:\n" + "-"*50)
    for tag in key_tags:
        if tag in exif:
            print(f"{tag:20}: {exif[tag]}")

    # Extract GPS if available
    if "GPSInfo" in exif:
        gps_raw = exif["GPSInfo"]
        for key in gps_raw:
            name = GPSTAGS.get(key, key)
            gps_data[name] = gps_raw[key]

        if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
            lat = to_decimal(gps_data["GPSLatitude"], gps_data["GPSLatitudeRef"])
            lon = to_decimal(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
            print("\n🌍 GPS Coordinates:")
            print(f"Latitude           : {lat}")
            print(f"Longitude          : {lon}")
        else:
            print("\n📍 GPSInfo found, but coordinates are incomplete.")
    else:
        print("\n❌ No GPS data found.")

ext("image.jpeg")
