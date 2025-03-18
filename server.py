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

LOCK_GRAPH_FILE = "lock_graph.json"

def read_graph():
    """Reads and returns the lock graph JSON file safely."""
    try:
        if os.path.exists(LOCK_GRAPH_FILE):
            with open(LOCK_GRAPH_FILE, "r") as f:
                return json.load(f)
        else:
            return {"nodes": [], "links": [], "deadlocks": []}  # Ensure deadlocks field exists
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {LOCK_GRAPH_FILE}: {e}")
        return {"nodes": [], "links": [], "deadlocks": []}

@app.route("/graph")
def get_graph():
    """API endpoint to fetch the current graph."""
    return jsonify(read_graph())

@socketio.on("connect")
def handle_connect():
    """Handles a new client connection."""
    print("Client connected:", request.sid)
    socketio.emit("update_graph", read_graph())  # Send latest graph upon connection

def send_updates():
    """Continuously sends graph updates to all clients every 2 seconds."""
    while True:
        data = read_graph()
        socketio.emit("update_graph", data)
        time.sleep(2)

if __name__ == "__main__":
    update_thread = threading.Thread(target=send_updates, daemon=True)
    update_thread.start()
    socketio.run(app, debug=True, port=8080, host="0.0.0.0")
