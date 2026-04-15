import os
import requests
from flask import Flask, requestimport os
import requests
from flask import Flask, request, jsonify
import yt_dlp
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "OK"

# 🔍 SEARCH (yt-dlp YOK)
def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", r.text)

    return list(dict.fromkeys(video_ids))[:10]


# 🎧 STREAM AL
def get_stream(video_id):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(
            f"https://www.youtube.com/watch?v={video_id}",
            download=False
        )

        return {
            "url": info["url"],
            "title": info.get("title"),
            "artist": info.get("uploader"),
            "thumbnail": info.get("thumbnail")
        }


# 🔎 SEARCH ENDPOINT
@app.route('/search')
def search():
    query = request.args.get('term')
    if not query:
        return jsonify([])

    ids = search_youtube(query)

    return jsonify([
        {
            "trackId": vid,
            "trackName": "Tap to play",
            "previewUrl": ""
        }
        for vid in ids
    ])


# 🎵 STREAM ENDPOINT (YENİ)
@app.route('/stream')
def stream():
    video_id = request.args.get('id')

    try:
        data = get_stream(video_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port), jsonify
import yt_dlp
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Sunucu Çalışıyor!"

# 🔍 YouTube HTML'den video ID çek
def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    video_ids = re.findall(r"watch\?v=(\S{11})", r.text)

    # ilk 5 benzersiz sonuç
    return list(dict.fromkeys(video_ids))[:5]


# 🎵 Video → stream URL al
def get_stream_url(video_id):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return info.get("url"), info
    except:
        return None, None


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query:
        return jsonify([])

    try:
        video_ids = search_youtube(query)

        results = []

        for vid in video_ids:
            stream_url, info = get_stream_url(vid)

            if not stream_url or not info:
                continue

            results.append({
                'trackId': vid,
                'trackName': info.get('title', 'Bilinmeyen'),
                'artistName': info.get('uploader', 'Bilinmeyen'),
                'previewUrl': stream_url,
                'artworkUrl100': info.get('thumbnail', '')
            })

        return jsonify(results)

    except Exception as e:
        return jsonify([{
            "trackId": "error",
            "trackName": str(e)
        }]), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
