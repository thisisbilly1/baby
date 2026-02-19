from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder='frontend/dist')
CORS(app)

DATABASE = 'baby_tracker.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with tables"""
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS diapers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT NOT NULL CHECK(type IN ('pee', 'poop', 'both'))
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS feedings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL
        )
    ''')
    db.commit()
    db.close()

# API Routes for Diapers
@app.route('/api/diapers', methods=['GET', 'POST'])
def diapers():
    db = get_db()
    
    if request.method == 'POST':
        data = request.json
        diaper_type = data.get('type')
        
        if diaper_type not in ['pee', 'poop', 'both']:
            return jsonify({'error': 'Invalid diaper type'}), 400
        
        cursor = db.execute(
            'INSERT INTO diapers (type) VALUES (?)',
            (diaper_type,)
        )
        db.commit()
        
        return jsonify({
            'id': cursor.lastrowid,
            'type': diaper_type,
            'timestamp': datetime.now().isoformat()
        }), 201
    
    else:  # GET
        limit = request.args.get('limit', 50, type=int)
        diapers = db.execute(
            'SELECT * FROM diapers ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        ).fetchall()
        
        return jsonify([dict(row) for row in diapers])

@app.route('/api/diapers/<int:diaper_id>', methods=['GET', 'DELETE'])
def diaper_detail(diaper_id):
    db = get_db()
    
    if request.method == 'DELETE':
        db.execute('DELETE FROM diapers WHERE id = ?', (diaper_id,))
        db.commit()
        return '', 204
    
    else:  # GET
        diaper = db.execute('SELECT * FROM diapers WHERE id = ?', (diaper_id,)).fetchone()
        if diaper is None:
            return jsonify({'error': 'Diaper not found'}), 404
        return jsonify(dict(diaper))

# API Routes for Feedings
@app.route('/api/feedings', methods=['GET', 'POST'])
def feedings():
    db = get_db()
    
    if request.method == 'POST':
        data = request.json
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if not start_time or not end_time:
            return jsonify({'error': 'start_time and end_time are required'}), 400
        
        cursor = db.execute(
            'INSERT INTO feedings (start_time, end_time) VALUES (?, ?)',
            (start_time, end_time)
        )
        db.commit()
        
        return jsonify({
            'id': cursor.lastrowid,
            'start_time': start_time,
            'end_time': end_time
        }), 201
    
    else:  # GET
        limit = request.args.get('limit', 50, type=int)
        feedings = db.execute(
            'SELECT * FROM feedings ORDER BY start_time DESC LIMIT ?',
            (limit,)
        ).fetchall()
        
        return jsonify([dict(row) for row in feedings])

@app.route('/api/feedings/<int:feeding_id>', methods=['GET', 'DELETE'])
def feeding_detail(feeding_id):
    db = get_db()
    
    if request.method == 'DELETE':
        db.execute('DELETE FROM feedings WHERE id = ?', (feeding_id,))
        db.commit()
        return '', 204
    
    else:  # GET
        feeding = db.execute('SELECT * FROM feedings WHERE id = ?', (feeding_id,)).fetchone()
        if feeding is None:
            return jsonify({'error': 'Feeding not found'}), 404
        return jsonify(dict(feeding))

# Serve Frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    dist_dir = os.path.join(app.static_folder)
    
    # Check if dist directory exists
    if not os.path.exists(dist_dir):
        return jsonify({
            'message': 'Frontend not built yet. Run: cd frontend && npm run build'
        }), 404
    
    # If path exists, serve it
    if path and os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    
    # Otherwise serve index.html (SPA fallback)
    index_path = os.path.join(dist_dir, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(dist_dir, 'index.html')
    
    return jsonify({
        'message': 'Frontend not built yet. Run: cd frontend && npm run build'
    }), 404

if __name__ == '__main__':
    init_db()
    print("🍼 Baby tracker server starting...")
    print("📊 API available at http://localhost:5000/api")
    print("🌐 Frontend will be served at http://localhost:5000")
    app.run(debug=True, port=5000)