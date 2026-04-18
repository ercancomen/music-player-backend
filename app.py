import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)AUDIUS_NODES = [
    "https://audius-discovery-1.cultureregen.com",
    "https://discovery-provider.audius.co",
    "https://audius-dp.creary.net"
]

@app.route('/')
def home():
    return "API Aktif - Arama yapmak icin /search?q=sorgu kullanin."

@app.route('/search', methods=['GET'])
def search():
    # Android'den gelen 'q' parametresini al
    query = request.args.get('q')
    
    if not query:
        return jsonify([])

    for node in AUDIUS_NODES:
        try:
            url = f"{node}/v1/tracks/search?query={query}&app_name=ERCAN_PLAYER"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                results = []
                for track in data:
                    # Android tarafındaki iTunesResult sınıfı ile TAM UYUM
                    results.append({
                        "trackId": str(track.get('id', '')), # ID'yi mutlaka String'e cevir
                        "trackName": str(track.get('title', 'Bilinmeyen Sarki')),
                        "artistName": str(track.get('user', {}).get('name', 'Bilinmeyen Sanatci')),
                        "previewUrl": f"{node}/v1/tracks/{track.get('id')}/stream?app_name=ERCAN_PLAYER",
                        "artworkUrl100": str(track.get('artwork', {}).get('150x150', ''))
                    })
                return jsonify(results)
        except:
            continue
            
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
