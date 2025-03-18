from flask import Flask, jsonify
from flask_socketio import SocketIO
import json
import time
import threading
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def read_graph():
    try:
        if os.path.exists("lock_graph.json"):
            with open("lock_graph.json", "r") as f:
                return json.load(f)
        else:
            return {"nodes": [], "links": []}
    except json.JSONDecodeError:
        print("Error reading lock_graph.json! File might be incomplete.")
        return {"nodes": [], "links": []}

@app.route("/graph")
def get_graph():
    return jsonify(read_graph())

@socketio.on("connect")
def handle_connect():
    print("Client connected")

def send_updates():
    while True:
        socketio.emit("update_graph", read_graph())
        time.sleep(2)

if __name__ == "__main__":
    update_thread = threading.Thread(target=send_updates, daemon=True)
    update_thread.start()
    socketio.run(app, debug=True, port=8080)
