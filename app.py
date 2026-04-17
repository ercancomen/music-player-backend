import os
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Müzik Sunucusu Aktif!"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query:
        return jsonify([])
    
    # YouTube engellerini aşmak ve hızı artırmak için en güvenli ayarlar
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'nocheckcertificate': True,
        'ignoreerrors': True, # Bir hata olursa diğerine geç
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube'da ara (ilk 10 sonuç)
            info_dict = ydl.extract_info(f"ytsearch10:{query}", download=False)
            
            if not info_dict or 'entries' not in info_dict:
                return jsonify([])
                
            results = []
            for entry in info_dict['entries']:
                if entry and entry.get('url'): # URL varsa ekle
                    results.append({
                        'trackId': str(entry.get('id', '')),
                        'trackName': entry.get('title', 'Bilinmeyen Şarkı'),
                        'artistName': entry.get('uploader', 'Bilinmeyen Sanatçı'),
                        'previewUrl': entry.get('url', ''),
                        'artworkUrl100': entry.get('thumbnail', '')
                    })
            return jsonify(results)
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Render'ın beklediği port ayarı
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
