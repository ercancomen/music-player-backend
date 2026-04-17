import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Audius Müzik API Aktif!"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('term')
    if not query: return jsonify([])
    
    try:
        # Audius Discovery API kullanımı
        search_url = f"https://discoveryprovider.audius.co/v1/tracks/search?query={query}&app_name=ERCAN_MUSIC"
        response = requests.get(search_url, timeout=10)
        data = response.json().get('data', [])
        
        results = []
        for track in data:
            track_id = track.get('id')
            # Direkt çalınabilir stream URL'si
            stream_url = f"https://discoveryprovider.audius.co/v1/tracks/{track_id}/stream?app_name=ERCAN_MUSIC"
            
            results.append({
                'trackId': str(track_id),
                'trackName': track.get('title'),
                'artistName': track.get('user', {}).get('name'),
                'previewUrl': stream_url,
                'artworkUrl100': track.get('artwork', {}).get('150x150', '')
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
