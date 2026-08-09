from flask import Flask, request, jsonify, send_file
import json
import datetime
import os
from pathlib import Path

app = Flask(__name__)

# Serve the main page
@app.route('/', methods=['GET'])
def serve_index():
    return send_file('../static/index.html')

# Receive tracking data
@app.route('/track', methods=['POST'])
def track_data():
    data = request.json
    
    # Log to console (visible in Vercel dashboard)
    print(f"\n{'='*60}")
    print(f"TRACKING DATA RECEIVED - {datetime.datetime.now()}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2))
    print(f"{'='*60}\n")
    
    # Save to /tmp directory (temporary storage on Vercel)
    try:
        log_file = '/tmp/tracker_log.txt'
        with open(log_file, 'a') as f:
            f.write(f"\n--- {datetime.datetime.now()} ---\n")
            f.write(json.dumps(data, indent=2))
            f.write("\n")
    except Exception as e:
        print(f"Log write error: {e}")
    
    return jsonify({"status": "success", "message": "Data received"})

# View logs (for debugging)
@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open('/tmp/tracker_log.txt', 'r') as f:
            return f.read()
    except:
        return "No logs yet"

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

# For Vercel serverless deployment
app = app