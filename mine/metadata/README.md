# Melkit - Image Metadata Extractor

A beautiful web application for extracting metadata from uploaded images.

## Features

- 📸 Upload images through a modern, responsive interface
- 🔍 Extract EXIF metadata including GPS coordinates
- 🗺️ Display location information when available
- 🎨 Beautiful glass-morphism UI design
- 📱 Mobile-responsive design

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python network.py
```

3. Open your browser and go to `http://localhost:5000`

## How to Use

1. **Upload Image**: Go to the home page and click "Choose Image" to select an image file
2. **Extract Metadata**: Click "Extract Metadata" to process the image
3. **View Results**: The application will redirect to the results page showing:
   - The uploaded image
   - All extracted EXIF metadata
   - GPS coordinates and location (if available)

## File Structure

- `network.py` - Main Flask application
- `templates/home.html` - Upload page
- `templates/index.html` - Results display page
- `uploads/` - Directory where uploaded images are stored
- `requirements.txt` - Python dependencies

## Routes

- `/` or `/home` - Upload page
- `/upload` - File upload handler (POST)
- `/index` - Results display page
- `/uploads/<filename>` - Serve uploaded images

## Features

- **Image Upload**: Drag and drop or click to browse
- **Metadata Extraction**: Extracts all available EXIF data
- **GPS Processing**: Converts GPS coordinates to decimal format
- **Error Handling**: Graceful error messages for invalid files
- **Session Management**: Maintains upload state between pages 