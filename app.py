import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query: return jsonify([])
    
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da ara ve ilk 10 sonucu al
            search_results = ydl.extract_info(f"ytsearch10:{query}", download=False)['entries']
            results = []
            for info in search_results:
                results.append({
                    'trackId': info.get('id'),
                    'trackName': info.get('title'),
                    'artistName': info.get('uploader'),
                    'previewUrl': info.get('url'),
                    'artworkUrl100': info.get('thumbnail')
                })
            return jsonify(results)
    except Exception as e:
        return jsonify([]), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
