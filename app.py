import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Audius Node listesi
NODES = ["https://audius-discovery-1.cultureregen.com", "https://discovery-provider.audius.co"]

@app.route('/')
def home():
    return "API Online"

@app.route('/search', methods=['GET'])
def search():
    # Hem 'q' hem 'term' kontrolü yaparak Android ile tam uyum sağlıyoruz
    query = request.args.get('q') or request.args.get('term')
    if not query:
        return jsonify([])

    for node in NODES:
        try:
            url = f"{node}/v1/tracks/search?query={query}&app_name=ERCAN_PLAYER"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', [])
                results = []
                for track in data:
                    results.append({
                        "trackId": str(track.get('id', '')),
                        "trackName": str(track.get('title', 'Bilinmeyen')),
                        "artistName": str(track.get('user', {}).get('name', 'Sanatçı')),
                        "previewUrl": f"{node}/v1/tracks/{track.get('id')}/stream?app_name=ERCAN_PLAYER",
                        "artworkUrl100": str(track.get('artwork', {}).get('150x150', ''))
                    })
                return jsonify(results)
        except Exception as e:
            print(f"Node Error: {e}")
            continue
            
    return jsonify([]) # Hiçbir node çalışmazsa boş liste dön (Hata verme)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
