from yt_dlp import YoutubeDL

url = 'https://youtu.be/vEQ8CXFWLZU'

ydl_opts = {}
with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    print(info.keys())