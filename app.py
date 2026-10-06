import sqlite3
import logging
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

logging.basicConfig(filename='server.log', level=logging.INFO)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_name TEXT,
            title TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def panel():
    return render_template('index.html')

@app.route('/device-status', methods=['POST'])

@app.route('/api/device-status', methods=['POST'])
def device_status():
    data = request.json or {}
    device_id = data.get('device_id', 'unknown')
    status = data.get('status', 'online')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO devices (device_id, status) VALUES (?, ?)', (device_id, status))
    conn.commit()
    conn.close()
    
    app.logger.info(f"Status saved: {data}")
    return jsonify({"status": "success", "message": "Status received"}), 200

@app.route('/notifications', methods=['POST'])
@app.route('/api/notifications', methods=['POST'])
def receive_notification():
    data = request.json or {}
    package_name = data.get('package_name', '')
    title = data.get('title', '')
    text = data.get('text', '')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notifications (package_name, title, text) VALUES (?, ?, ?)',
        (package_name, title, text)
    )
    conn.commit()
    conn.close()

    app.logger.info(f"Notification saved: {data}")
    return jsonify({"status": "success", "message": "Notification logged"}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT device_id, status, timestamp '
        'FROM devices ORDER BY id DESC LIMIT 10'
    )
    devices = [
        {'device_id': row[0], 'status': row[1], 'timestamp': row[2]}
        for row in cursor.fetchall()
    ]

    cursor.execute(
        'SELECT package_name, title, text, timestamp '
        'FROM notifications '
        'ORDER BY id DESC LIMIT 20'
    )
    notifications = [
        {'package_name': row[0], 'title': row[1], 'text': row[2], 'timestamp': row[3]}
        for row in cursor.fetchall()
    ]

    conn.close()

    return jsonify({
        'devices': devices,
        'notifications': notifications
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
