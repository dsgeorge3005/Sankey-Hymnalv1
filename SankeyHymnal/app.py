import time
from datetime import datetime, timedelta
# 1. FIXED: Changed 'render_code' to 'render_template'
from flask import Flask, render_template, request, jsonify

# 2. FIXED: Ensure 'app' is declared FIRST before any routes use it!
app = Flask(__name__)

# Global in-memory storage for setlists
# WARNING: This resets whenever Render restarts. Consider a database later!
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

# --- CORE ROUTING FIXES FOR RENDER ---

@app.route('/', methods=['GET'])
def home():
    """
    FIXED: Root route to satisfy Render's health check.
    Make sure your 'index.html' file is inside a folder named 'templates'.
    """
    try:
        return render_template('index.html')
    except Exception:
        # Fallback string if index.html isn't in the templates folder yet
        return "Sankey Hymnal API is running!", 200

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    """
    FIXED: Resolves the constant 404 errors seen in the logs.
    """
    return jsonify({
        "status": "healthy",
        "message": "Welcome to the Sankey Hymnal Dashboard",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# --- API SETLIST ENDPOINTS ---

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

# --- PLACEHOLDERS FOR YOUR OTHER ROUTES ---
# Paste your existing search and audio routing code right below here!

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Your search logic goes here
    return jsonify({"results": [], "query": query})


if __name__ == '__main__':
    # Local development settings
    app.run(debug=True, port=10000)
