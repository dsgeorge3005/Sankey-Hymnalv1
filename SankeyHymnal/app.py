import json
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global in-memory storage for setlists
setlists_db = {}
HYMNS_DATABASE = []

# --- LOAD YOUR ACTUAL HYMNS.JSON DATABASE ---
def load_hymns_database():
    global HYMNS_DATABASE
    # Checks for 'hymns.json' in your main project folder
    json_path = os.path.join(os.path.dirname(__file__), 'hymns.json')
    
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                HYMNS_DATABASE = json.load(f)
                print(f" Successfully loaded {len(HYMNS_DATABASE)} hymns from hymns.json")
        except Exception as e:
            print(f"❌ Error reading hymns.json: {e}")
            HYMNS_DATABASE = []
    else:
        print("⚠️ Warning: hymns.json not found in root directory! Please make sure it's uploaded next to app.py.")
        HYMNS_DATABASE = []

# Initialize the database on startup
load_hymns_database()


def cleanup_old_setlists():
    """Removes setlists that are older than 4 weeks (28 days)"""
    now = datetime.now()
    four_weeks_ago = now - timedelta(days=28)
    
    to_delete = []
    for key_str in list(setlists_db.keys()):
        try:
            date_part = key_str.split("::")[0]
            setlist_date = datetime.strptime(date_part, "%Y-%m-%d")
            if setlist_date < four_weeks_ago:
                to_delete.append(key_str)
        except Exception:
            to_delete.append(key_str)
            
    for old_key in to_delete:
        if old_key in setlists_db:
            del setlists_db[old_key]

@app.route('/', methods=['GET'])
def home():
    try:
        return render_template('index.html')
    except Exception:
        return "Sankey Hymnal API is running! (Make sure index.html is inside the 'templates' folder)", 200

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/api/setlists', methods=['GET'])
def get_setlists():
    cleanup_old_setlists() 
    return jsonify(setlists_db)

@app.route('/api/setlists', methods=['POST'])
def save_setlist():
    data = request.get_json() or {}
    date_key = data.get('date')       
    hymns_list = data.get('hymns', []) 
    
    if not date_key:
        return jsonify({"error": "Missing date key"}), 400
        
    setlists_db[date_key] = [str(num).strip() for num in hymns_list if str(num).strip()]
    cleanup_old_setlists() 
    return jsonify({"success": True, "data": setlists_db})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])

    matched_results = []
    for hymn in HYMNS_DATABASE:
        hymn_num = str(hymn.get("number", "")).strip().lower()
        hymn_title = str(hymn.get("title", "")).strip().lower()
        
        # Match exactly by number, or check if query is in the title string
        if query == hymn_num or query in hymn_title:
            matched_results.append(hymn)

    return jsonify(matched_results)

if __name__ == '__main__':
    app.run(debug=True, port=10000)
