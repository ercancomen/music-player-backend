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


# ---------------------------
# Yardımcı Fonksiyonlar
# ---------------------------

def clean_text(text):
    return (text or "").lower().strip()


def build_query(query):
    # Daha iyi sonuç için query genişlet
    return f"{query} turkish official"


def is_relevant(track, query):
    title = clean_text(track.get("title"))
    artist = clean_text(track.get("user", {}).get("name"))

    q = clean_text(query)

    return q in title or q in artist


def score_track(track, query):
    title = clean_text(track.get("title"))
    artist = clean_text(track.get("user", {}).get("name"))
    q = clean_text(query)

    score = 0

    # Ana eşleşme
    if q in title:
        score += 5
    if q in artist:
        score += 3

    # Türkçe boost
    if "turk" in title or "turk" in artist:
        score += 2

    # kısa başlıklar genelde daha doğru
    if len(title) < 40:
        score += 1

    return score


def format_track(track, node):
    return {
        "trackId": track.get("id"),
        "trackName": track.get("title", "Bilinmeyen"),
        "artistName": track.get("user", {}).get("name", "Bilinmeyen"),
        "previewUrl": f"{node}/v1/tracks/{track.get('id')}/stream?app_name={APP_NAME}",
        "artworkUrl100": track.get("artwork", {}).get("150x150", "")
    }


# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def home():
    return "Müzik API Aktif 🚀"


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("term")

    if not query:
        return jsonify([])

    search_query = build_query(query)

    for node in AUDIUS_NODES:
        try:
            url = f"{node}/v1/tracks/search"
            params = {
                "query": search_query,
                "app_name": APP_NAME,
                "limit": 50
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code != 200:
                continue

            data = response.json().get("data", [])

            # 1. filtre
            filtered = [t for t in data if is_relevant(t, query)]

            # filtre boşsa fallback (filtreyi gevşet)
            if not filtered:
                filtered = data

            # 2. skorla ve sırala
            sorted_tracks = sorted(
                filtered,
                key=lambda x: score_track(x, query),
                reverse=True
            )

            # 3. ilk 15'i al
            final_tracks = sorted_tracks[:15]

            results = [format_track(t, node) for t in final_tracks]

            return jsonify(results)

        except Exception as e:
            continue

    return jsonify([])


# ---------------------------
# RUN
# ---------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
