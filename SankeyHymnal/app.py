import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = 'dashboard_data.json'

def load_dashboard_data():
    """Helper to read shared plan from disk safely"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"notes": "", "date": ""}

def save_dashboard_data(data):
    """Helper to save shared plan to disk"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Returns the globally saved notes and service calendar date"""
    return jsonify(load_dashboard_data())

@app.route('/api/dashboard', methods=['POST'])
def update_dashboard():
    """Receives changes from any device and saves them globally"""
    req_data = request.get_json() or {}
    current_data = load_dashboard_data()
    
    # Update only fields sent in the request package
    if 'notes' in req_data:
        current_data['notes'] = req_data['notes']
    if 'date' in req_data:
        current_data['date'] = req_data['date']
        
    save_dashboard_data(current_data)
    return jsonify({"status": "success", "data": current_data})

# (Keep your existing /search or /audio routes down here)
if __name__ == '__main__':
    app.run(debug=True)
