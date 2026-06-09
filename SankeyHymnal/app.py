import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Global in-memory storage for setlists
setlists_db = {}

# Mock Database Dataset matching frontend payload expectations
HYMNS_DATABASE = [
    {
        "number": "1",
        "title": "Ho, Every One That Thirsteth",
        "page": "5",
        "prev_hymn": None,
        "next_hymn": "2",
        "audio": {"Soprano": "hymn1_sop.mp3", "Alto": "hymn1_alt.mp3"}
    },
    {
        "number": "2",
        "title": "Grace Greater than Our Sin",
        "page": "6",
        "prev_hymn": "1",
        "next_hymn": "3",
        "audio": {"Full Mix": "hymn2_full.mp3"}
    },
    {
        "number": "23",
        "title": "The Lord's My Shepherd",
        "page": "25",
        "prev_hymn": "22",
        "next_hymn": "24",
        "audio": {"Tenor": "hymn23_ten.mp3", "Bass": "hymn23_bas.mp3"}
    }
]

def cleanup_old_setlists():
    """Removes setlists that are older than 4 weeks (28 days)"""
    now = datetime.now()
    four_weeks_ago = now - timedelta(days=28)
    
    to_delete = []
    for key_str in list(setlists_db.keys()):
        try:
            # Handle standard composite formats gracefully
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
        "message": "Welcome to the Sankey Hymnal Dashboard",
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
        # Match against number or against title text strings safely
        if query == str(hymn["number"]).lower() or query in hymn["title"].lower():
            matched_results.append(hymn)

    # Return raw array directly to match frontend parsing architecture expectations
    return jsonify(matched_results)

if __name__ == '__main__':
    app.run(debug=True, port=10000)
