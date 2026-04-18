import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# En güncel ve hızlı Audius sunucuları
AUDIUS_NODES = [
    "https://audius-discovery-1.cultureregen.com",
    "https://discovery-provider.audius.co",
    "https://audius-dp.creary.net"
]

@app.route('/')
def home():
    return "Ercan Music API Aktif! Arama yapmak için /search?q=sorgu kullanın."

@app.route('/search', methods=['GET'])
def search():
    # Android tarafı 'q' harfiyle veri gönderiyor
    query = request.args.get('q') or request.args.get('term') or request.args.get('query')
    
    if not query:
        return jsonify([])

    for node in AUDIUS_NODES:
        try:
            # Audius API Arama
            url = f"{node}/v1/tracks/search?query={query}&app_name=ERCAN_PLAYER"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                results = []
                for track in data:
                    # BURASI ÇOK ÖNEMLİ: Android'deki iTunesResult sınıfı ile birebir aynı isimler olmalı
                    results.append({
                        "trackId": str(track.get('id', '')),
                        "trackName": track.get('title', 'Bilinmeyen Şarkı'),
                        "artistName": track.get('user', {}).get('name', 'Bilinmeyen Sanatçı'),
                        "previewUrl": f"{node}/v1/tracks/{track.get('id')}/stream?app_name=ERCAN_PLAYER",
                        "artworkUrl100": track.get('artwork', {}).get('150x150', '')
                    })
                return jsonify(results)
        except Exception as e:
            print(f"Hata: {e}")
            continue
            
    return jsonify([])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
