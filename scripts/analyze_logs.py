
from flask import Flask, request, jsonify
import openai  # If using OpenAI API

app = Flask(__name__)

openai.api_key = "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"

@app.route("/analyze", methods=["POST"])
def analyze_graph():
    data = request.json  # Get graph data
    nodes = data.get("nodes", [])
    links = data.get("links", [])
    
    # Basic Analysis
    issues = []
    for link in links:
        if link.get("type") == "race_condition":
            issues.append(f"Potential race condition between {link['source']} and {link['target']}.")
        elif link.get("type") == "waiting":
            issues.append(f"Thread {link['source']} is waiting on {link['target']}. Possible deadlock risk.")

    # **AI-Powered Analysis**
    ai_prompt = f"Analyze this concurrency graph and suggest optimizations:\nNodes: {nodes}\nLinks: {links}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[{"role": "user", "content": ai_prompt}]
    )

    ai_suggestion = response["choices"][0]["message"]["content"]
    
    return jsonify({"issues": issues, "ai_suggestion": ai_suggestion})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
