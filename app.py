import os
import requests
from flask import Flask, request, jsonifyapp = Flask(__name__)

# En stabil Audius sunucuları
AUDIUS_NODES = [
    "https://audius-discovery-1.cultureregen.com",
    "https://discovery-provider.audius.co",
    "https://audius-dp.creary.net"
]

@app.route('/')
def home():
    return "Müzik API Aktif!"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query: return jsonify([])
    
    # Sırayla sunucuları dene
    for node in AUDIUS_NODES:
        try:
            url = f"{node}/v1/tracks/search?query={query}&app_name=ERCAN_MUSIC"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json().get('data', [])
                results = []
                for track in data:
                    results.append({
                        'trackId': track.get('id'),
                        'trackName': track.get('title', 'Bilinmeyen'),
                        'artistName': track.get('user', {}).get('name', 'Bilinmeyen'),
                        'previewUrl': f"{node}/v1/tracks/{track.get('id')}/stream?app_name=ERCAN_MUSIC",
                        'artworkUrl100': track.get('artwork', {}).get('150x150', '')
                    })
                return jsonify(results)
        except:
            continue
            
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
