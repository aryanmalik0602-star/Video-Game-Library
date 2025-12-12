import json
import os
import csv
from flask import Flask, jsonify, request

app = Flask(__name__)

# NEW ROBUST PATHING
# This finds the root directory of the project, two levels up from server.py's location
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data') # This is the correct relative path to the data folder

# Define file paths relative to the data folder
DATA_FILE = os.path.join(DATA_FOLDER, 'library_data.json')
CSV_FILE = os.path.join(DATA_FOLDER, 'video_games.csv')

def load_data():
    if not os.path.exists(DATA_FILE):
        if os.path.exists(CSV_FILE):
            print(">> SYSTEM: Importing data from video_games.csv...")
            import_csv_data()
        else:
            return {}     
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def import_csv_data():
    data = {}
    try:
        with open(CSV_FILE, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                name = row.get('name', 'Unknown').strip()
                platform = row.get('platform', 'General').strip()
                date = row.get('release_date', 'Unknown').strip()
                rating = row.get('user_review', 'N/A').strip()
                
                key = f"{name} ({platform})"
                data[key] = {
                    "name": name,
                    "author": "See Summary",
                    "publisher": f"User Rating: {rating}",
                    "date": date,
                    "category": platform
                }
                count += 1
                if count >= 800: # Increased limit slightly
                    break
        save_data(data)
    except Exception as e:
        print(f">> ERROR: {e}")

# --- ROUTES ---

@app.route('/', methods=['GET'])
def home_root():
    return "<h1>NEON LIBRARY BACKEND ONLINE</h1>"

@app.route('/media', methods=['GET'])
def get_all_media():
    data = load_data()
    return jsonify(list(data.values()))

@app.route('/media/category/<category>', methods=['GET'])
def get_media_by_category(category):
    data = load_data()
    filtered = [item for item in data.values() if item.get('category') == category]
    return jsonify(filtered)

# UPDATED SEARCH: Returns a LIST of matches now
@app.route('/media/search/<name>', methods=['GET'])
def search_media(name):
    data = load_data()
    matches = []
    # Check for partial match in name (case-insensitive)
    for item in data.values():
        if name.lower() in item['name'].lower():
            matches.append(item)
    
    # Return list (even if empty) to avoid 404 errors during typing
    return jsonify(matches)

@app.route('/media/item/<name>', methods=['GET'])
def get_media_item(name):
    data = load_data()
    # Exact match lookup
    for item in data.values():
        if item['name'] == name:
            return jsonify(item)
    return jsonify({"error": "Not found"}), 404

@app.route('/media', methods=['POST'])
def create_media():
    new_item = request.json
    name = new_item.get('name')
    if not name: return jsonify({"error": "Name required"}), 400
    data = load_data()
    data[name] = new_item
    save_data(data)
    return jsonify({"message": "Created"}), 201

@app.route('/media/<name>', methods=['DELETE'])
def delete_media(name):
    data = load_data()
    target_key = None
    for key, item in data.items():
        if item['name'] == name:
            target_key = key
            break
    if target_key:
        del data[target_key]
        save_data(data)
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "Not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)