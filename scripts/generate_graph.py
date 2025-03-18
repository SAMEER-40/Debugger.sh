import json
import networkx as nx

LOG_FILE = "mutex_log.txt"
OUTPUT_JSON = "lock_graph.json"

def parse_log():
    edges = []
    nodes = set()
    lock_states = {}  # Track which thread is holding a lock

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = line.strip().split()
            
            if "Locking mutex" in line:
                timestamp = parts[0]  # Assuming log format: [timestamp] Locking mutex <id> by thread <id>
                thread_id = parts[3]
                mutex_id = parts[-1]

                edges.append({"source": thread_id, "target": mutex_id, "timestamp": timestamp})
                nodes.update([thread_id, mutex_id])
                lock_states[mutex_id] = thread_id  # Mark lock as held by thread
            
            elif "Unlocking mutex" in line:
                mutex_id = parts[-1]
                if mutex_id in lock_states:
                    del lock_states[mutex_id]  # Mark lock as released

    return edges, nodes

def detect_deadlocks(graph):
    """Detect circular dependencies indicating a deadlock"""
    try:
        cycle = nx.find_cycle(graph, orientation="original")
        return cycle  # Returns a list of edges forming the cycle
    except nx.NetworkXNoCycle:
        return None  # No deadlock

def generate_json():
    graph = nx.DiGraph()
    edges, nodes = parse_log()

    for edge in edges:
        graph.add_edge(edge["source"], edge["target"], timestamp=edge["timestamp"])

    # Convert to D3.js JSON format
    json_graph = {
        "nodes": [{"id": node, "type": "thread" if "thread" in node else "lock"} for node in nodes],
        "links": [{"source": e["source"], "target": e["target"], "timestamp": e["timestamp"]} for e in edges],
        "deadlocks": detect_deadlocks(graph)
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(json_graph, f, indent=4)

    print(f"✅ Graph saved as {OUTPUT_JSON}")

if __name__ == "__main__":
    generate_json()
