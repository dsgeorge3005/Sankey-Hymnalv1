import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# The filename on the server where the shared data is stored
DATA_FILE = 'dashboard_data.json'

def load_dashboard_data():
    """Safely reads the shared notes and calendar date from the server disk."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure the structure always has the expected keys
                if isinstance(data, dict):
                    return {
                        "notes": data.get("notes", ""),
                        "date": data.get("date", "")
                    }
        except Exception as e:
            print(f"Error reading dashboard JSON file: {e}")
    
    # Return empty defaults if the file doesn't exist or is corrupted
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
    
    # CRITICAL FIX: Only overwrite data if the key is explicitly sent in the payload.
    # This prevents notes from erasing dates (and vice versa) across different devices.
    if 'notes' in req_data and req_data['notes'] is not None:
        current_data['notes'] = req_data['notes']
        
    if 'date' in req_data and req_data['date'] is not None:
        current_data['date'] = req_data['date']
        
    save_dashboard_data(current_data)
    return jsonify({"status": "success", "data": current_data})

# --- Placeholder for your other existing app routes ---
# Make sure to keep your existing /search, /audio, or image retrieval routes below this line!
#
# @app.route('/search')
# def search():
#     ...
# -----------------------------------------------------

if __name__ == '__main__':
    # Run the server
    app.run(debug=True)
