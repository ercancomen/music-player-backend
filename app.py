import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

AUDIUS_NODES = [
    "https://audius-discovery-1.cultureregen.com",
    "https://discovery-provider.audius.co",
    "https://audius-dp.creary.net"
]

APP_NAME = "ERCAN_MUSIC"


def clean(text):
    return (text or "").lower()


def score_track(track, query):
    title = clean(track.get("title"))
    artist = clean(track.get("user", {}).get("name"))
    q = clean(query)

    score = 0

    # güçlü eşleşme
    if q in title:
        score += 5
    if q in artist:
        score += 3

    # kelime bazlı eşleşme
    for word in q.split():
        if word in title:
            score += 2
        if word in artist:
            score += 1

    # türkçe boost (yumuşak)
    if any(x in title for x in ["aşk", "kalp", "sev", "göz", "bir", "sen"]):
        score += 1

    return score


@app.route("/")
def home():
    return "API çalışıyor"


@app.route("/search")
def search():
    query = request.args.get("term")

    if not query:
        return jsonify([])

    for node in AUDIUS_NODES:
        try:
            url = f"{node}/v1/tracks/search"
            params = {
                "query": query,   # 🔴 ARTIK query'yi bozmadık
                "app_name": APP_NAME,
                "limit": 50
            }

            res = requests.get(url, params=params, timeout=5)

            if res.status_code != 200:
                continue

            data = res.json().get("data", [])

            # 🔥 SADECE SIRALA (filtre yok)
            sorted_tracks = sorted(
                data,
                key=lambda x: score_track(x, query),
                reverse=True
            )

            results = []
            for track in sorted_tracks[:15]:
                results.append({
                    "trackId": track.get("id"),
                    "trackName": track.get("title", "Bilinmeyen"),
                    "artistName": track.get("user", {}).get("name", "Bilinmeyen"),
                    "previewUrl": f"{node}/v1/tracks/{track.get('id')}/stream?app_name={APP_NAME}",
                    "artworkUrl100": track.get("artwork", {}).get("150x150", "")
                })

            return jsonify(results)

        except:
            continue

    return jsonify([])
