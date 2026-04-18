import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Ercan Player Gelişmiş API Aktif!"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query:
        return jsonify([])

    # Daha isabetli sonuçlar için sorguyu müzik odaklı hale getiriyoruz
    search_query = f"ytsearch20:{query} official audio"

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da 20 sonuç arıyoruz (Daha detaylı)
            info = ydl.extract_info(search_query, download=False)
            
            results = []
            if info and 'entries' in info:
                for entry in info['entries']:
                    if entry and entry.get('url'):
                        results.append({
                            'trackId': entry.get('id', 'unknown'),
                            'trackName': entry.get('title', 'Bilinmeyen Şarkı'),
                            'artistName': entry.get('uploader', 'Bilinmeyen Sanatçı'),
                            'previewUrl': entry.get('url', ''),
                            'artworkUrl100': entry.get('thumbnail', '')
                        })
            
            return jsonify(results)
    except Exception as e:
        # Hata olsa bile 500 hatası yerine boş liste döndürerek uygulamayı koru
        return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
