import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# En stabil Audius sunucuları
AUDIUS_NODES = [
    "https://audius-discovery-1.cultureregen.com",
    "https://discovery-provider.audius.co",
    "https://audius-dp.creary.net"
]

@app.route('/')
def home():
    return "Ercan Music API (Audius) Aktif!"

@app.route('/search', methods=['GET'])
def search():
    # Android'den gelen her iki parametreyi de kontrol et
    query = request.args.get('q') or request.args.get('term')
    
    if not query:
        return jsonify([])

    for node in AUDIUS_NODES:
        try:
            # Audius API üzerinden arama yap
            url = f"{node}/v1/tracks/search?query={query}&app_name=ERCAN_MUSIC"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                results = []
                for track in data:
                    # Android'deki iTunesResult sınıfıyla tam eşleşme
                    results.append({
                        'trackId': str(track.get('id')),
                        'trackName': track.get('title', 'Bilinmeyen'),
                        'artistName': track.get('user', {}).get('name', 'Bilinmeyen'),
                        'previewUrl': f"{node}/v1/tracks/{track.get('id')}/stream?app_name=ERCAN_MUSIC",
                        'artworkUrl100': track.get('artwork', {}).get('150x150', '')
                    })
                return jsonify(results)
        except Exception as e:
            print(f"Node hatası: {e}")
            continue # Diğer sunucuyu dene

    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
