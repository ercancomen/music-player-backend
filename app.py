import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

# Sunucunun çalışıp çalışmadığını test etmek için ana sayfa
@app.route('/')
def home():
    return "Müzik Sunucusu Aktif!"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query:
        return jsonify([])
    
    # Render gibi servislerde YouTube engelini aşmak için ayarlar
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da ara ve ilk 5 sonucu al
            search_results = ydl.extract_info(f"ytsearch5:{query}", download=False)
            
            if not search_results or 'entries' not in search_results:
                return jsonify([])
                
            results = []
            for entry in search_results['entries']:
                if entry:
                    results.append({
                        'trackId': str(entry.get('id', '')),
                        'trackName': entry.get('title', 'Bilinmeyen Şarkı'),
                        'artistName': entry.get('uploader', 'Bilinmeyen Sanatçı'),
                        'previewUrl': entry.get('url', ''),
                        'artworkUrl100': entry.get('thumbnail', '')
                    })
            return jsonify(results)
    except Exception as e:
        # Hatayı terminale bas
        print(f"Hata: {str(e)}")
        return jsonify([{"trackId": "error", "trackName": str(e)}]), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
