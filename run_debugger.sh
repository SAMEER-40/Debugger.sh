#!/bin/bash

# Step 1: Compile the mutex hook
echo "🔧 Compiling mutex hook..."
gcc -o mutex_hook.so src/instrumentation/user_hooks.c -shared -fPIC -ldl -pthread -lrt || { echo "❌ Compilation failed!"; exit 1; }

# Step 2: Remove old logs & images
echo "🧹 Cleaning up old logs..."
rm -rf mutex_log.txt lock_graph.json

# Step 3: Run the test program with LD_PRELOAD
echo "🚀 Running test program with mutex tracking..."
LD_PRELOAD=./mutex_hook.so ./tests/test_mutex &

# Step 4: Wait for logs to be generated
sleep 2  # Adjust if needed for your program

# Step 5: Generate the graph
echo "📊 Generating lock dependency graph..."
python3 scripts/generate_graph.py || { echo "❌ Graph generation failed!"; exit 1; }

# Step 6: Start the Flask web server (using server.py)
echo "🌐 Starting visualization server..."
fuser -k 8080/tcp || true  # Kill any existing server on port 8080
python3 server.py &> server.log &  # Run Flask server and log output

# Step 7: Wait for the server to start
sleep 3  # Ensures the server is running before opening the browser

# Step 8: Open the visualization in the browser
xdg-open file:///home/SaM/Desktop/concurrency-debugger/Frontend/index.html || open file:///home/SaM/Desktop/concurrency-debugger/Frontend/index.html  # Linux/macOS

echo "✅ Done! Check your browser for the visualization."
