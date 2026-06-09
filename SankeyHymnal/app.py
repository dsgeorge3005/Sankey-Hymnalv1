import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# Core Application File Mappings
DATA_FILE = 'dashboard_data.json'
HYMNS_JSON_FILE = 'hymns.json'
AUDIO_FOLDER = 'audio'

def load_hymns_database():
    """Loads the main hymn book database from hymns.json"""
    if os.path.exists(HYMNS_JSON_FILE):
        try:
            with open(HYMNS_JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading hymn database JSON: {e}")
    else:
        print(f"CRITICAL WARNING: '{HYMNS_JSON_FILE}' could not be located on the server!")
    return []

def load_dashboard_data():
    """Safely reads the shared notes and calendar date from the server disk."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return {
                        "notes": data.get("notes", ""),
                        "date": data.get("date", "")
                    }
        except Exception as e:
            print(f"Error reading dashboard JSON file: {e}")
    return {"notes": "", "date": ""}

def save_dashboard_data(data):
    """Saves the dashboard state securely to the server disk."""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error writing dashboard JSON file: {e}")

@app.route('/')
def index():
    """Renders the main app home page."""
    return render_template('index.html')

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Returns the globally saved notes and service calendar date to any device checking in."""
    return jsonify(load_dashboard_data())

@app.route('/api/dashboard', methods=['POST'])
def update_dashboard():
    """
    Receives updates from a device and saves them globally.
    Protects against data deletion by checking if fields are explicitly provided.
    """
    req_data = request.get_json() or {}
    current_data = load_dashboard_data()
    
    if 'notes' in req_data and req_data['notes'] is not None:
        current_data['notes'] = req_data['notes']
        
    if 'date' in req_data and req_data['date'] is not None:
        current_data['date'] = req_data['date']
        
    save_dashboard_data(current_data)
    return jsonify({"status": "success", "data": current_data})

@app.route('/search')
def search():
    """Searches the database for hymn numbers or titles matching the query string"""
    query = request.args.get('q', '').strip().lower()
    hymns = load_hymns_database()
    results = []
    
    if not query:
        return jsonify([])
        
    for hymn in hymns:
        hymn_num = str(hymn.get('number', '')).lower()
        hymn_title = str(hymn.get('title', '')).lower()
        
        if query in hymn_num or query in hymn_title:
            results.append(hymn)
            
    return jsonify(results)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    """Serves the vocal part rehearsal tracks safely from the audio folder"""
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
