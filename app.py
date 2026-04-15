import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query:
        return jsonify([])
    
    # Daha hızlı ve güvenli arama için ayarlar
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da ara
            info_dict = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
            if not info_dict or 'entries' not in info_dict:
                return jsonify([])
                
            results = []
            for entry in info_dict['entries']:
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
        print(f"Hata oluştu: {str(e)}")
        # Hatayı uygulamaya gönder ki ne olduğunu görelim
        return jsonify([{"trackId": "error", "trackName": str(e)}]), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
