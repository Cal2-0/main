from flask import Flask, render_template, request,Blueprint
import os
import yt_dlp


ytt_dlp = Blueprint('yt', __name__,)

@ytt_dlp.route("/yt", methods=["GET", "POST"])
def yt():
    output = ""
    info_data = {}
    url = ""  # Always initialize url


    if request.method == "POST":
        url = request.form.get("inputText", "").strip()
        action = request.form.get("action", "view")  # Default to view (info only)
        

        try:
            # Create downloads directory if it doesn't exist
            os.makedirs('downloads', exist_ok=True)

            ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',  # saves in current folder
        'format': 'best',
        'quiet': False
    }


            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info (this doesn't download)
                info = ydl.extract_info(url, download=False)

                # If action is 'view', prepare info data to show on page
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
                    # Download the video
                    ydl.download([url])
                    filename = ydl.prepare_filename(info)
                    output = f"✅ Download complete! File saved at: {filename}"
            
            

        except Exception as e:
            output = f"❌ An error occurred: {str(e)}"
            

    return render_template("yt.html", output=output, info=info_data, url=url)

if __name__ == "__main__":
    ytt_dlp.run(debug=True)
