from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(filename='server.log', level=logging.INFO)

@app.route('/api/device-status', methods=['POST'])
def device_status():
    data = request.json
    print("Cihaz Durumu Alindi:", data)
    app.logger.info(f"Status: {data}")
    return jsonify({"status": "success", "message": "Status received"}), 200

@app.route('/api/notifications', methods=['POST'])
def receive_notification():
    data = request.json
    print("YENI BILDIRIM GELDI:", data)
    app.logger.info(f"Notification: {data}")
    return jsonify({"status": "success", "message": "Notification logged"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
