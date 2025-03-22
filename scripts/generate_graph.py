import json
import networkx as nx

LOG_FILE = "mutex_log.txt"
OUTPUT_JSON = "lock_graph.json"

def parse_log():
    edges = []
    nodes = set()
    lock_owners = {}  # Maps mutex -> thread that owns it

    with open(LOG_FILE, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 5:
                continue  # Ignore malformed lines

            if "Locking" in line:
                mutex_id = parts[2]  # "Locking mutex X"
                thread_id = parts[-1]  # "by thread Y"

                nodes.update([thread_id, mutex_id])
                
                # Track lock dependency
                if mutex_id in lock_owners:
                    edges.append({"source": lock_owners[mutex_id], "target": thread_id})  # Thread dependency
                
                lock_owners[mutex_id] = thread_id  # Mark mutex as owned by thread

            elif "Unlocking" in line:
                mutex_id = parts[2]
                if mutex_id in lock_owners:
                    del lock_owners[mutex_id]  # Remove ownership on unlock

    return edges, nodes

def detect_deadlocks(graph):
    """Detect cycles (deadlocks) in the dependency graph."""
    try:
        cycle = nx.find_cycle(graph, orientation="original")
        return [{"source": u, "target": v} for u, v, _ in cycle]  # Return cycle edges
    except nx.NetworkXNoCycle:
        return None  # No deadlock

def generate_json():
    graph = nx.DiGraph()
    edges, nodes = parse_log()

    for edge in edges:
        graph.add_edge(edge["source"], edge["target"])

    # Convert to JSON format
    json_graph = {
        "nodes": [{"id": node, "type": "thread" if node.isdigit() else "lock"} for node in nodes],
        "links": [{"source": e["source"], "target": e["target"]} for e in edges],
        "deadlocks": detect_deadlocks(graph)  # Detect and include deadlock cycles
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(json_graph, f, indent=4)

    print(f"✅ Graph saved as {OUTPUT_JSON}")
    if json_graph["deadlocks"]:
        print("❌ Deadlock detected!")
    else:
        print("✅ No deadlock detected.")

if __name__ == "__main__":
    generate_json()
