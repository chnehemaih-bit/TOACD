import http.server
import socketserver
import urllib.parse
import subprocess
import json
import os
import sys
import time
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import agentic_engine

# Lazy-import analysis modules (graceful degradation if missing)
try:
    from lexer import MASTER_REGEX, CPP_KEYWORDS
    _LEXER_OK = True
except Exception:
    _LEXER_OK = False

try:
    from cpp_parser import build_ast
    _PARSER_OK = True
except Exception:
    _PARSER_OK = False

try:
    from semantic_analyzer import SemanticAnalyzer
    _SEMANTIC_OK = True
except Exception:
    _SEMANTIC_OK = False


def _tokenize_string(code_str):
    """Tokenize a raw code string in-memory (mirrors lexer.tokenize_file logic)."""
    tokens = []
    if not _LEXER_OK:
        return tokens
    token_index = 0
    line = 1
    line_start = 0
    for mo in MASTER_REGEX.finditer(code_str):
        kind = mo.lastgroup
        value = mo.group()
        col = mo.start() - line_start + 1
        if kind == "COMMENT":
            line += value.count('\n')
            continue
        if kind == "NEWLINE":
            line += 1
            line_start = mo.end()
            continue
        if kind == "WHITESPACE":
            continue
        if kind == "IDENTIFIER" and value in CPP_KEYWORDS:
            kind = "KEYWORD"
        tokens.append({"token_index": token_index, "token_type": kind,
                        "token_value": value, "line": line, "column": col})
        token_index += 1
    return tokens


def _ast_to_json(node):
    """Recursively convert ASTNode to a JSON-serialisable dict."""
    if node is None:
        return None
    return {
        "node_type": node.node_type,
        "value": node.value,
        "line": node.line,
        "children": [_ast_to_json(c) for c in node.children if c is not None],
    }


def _collect_errors(node, errors=None):
    """Walk AST and collect all ErrorNode entries."""
    if errors is None:
        errors = []
    if node is None:
        return errors
    if node.node_type == "ErrorNode":
        errors.append({
            "type": node.value,
            "message": f"{node.value.replace('_', ' ').title()} detected",
            "line": node.line,
            "column": 0,
            "severity": "ERROR",
            "snippet": "",
        })
    for child in node.children:
        _collect_errors(child, errors)
    return errors

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

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
        if self.path == '/' or self.path == '/index.html':
            # Always serve fresh — no cache
            try:
                f = open(os.path.join(SCRIPT_DIR, 'index.html'), 'rb')
                content = f.read(); f.close()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.end_headers()
                self.wfile.write(content)
                return
            except Exception as e:
                self.send_error(500, str(e)); return
        elif self.path == '/performance':
            self.path = '/performance.html'
        elif self.path == '/presentation':
            self.path = '/presentation.html'
        elif self.path == '/performance-data':
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
                
                valid_flags = [arg for arg in args[1:] if arg in ('--self-heal', '--agentic')]
                self_heal = '--self-heal' in valid_flags
                is_agentic = '--agentic' in valid_flags
                
                if is_agentic:
                    # Run full Agentic AI Pipeline
                    try:
                        res = agentic_engine.run_agentic_pipeline(actual_filename)
                        fixed_name = actual_filename.replace('.cpp', '.fixed.cpp')
                        with open(fixed_name, 'w', encoding='utf-8') as f:
                            f.write(res["repair"]["healed_code"])
                        
                        agent_lines = [
                            "=" * 60,
                            "  🤖 AGENTIC AI AUTONOMOUS REPAIR & AUDIT ENGINE",
                            "=" * 60,
                            f"File Target: {actual_filename}",
                            f"ML Class   : {res['ml_error_type']} (Confidence: {res['confidence']}%)",
                            "",
                            "--- AGENT REASONING & REFLECTION TRAIL ---"
                        ]
                        for t in res["repair"]["thoughts"]:
                            agent_lines.append(f"[{t['timestamp']}] Turn {t['turn']} | {t['phase']}: {t['message']}")
                        
                        agent_lines.extend([
                            "",
                            "--- 🍃 GREEN COMPUTING & ENERGY PROFILER ---",
                            f"Eco-Grade         : {res['green_computing']['eco_grade']} ({res['green_computing']['eco_status']})",
                            f"Time Complexity   : {res['green_computing']['time_complexity']}",
                            f"Est. CPU Cycles   : {res['green_computing']['estimated_cpu_cycles']:,}",
                            f"Energy per Exec   : {res['green_computing']['energy_microjoules']} µJ",
                            f"Carbon (10M runs) : {res['green_computing']['carbon_gco2_per_10m']} gCO2e",
                            "Optimization Tips :",
                        ])
                        for tip in res['green_computing']['recommendations']:
                            agent_lines.append(f"  • {tip}")
                        
                        agent_lines.extend([
                            "",
                            "--- 🛡️ CYBERSECURITY THREAT DEFENSE ---",
                            f"Threat Severity   : {res['security_shield']['overall_threat']} (Security Score: {res['security_shield']['security_score']}/100)",
                            f"Vulnerabilities   : {res['security_shield']['vulnerabilities_found']} detected",
                        ])
                        for v in res['security_shield']['vulnerabilities']:
                            agent_lines.append(f"  • [{v['severity']}] {v['id']} ({v['name']}) at line {v['line']}")
                            agent_lines.append(f"    Exploit: {v['exploit']}")
                        
                        agent_lines.extend([
                            "",
                            f"✅ AUTONOMOUS REPAIR COMPLETE — Healed file saved to: {fixed_name}",
                            "=" * 60
                        ])
                        output = "\n".join(agent_lines)
                    except Exception as e:
                        output = f"Agentic AI Engine Error: {str(e)}"
                else:
                    # Run the prediction script
                    try:
                        result = subprocess.run(
                            [sys.executable, 'predict.py', actual_filename] + valid_flags,
                            capture_output=True,
                            text=True,
                            encoding='utf-8',
                            errors='replace',
                            check=True
                        )
                        output = result.stdout
                    except subprocess.CalledProcessError as e:
                        output = e.stdout + "\n" + e.stderr
                    except Exception as e:
                        output = str(e)
                
                # Extract performance metrics from output and store them
                perf_entry = extract_performance_from_output(output, actual_filename, self_heal or is_agentic)
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
        elif self.path == '/agentic-run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                filename = data.get('filename', '').strip()
                code = data.get('code', None)
                
                for prefix in ['python3 predict.py ', 'python predict.py ']:
                    if filename.startswith(prefix):
                        filename = filename[len(prefix):].strip()
                filename = filename.split()[0] if filename else 'test1.cpp'

                if code and code.strip():
                    target = code.strip()
                    filename = filename if filename and filename.endswith('.cpp') else 'custom_input.cpp'
                    filepath = os.path.join('.', filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(target)
                else:
                    filepath = os.path.join('.', filename)
                    if not os.path.exists(filepath):
                        self._send_json({"error": f"File '{filename}' not found."})
                        return
                    target = filepath

                res = agentic_engine.run_agentic_pipeline(target)
                
                # Save healed file
                if res.get("repair", {}).get("healed_code"):
                    fixed_name = filename.replace('.cpp', '.fixed.cpp')
                    with open(fixed_name, 'w', encoding='utf-8') as f:
                        f.write(res["repair"]["healed_code"])

                self._send_json(res)
            except Exception as e:
                self._send_json({"error": str(e)})

        elif self.path == '/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8-sig', errors='replace'))
                code = data.get('code', '')
                source_lines = code.splitlines()

                # ── 1. Lexical analysis ───────────────────────────────────────
                tokens = _tokenize_string(code)
                counts = {"total": len(tokens), "keywords": 0, "identifiers": 0,
                          "operators": 0, "literals": 0, "punctuation": 0, "unknown": 0}
                for t in tokens:
                    tt = t["token_type"]
                    if tt == "KEYWORD":          counts["keywords"]    += 1
                    elif tt == "IDENTIFIER":     counts["identifiers"] += 1
                    elif tt == "OPERATOR":       counts["operators"]   += 1
                    elif tt in ("INTEGER","FLOAT","STRING","CHAR"): counts["literals"] += 1
                    elif tt in ("SEMICOLON","OPEN_PAREN","CLOSE_PAREN",
                                "OPEN_BRACE","CLOSE_BRACE","OPEN_BRACKET",
                                "CLOSE_BRACKET","HASH"):            counts["punctuation"] += 1
                    elif tt == "UNKNOWN":        counts["unknown"]     += 1

                # ── 2. Syntax / AST analysis ──────────────────────────────────
                ast_root = None
                syntax_errors = []
                ast_json = {}
                if _PARSER_OK:
                    try:
                        ast_root, parse_errors = build_ast(tokens if tokens else code)
                        ast_json = _ast_to_json(ast_root) or {}
                        syntax_errors = _collect_errors(ast_root)
                        # Also surface parse_errors strings
                        seen_lines = {e["line"] for e in syntax_errors}
                        for pe in (parse_errors or []):
                            m = re.search(r'line\s+(\d+)', str(pe))
                            ln = int(m.group(1)) if m else 0
                            snippet = source_lines[ln-1].strip() if 1<=ln<=len(source_lines) else ""
                            etype = "MISSING_SEMICOLON" if "semicolon" in str(pe).lower() else \
                                    "UNMATCHED_BRACE" if "brace" in str(pe).lower() else \
                                    "SYNTAX_ERROR"
                            if ln not in seen_lines:
                                syntax_errors.append({"type": etype,
                                    "message": str(pe), "line": ln,
                                    "column": 0, "severity": "ERROR",
                                    "snippet": snippet})
                                seen_lines.add(ln)
                        # Fill in snippets
                        for e in syntax_errors:
                            if not e.get("snippet") and 1<=e.get("line",0)<=len(source_lines):
                                e["snippet"] = source_lines[e["line"]-1].strip()
                    except Exception as pe:
                        syntax_errors.append({"type": "PARSE_ERROR",
                            "message": str(pe), "line": 0, "column": 0,
                            "severity": "ERROR", "snippet": ""})

                # ── 3. Semantic analysis ──────────────────────────────────────
                semantic_issues = []
                symbol_table   = []
                scope_summary  = {}
                if _SEMANTIC_OK and ast_root is not None:
                    try:
                        sem = SemanticAnalyzer()
                        sem_result = sem.analyze(ast_root, tokens, source_lines)
                        semantic_issues = sem_result.get("issues", [])
                        symbol_table    = sem_result.get("symbol_table", [])
                        scope_summary   = sem_result.get("scope_summary", {})
                    except Exception as se:
                        semantic_issues = [{"severity": "INFO",
                            "type": "Analyzer Error", "message": str(se),
                            "line": 0, "column": 0, "snippet": "", "suggestion": ""}]

                grammar_productions = [
                    "Program → Declaration*",
                    "Declaration → FunctionDecl | VarDecl | ClassDecl | NamespaceDecl",
                    "FunctionDecl → Type Identifier '(' Params ')' CompoundStmt",
                    "VarDecl → Type Identifier ['=' Expr] ';'",
                    "CompoundStmt → '{' Statement* '}'",
                    "Statement → VarDecl | ExprStmt | ReturnStmt | IfStmt | WhileStmt | ForStmt",
                    "ExprStmt → Expr ';'",
                    "ReturnStmt → 'return' Expr ';'",
                    "IfStmt → 'if' '(' Expr ')' Statement ['else' Statement]",
                    "WhileStmt → 'while' '(' Expr ')' Statement",
                    "ForStmt → 'for' '(' Expr ';' Expr ';' Expr ')' Statement",
                    "Expr → Expr BinOp Expr | UnaryOp Expr | Identifier | Literal | FuncCall",
                ]

                self._send_json({
                    "tokens":              tokens,
                    "token_summary":       counts,
                    "syntax_errors":       syntax_errors,
                    "has_errors":          len(syntax_errors) > 0,
                    "ast_json":            ast_json,
                    "semantic_issues":     semantic_issues,
                    "symbol_table":        symbol_table,
                    "scope_summary":       scope_summary,
                    "grammar_productions": grammar_productions,
                })
            except Exception as e:
                self._send_json({"error": str(e)})

        elif self.path == '/optimize':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                from agentic_engine import CodeOptimizer
                data   = json.loads(post_data.decode('utf-8-sig', errors='replace'))
                code   = data.get('code', '')
                result = CodeOptimizer.optimize(code)
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)})

        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, response_dict):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_dict).encode('utf-8'))

if __name__ == "__main__":
    load_stored_data()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), TerminalUIHandler) as httpd:
        print(f"Serving terminal UI at http://localhost:{PORT}")
        print(f"Performance dashboard at http://localhost:{PORT}/performance")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
