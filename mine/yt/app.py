from flask import Flask, render_template, request
import os
import yt_dlp

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    Title = ""
    Views = ""
    
    if request.method == "POST":
        url = request.form.get("inputText", "").strip()
        try:
            download_dir = os.path.join(os.getcwd(), 'downloads')
            ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',  # saves in current folder
    'format': 'best',
}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                Title = info.get('title', 'Unknown')
                Views = info.get('view_count', 'Unknown')
                filename = ydl.prepare_filename(info)
                output = f"✅ Download complete! File saved at: {filename}"

        except Exception as e:
            output = f"❌ An error occurred: {str(e)}"
    
    return render_template("index.html", output=output, Title=Title, Views=Views)

if __name__ == "__main__":
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)
