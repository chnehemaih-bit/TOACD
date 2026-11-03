import http.server
import socketserver
import urllib.parse
import subprocess
import json
import os
import time

PORT = 8000

# In-memory performance data store (persists across requests while server is running)
PERFORMANCE_STORE = {
    "history": [],          # List of per-run results
    "summary": {
        "total_runs": 0,
        "total_errors": 0,
        "avg_confidence": 0,
        "avg_detection_time": 0,
        "fixes_applied": 0,
        "successful_compilations": 0,
    }
}

# Path to the JSON file that persists data across server restarts
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "performance_data.json")


def load_stored_data():
    """Load performance data from disk if it exists."""
    global PERFORMANCE_STORE
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                PERFORMANCE_STORE = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # Start fresh if file is corrupt


def save_stored_data():
    """Persist performance data to disk."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(PERFORMANCE_STORE, f, indent=2)
    except IOError:
        pass


def get_file_stats():
    """Analyze all .cpp test files and categorize by complexity."""
    stats = {}
    for f in os.listdir('.'):
        if f.endswith('.cpp') and not f.endswith('.fixed.cpp'):
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                    lines = content.strip().split('\n')
                    line_count = len(lines)
                    # Count non-empty, non-comment lines
                    code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith('//'))
                    # Count control structures
                    controls = sum(1 for l in lines if any(k in l for k in ['if ', 'for ', 'while ', 'switch ', 'class ', 'struct ']))
                    # Complexity heuristic
                    if code_lines <= 8 and controls <= 1:
                        complexity = "simple"
                    elif code_lines <= 20 and controls <= 3:
                        complexity = "medium"
                    else:
                        complexity = "complex"
                    stats[f] = {
                        "lines": line_count,
                        "code_lines": code_lines,
                        "controls": controls,
                        "complexity": complexity
                    }
            except Exception:
                pass
    return stats


def update_summary():
    """Recompute summary statistics from history."""
    history = PERFORMANCE_STORE["history"]
    n = len(history)
    if n == 0:
        return

    PERFORMANCE_STORE["summary"] = {
        "total_runs": n,
        "total_errors": sum(1 for h in history if h.get("error_type")),
        "avg_confidence": sum(h.get("confidence", 0) for h in history) / n,
        "avg_detection_time": sum(h.get("detection_time", 0) for h in history) / n,
        "fixes_applied": sum(1 for h in history if h.get("fix_attempted")),
        "successful_compilations": sum(1 for h in history if h.get("fix_compiled")),
    }


def extract_performance_from_output(output, filename, self_heal=False):
    """Parse the predict.py output to extract performance metrics.
    
    Also looks for a PERF_JSON line that predict.py outputs for structured data.
    """
    entry = {
        "filename": filename,
        "error_type": None,
        "confidence": 0.0,
        "detection_time": 0.0,
        "fix_attempted": self_heal,
        "fix_compiled": False,
        "timestamp": time.time(),
    }

    for line in output.split("\n"):
        line_stripped = line.strip()

        # Check for structured JSON line from predict.py
        if line_stripped.startswith("PERF_JSON:"):
            try:
                perf = json.loads(line_stripped[len("PERF_JSON:"):])
                entry["error_type"] = perf.get("error_type", entry["error_type"])
                entry["confidence"] = perf.get("confidence", entry["confidence"])
                entry["detection_time"] = perf.get("detection_time", entry["detection_time"])
                entry["fix_compiled"] = perf.get("fix_compiled", entry["fix_compiled"])
                entry["fix_attempted"] = perf.get("fix_attempted", entry["fix_attempted"])
                return entry
            except json.JSONDecodeError:
                pass

        # Fallback: parse text output
        if "PREDICTED ERROR TYPE:" in line_stripped:
            entry["error_type"] = line_stripped.split(":")[-1].strip()
        elif "CONFIDENCE:" in line_stripped:
            try:
                entry["confidence"] = float(line_stripped.split(":")[-1].strip().replace("%", ""))
            except ValueError:
                pass
        elif "COMPILE/RUN SUCCESS" in line_stripped:
            entry["fix_compiled"] = True

    return entry


class TerminalUIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/performance':
            self.path = '/performance.html'
        elif self.path == '/performance-data':
            # Enrich response with file complexity stats
            response_data = dict(PERFORMANCE_STORE)
            response_data['file_stats'] = get_file_stats()
            self._send_json(response_data)
            return
        elif self.path == '/performance-clear':
            PERFORMANCE_STORE["history"] = []
            PERFORMANCE_STORE["summary"] = {
                "total_runs": 0, "total_errors": 0,
                "avg_confidence": 0, "avg_detection_time": 0,
                "fixes_applied": 0, "successful_compilations": 0,
            }
            save_stored_data()
            self._send_json({"status": "cleared"})
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == '/run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                filename = data.get('filename', '').strip()
                
                # If the user accidentally types the full command instead of just filename
                if filename.startswith('python3 predict.py '):
                    filename = filename.replace('python3 predict.py ', '').strip()
                elif filename.startswith('python predict.py '):
                    filename = filename.replace('python predict.py ', '').strip()
                
                import shlex
                try:
                    args = shlex.split(filename)
                except ValueError:
                    args = [filename]
                
                if not args:
                    response = {"output": "Error: Please provide a filename.\n"}
                    self._send_json(response)
                    return
                
                actual_filename = args[0]
                
                # Check if file exists to prevent arbitrary command injection issues
                if not os.path.exists(actual_filename):
                    response = {"output": f"Error: File '{actual_filename}' not found in the current directory.\n"}
                    self._send_json(response)
                    return
                
                valid_flags = [arg for arg in args[1:] if arg == '--self-heal']
                self_heal = '--self-heal' in valid_flags
                
                # Run the prediction script
                try:
                    result = subprocess.run(
                        ['python3', 'predict.py', actual_filename] + valid_flags,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    output = result.stdout
                except subprocess.CalledProcessError as e:
                    output = e.stdout + "\n" + e.stderr
                except Exception as e:
                    output = str(e)
                
                # Extract performance metrics from output and store them
                perf_entry = extract_performance_from_output(output, actual_filename, self_heal)
                PERFORMANCE_STORE["history"].append(perf_entry)
                update_summary()
                save_stored_data()

                # Strip the PERF_JSON line from user-visible output
                clean_output = "\n".join(
                    line for line in output.split("\n")
                    if not line.strip().startswith("PERF_JSON:")
                )

                response = {"output": clean_output}
                self._send_json(response)
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, response_dict):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_dict).encode('utf-8'))

# Load previous data
load_stored_data()

# Allow reusing the address to avoid common Address in use error
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), TerminalUIHandler) as httpd:
    print(f"Serving terminal UI at http://localhost:{PORT}")
    print(f"Performance dashboard at http://localhost:{PORT}/performance")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
