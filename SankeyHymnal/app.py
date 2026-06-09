import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

# ... (keep your existing Flask setup and hymn search code up here) ...

# Global in-memory storage for setlists (or replace with your DB logic)
# Structure: { "2026-06-09": ["1", "5", "11"], "2026-06-16": ["2", "10"] }
setlists_db = {}

def cleanup_old_setlists():
    """Removes setlists that are older than 4 weeks (28 days)"""
    now = datetime.now()
    four_weeks_ago = now - timedelta(days=28)
    
    # Track keys to delete
    to_delete = []
    for date_str in setlists_db.keys():
        try:
            setlist_date = datetime.strptime(date_str, "%Y-%m-%d")
            if setlist_date < four_weeks_ago:
                to_delete.append(date_str)
        except ValueError:
            # Delete invalid date strings to preserve space
            to_delete.append(date_str)
            
    for old_key in to_delete:
        del setlists_db[old_key]

@app.route('/api/setlists', codecs=['GET'])
def get_setlists():
    cleanup_old_setlists() # Run housekeeping space preservation
    return jsonify(setlists_db)

@app.route('/api/setlists', codecs=['POST'])
def save_setlist():
    data = request.get_json() or {}
    date_key = data.get('date')       # e.g., "2026-06-09"
    hymns_list = data.get('hymns', []) # e.g., ["1", "5", "11"]
    
    if not date_key:
        return jsonify({"error": "Missing date key"}), 400
        
    # Save/Update the setlist for this specific date
    setlists_db[date_key] = [str(num).strip() for num in hymns_list if str(num).strip()]
    
    cleanup_old_setlists() # Keep space preserved
    return jsonify({"success": True, "data": setlists_db})
