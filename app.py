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
            battery TEXT,
            android_version TEXT,
            connection_type TEXT,
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

@app.route('/api/device-status', methods=['GET', 'POST'])
def device_status():
    if request.method == 'POST':
        data = request.json or {}
        device_id = data.get('device_id', 'Android Cihaz')
        status = data.get('status', 'online')
        battery = data.get('battery', '%85')
        android_version = data.get('android_version', '13')
        connection_type = data.get('connection_type', 'Wi-Fi')

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO devices (device_id, status, battery, android_version, connection_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (device_id, status, battery, android_version, connection_type))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Status received"}), 200
    return jsonify({"status": "info", "message": "Use POST to send device status"}), 200

@app.route('/api/notifications', methods=['GET', 'POST'])
def receive_notification():
    if request.method == 'POST':
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
        return jsonify({"status": "success", "message": "Notification logged"}), 200
    return jsonify({"status": "info", "message": "Use POST to send notifications"}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT device_id, status, battery, android_version, connection_type, timestamp FROM devices ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    
    device_data = {}
    if row:
        device_data = {
            'device_id': row[0],
            'status': row[1],
            'battery': row[2],
            'android_version': row[3],
            'connection_type': row[4],
            'timestamp': row[5]
        }

    cursor.execute('SELECT package_name, title, text, timestamp FROM notifications ORDER BY id DESC LIMIT 20')
    notifications = [{'package_name': row[0], 'title': row[1], 'text': row[2], 'timestamp': row[3]} for row in cursor.fetchall()]

    conn.close()
    return jsonify({'device': device_data, 'devices': [device_data] if device_data else [], 'notifications': notifications}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
