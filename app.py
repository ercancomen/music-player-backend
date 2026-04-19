import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Daha stabil Audius Discovery Node'ları
NODES = [
    "https://discoveryprovider.audius.co",
    "https://audius-discovery-1.cultureregen.com",
    "https://discovery-provider.audius.co",
    "https://audius-metadata-1.figment.io"
]

@app.route('/')
def home():
    return "API Online"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q') or request.args.get('term')
    if not query:
        return jsonify([])

    for node in NODES:
        try:
            # Audius v1 search API
            url = f"{node}/v1/tracks/search?query={query}&app_name=ERCAN_PLAYER"
            response = requests.get(url, timeout=5) # Timeout'u 5 saniyeye düşürüp hızlıca diğer node'a geçiyoruz
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                if not data: continue # Veri boşsa diğer node'u dene
                
                results = []
                for track in data:
                    # Bazı track'lerde stream linki farklı olabilir, güvenli alalım
                    track_id = track.get('id')
                    results.append({
                        "trackId": str(track_id),
                        "trackName": str(track.get('title', 'Bilinmeyen')),
                        "artistName": str(track.get('user', {}).get('name', 'Sanatçı')),
                        "previewUrl": f"{node}/v1/tracks/{track_id}/stream?app_name=ERCAN_PLAYER",
                        "artworkUrl100": str(track.get('artwork', {}).get('150x150', ''))
                    })
                return jsonify(results)
        except Exception as e:
            print(f"Node Error ({node}): {e}")
            continue
            
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
