import time
from datetime import datetime, timedelta
# 1. FIXED: Changed 'render_code' to 'render_template'
from flask import Flask, render_template, request, jsonify

# 2. FIXED: Ensure 'app' is declared FIRST before any routes use it!
app = Flask(__name__)

# Global in-memory storage for setlists
setlists_db = {}

def cleanup_old_setlists():
    """Removes setlists that are older than 4 weeks (28 days)"""
    now = datetime.now()
    four_weeks_ago = now - timedelta(days=28)
    
    to_delete = []
    for date_str in list(setlists_db.keys()):
        try:
            setlist_date = datetime.strptime(date_str, "%Y-%m-%d")
            if setlist_date < four_weeks_ago:
                to_delete.append(date_str)
        except ValueError:
            to_delete.append(date_str)
            
    for old_key in to_delete:
        del setlists_db[old_key]

# 3. FIXED: Changed 'codecs=' to 'methods='
@app.route('/api/setlists', methods=['GET'])
def get_setlists():
    cleanup_old_setlists() 
    return jsonify(setlists_db)

# 4. FIXED: Changed 'codecs=' to 'methods='
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

# ... (Keep all your existing search, home, and audio routing code below this) ...
