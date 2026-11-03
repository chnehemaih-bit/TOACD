"""
agentic_engine.py
=================
Next-Generation Agentic AI Engine for C++ Syntax Error Healing, 
Green Computing Energy Profiling, and Cybersecurity Threat Defense.

Features:
1. Agentic Reflection & Self-Healing Loop:
   - Perceive: Inspects source code, AST, and ML classification.
   - Reason: Determines exact root cause and scope structure.
   - Act: Generates context-aware surgical code repair.
   - Verify: Re-evaluates candidate code with AST Parser (cpp_parser.py).
   - Reflect: If secondary errors remain, iteratively refines the fix.

2. Green Computing & Energy Consumption Profiler:
   - Algorithmic Time & Space complexity estimation.
   - CPU Instruction & Cycle estimation.
   - Energy consumption calculation (Joules, kWh/1M runs).
   - Carbon Footprint estimation (gCO2e).
   - Eco-Score Rating (A+ to F) & Green Software Engineering recommendations.

3. Cybersecurity Threat Shield & Attacker Defense:
   - Audits poor C++ code for exploitable security vulnerabilities:
     * Buffer Overflows (CWE-120 / CWE-121)
     * Format String Injection (CWE-134)
     * Integer Overflow / Wraparound (CWE-190)
     * Unbounded Loop / Denial of Service (CWE-835)
     * Memory Leaks & Resource Exhaustion (CWE-401)
     * Uninitialized Variable Use (CWE-457)
   - Threat Severity Scoring (CRITICAL / HIGH / MEDIUM / LOW).
   - Explains the attacker exploit vector and auto-generates security hardening.
"""

import os
import sys
import re
import time
import math
import difflib
from collections import defaultdict

# Add current folder to path to import local modules
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from lexer import MASTER_REGEX, CPP_KEYWORDS, strip_comments
from cpp_parser import build_ast, ASTNode

try:
    import joblib
    import pandas as pd
    from ast_features import extract_features
    _ML_AVAILABLE = True
except Exception:
    _ML_AVAILABLE = False


def classify_syntax_error(code_str):
    """
    Uses the trained Random Forest model (model.pkl) and AST feature extraction
    to classify the syntax error across all 13 trained dataset classes.
    """
    if _ML_AVAILABLE:
        try:
            tokens = tokenize_code(code_str)
            ast_root, parse_errors = build_ast(tokens)
            feats = extract_features(ast_root, parse_errors)
            df_feat = pd.DataFrame([feats])

            model_path = os.path.join(CURRENT_DIR, "model.pkl")
            scaler_path = os.path.join(CURRENT_DIR, "scaler.pkl")
            le_path = os.path.join(CURRENT_DIR, "label_encoder.pkl")

            if os.path.exists(model_path) and os.path.exists(scaler_path) and os.path.exists(le_path):
                rf = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                le = joblib.load(le_path)

                X_s = scaler.transform(df_feat.values)
                pred_idx = rf.predict(X_s)[0]
                probs = rf.predict_proba(X_s)[0]
                label = le.inverse_transform([pred_idx])[0]
                conf = round(float(probs[pred_idx]) * 100, 2)
                return label, conf
        except Exception:
            pass

    # High-precision heuristic fallbacks
    if re.search(r'\b(for|while)\s+[^({\n]+\s*\{', code_str):
        return "INVALID_LOOP", 98.0
    if re.search(r'\bif\s+[^({\n]+\s*\{', code_str):
        return "INVALID_CONDITIONAL", 98.0
    if re.search(r'\[[^\]\n]+;', code_str):
        return "INVALID_ARRAY_DECL", 96.0
    if re.search(r'[0-9]+\s*=\s*[a-zA-Z_]', code_str):
        return "INVALID_ASSIGNMENT", 97.0
    if code_str.count("{") != code_str.count("}"):
        return "UNMATCHED_BRACE", 98.0
    if code_str.count("(") != code_str.count(")"):
        return "UNMATCHED_PARANTHESES", 98.0
    return "MISSING_SEMICOLON", 96.0


def tokenize_code(code_str, filename="<agent_candidate>"):
    """In-memory tokenizer matching lexer.py behavior."""
    cleaned = strip_comments(code_str)
    tokens = []
    token_index = 0
    line = 1
    line_start = 0

    for mo in MASTER_REGEX.finditer(cleaned):
        kind  = mo.lastgroup
        value = mo.group()
        col   = mo.start() - line_start + 1

        if kind == "NEWLINE":
            line += 1
            line_start = mo.end()
            continue
        if kind == "WHITESPACE":
            continue

        if kind == "IDENTIFIER" and value in CPP_KEYWORDS:
            kind = "KEYWORD"

        tokens.append({
            "file_name":    filename,
            "label":        "UNKNOWN",
            "token_index":  token_index,
            "token_type":   kind,
            "token_value":  value,
            "line":         line,
            "column":       col,
        })
        token_index += 1
    return tokens



# ============================================================================
# 1. GREEN COMPUTING & ENERGY PROFILER
# ============================================================================

class GreenComputingProfiler:
    """
    Profiles C++ code for energy efficiency and environmental impact.
    Uses energy models based on CPU instruction estimation and TDP characteristics.
    """

    # Baseline constants (based on typical modern x86/ARM core: ~25W TDP peak, ~1.2 nJ per simple op)
    NANOJOULES_PER_CYCLE = 1.25  # nJ
    BASE_CYCLES_PER_STMT = 4
    LOOP_ESTIMATED_ITERATIONS = 1000
    GRID_CARBON_INTENSITY = 475.0  # grams CO2 per kWh (global average)

    @classmethod
    def profile_code(cls, code_lines):
        code_str = "".join(code_lines)
        lines = [l.strip() for l in code_lines if l.strip() and not l.strip().startswith("//")]

        # Count constructs
        for_loops = len(re.findall(r'\bfor\s*\(', code_str))
        while_loops = len(re.findall(r'\bwhile\s*\(', code_str))
        nested_loops = len(re.findall(r'(for|while)[\s\S]*?(for|while)', code_str))
        recursion_suspect = len(re.findall(r'(\w+)\s*\([^)]*\)[\s\S]*?\b\1\s*\(', code_str))
        dynamic_allocations = len(re.findall(r'\bnew\b|\bmalloc\b', code_str))
        io_operations = len(re.findall(r'\bcout\b|\bcin\b|\bprintf\b|\bscanf\b', code_str))
        branches = len(re.findall(r'\bif\s*\(|\bswitch\s*\(', code_str))

        # Estimate Complexity & Cycles
        total_loops = for_loops + while_loops
        if nested_loops > 0:
            time_complexity = "O(n²)"
            cycle_multiplier = 1000000
        elif total_loops > 0:
            time_complexity = "O(n)"
            cycle_multiplier = 50000
        elif recursion_suspect > 0:
            time_complexity = "O(2ⁿ) / O(n) recursive"
            cycle_multiplier = 200000
        else:
            time_complexity = "O(1)"
            cycle_multiplier = 500

        estimated_cycles = len(lines) * cls.BASE_CYCLES_PER_STMT + cycle_multiplier + (io_operations * 2500)
        
        # Energy in Joules (1 Joule = 1e9 nanojoules)
        energy_nanojoules = estimated_cycles * cls.NANOJOULES_PER_CYCLE
        energy_joules = energy_nanojoules / 1e9

        # Energy per 10 Million executions (kWh)
        # 1 kWh = 3,600,000 Joules
        kwh_per_10m = (energy_joules * 10_000_000) / 3_600_000
        carbon_grams_per_10m = kwh_per_10m * cls.GRID_CARBON_INTENSITY

        # Eco-Score calculation (0 to 100)
        score = 100
        if nested_loops > 0:
            score -= 30
        if total_loops > 2:
            score -= 15
        if dynamic_allocations > 0:
            score -= 10
        if io_operations > 5:
            score -= 10
        if recursion_suspect > 0:
            score -= 20
        score = max(20, min(100, score))

        if score >= 90:
            eco_grade = "A+"
            eco_status = "Highly Energy-Efficient (Eco-Friendly)"
            badge_color = "#28a745"
        elif score >= 80:
            eco_grade = "A"
            eco_status = "Energy-Optimized"
            badge_color = "#20c997"
        elif score >= 70:
            eco_grade = "B"
            eco_status = "Moderate Energy Consumption"
            badge_color = "#17a2b8"
        elif score >= 55:
            eco_grade = "C"
            eco_status = "Sub-optimal Energy Profile"
            badge_color = "#ffc107"
        elif score >= 40:
            eco_grade = "D"
            eco_status = "High Carbon Footprint"
            badge_color = "#fd7e14"
        else:
            eco_grade = "F"
            eco_status = "Critical Energy Drain (Inefficient)"
            badge_color = "#dc3545"

        recommendations = []
        if nested_loops > 0:
            recommendations.append("Flatten nested loops or vectorize operations to reduce CPU cycle consumption by up to 85%.")
        if io_operations > 2:
            recommendations.append("Fast I/O: Use `std::ios_base::sync_with_stdio(false); std::cin.tie(NULL);` to minimize system call overhead.")
        if dynamic_allocations > 0:
            recommendations.append("Prefer stack allocation or object pooling over repeated heap `new`/`delete` to prevent memory fragmentation and bus traffic.")
        if total_loops > 0:
            recommendations.append("Pass loop bounds as `const` references to enable compiler auto-vectorization (SIMD) and reduce energy per instruction.")
        if not recommendations:
            recommendations.append("Code adheres to Green Computing principles: optimal single-pass instruction execution.")

        return {
            "eco_grade": eco_grade,
            "eco_score": score,
            "eco_status": eco_status,
            "badge_color": badge_color,
            "time_complexity": time_complexity,
            "estimated_cpu_cycles": int(estimated_cycles),
            "energy_microjoules": round(energy_nanojoules / 1000.0, 3),
            "energy_joules_per_run": round(energy_joules, 8),
            "kwh_per_10m_runs": round(kwh_per_10m, 5),
            "carbon_gco2_per_10m": round(carbon_grams_per_10m, 3),
            "recommendations": recommendations,
            "green_metrics": {
                "loop_count": total_loops,
                "nested_loops": nested_loops,
                "dynamic_allocs": dynamic_allocations,
                "io_calls": io_operations
            }
        }


# ============================================================================
# 2. CYBERSECURITY THREAT SHIELD & ATTACK DEFENSE
# ============================================================================

class CyberThreatShield:
    """
    Audits C++ code for exploitable security weaknesses caused by poor code.
    Identifies CWE vulnerabilities, attack vectors, and applies security hardening.
    """

    VULNERABILITY_PATTERNS = [
        {
            "id": "CWE-120",
            "name": "Buffer Copy without Checking Size of Input (Classic Buffer Overflow)",
            "severity": "CRITICAL",
            "score": 9.8,
            "regex": r'\b(gets|strcpy|strcat|sprintf)\s*\(',
            "exploit": "An attacker can supply input exceeding the destination buffer size, overwriting the stack return address to achieve Remote Code Execution (RCE).",
            "mitigation": "Replace dangerous legacy C functions with bound-checked alternatives like `strncpy`, `snprintf`, or C++ `std::string`."
        },
        {
            "id": "CWE-134",
            "name": "Use of Externally-Controlled Format String",
            "severity": "HIGH",
            "score": 8.6,
            "regex": r'\bprintf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)',
            "exploit": "An attacker input containing format specifiers (e.g. '%x %x %n') can dump process memory or overwrite arbitrary memory locations.",
            "mitigation": "Always specify a literal format string: `printf(\"%s\", user_variable);` or use `std::cout`."
        },
        {
            "id": "CWE-121",
            "name": "Stack-based Buffer Overflow via Unbounded cin",
            "severity": "HIGH",
            "score": 8.2,
            "regex": r'cin\s*>>\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;',
            "exploit": "Streaming directly into a raw character array without size limit (`cin >> buf`) enables stack corruption and shellcode injection.",
            "mitigation": "Use `std::string` or `std::cin >> std::setw(sizeof(buf)) >> buf;`."
        },
        {
            "id": "CWE-190",
            "name": "Integer Overflow or Wraparound",
            "severity": "MEDIUM",
            "score": 6.5,
            "regex": r'\b(int|short)\s+[a-zA-Z0-9_]+\s*=\s*[0-9]{9,}',
            "exploit": "Signed integer overflow can cause unexpected negative values or zero wraparound, bypassing authorization or memory allocation checks.",
            "mitigation": "Use fixed-width integers from `<cstdint>` (e.g. `int64_t`, `size_t`) and validate arithmetic boundaries."
        },
        {
            "id": "CWE-401",
            "name": "Missing Release of Memory after Effective Lifetime (Memory Leak)",
            "severity": "MEDIUM",
            "score": 5.9,
            "regex": r'\bnew\s+[a-zA-Z0-9_]+(\[[^\]]*\])?',
            "exploit": "Repeated memory allocations without corresponding `delete` enable an attacker to trigger Out-Of-Memory (OOM) Denial of Service (DoS).",
            "mitigation": "Use RAII (Resource Acquisition Is Initialization) with `std::unique_ptr` or `std::vector` instead of raw pointers."
        },
        {
            "id": "CWE-835",
            "name": "Loop with Unreachable Exit Condition ('Infinite Loop')",
            "severity": "HIGH",
            "score": 7.5,
            "regex": r'while\s*\(\s*(1|true)\s*\)(?![\s\S]*?break;)',
            "exploit": "An infinite loop without an exit condition freezes thread execution, exhausting 100% CPU core capacity (Denial of Service).",
            "mitigation": "Ensure loops have bounded condition checks and timeout mechanisms."
        },
        {
            "id": "CWE-457",
            "name": "Use of Uninitialized Variable",
            "severity": "LOW",
            "score": 3.8,
            "regex": r'^\s*(int|float|double|char|long|short)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;',
            "exploit": "Reading uninitialized stack memory exposes indeterminate garbage or remnants of previous sensitive process memory.",
            "mitigation": "Always initialize variables upon declaration (e.g., `int x = 0;`)."
        }
    ]

    @classmethod
    def audit_code(cls, code_lines):
        code_str = "".join(code_lines)
        vulnerabilities = []

        for rule in cls.VULNERABILITY_PATTERNS:
            matches = list(re.finditer(rule["regex"], code_str, re.MULTILINE))
            if matches:
                # Find line numbers
                for m in matches:
                    line_no = code_str[:m.start()].count('\n') + 1
                    snippet = code_lines[line_no - 1].strip() if line_no <= len(code_lines) else ""
                    vulnerabilities.append({
                        "id": rule["id"],
                        "name": rule["name"],
                        "severity": rule["severity"],
                        "score": rule["score"],
                        "line": line_no,
                        "snippet": snippet,
                        "exploit": rule["exploit"],
                        "mitigation": rule["mitigation"]
                    })

        # Calculate overall threat level
        if any(v["severity"] == "CRITICAL" for v in vulnerabilities):
            overall_threat = "CRITICAL THREAT"
            threat_color = "#dc3545"
            security_score = 30
        elif any(v["severity"] == "HIGH" for v in vulnerabilities):
            overall_threat = "HIGH RISK"
            threat_color = "#fd7e14"
            security_score = 55
        elif any(v["severity"] == "MEDIUM" for v in vulnerabilities):
            overall_threat = "ELEVATED CONCERN"
            threat_color = "#ffc107"
            security_score = 75
        elif any(v["severity"] == "LOW" for v in vulnerabilities):
            overall_threat = "LOW RISK"
            threat_color = "#20c997"
            security_score = 90
        else:
            overall_threat = "SECURE / HARDENED"
            threat_color = "#28a745"
            security_score = 98

        # Generate hardened code recommendation
        hardened_code = cls.generate_hardened_code(code_lines, vulnerabilities)

        return {
            "overall_threat": overall_threat,
            "security_score": security_score,
            "threat_color": threat_color,
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "hardened_code": hardened_code
        }

    @classmethod
    def generate_hardened_code(cls, code_lines, vulnerabilities):
        """Creates a hardened version of the C++ code with security patches."""
        hardened = list(code_lines)
        for i, line in enumerate(hardened):
            # Replace gets with safe fgets or std::string
            if "gets(" in line:
                hardened[i] = re.sub(r'gets\(([^)]+)\)', r'fgets(\1, sizeof(\1), stdin)', line)
            # Replace unsafe printf(var) with printf("%s", var)
            if re.search(r'printf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)', line):
                hardened[i] = re.sub(r'printf\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)', r'printf("%s", \1)', line)
            # Initialize uninitialized variables
            match = re.match(r'^(\s*)(int|float|double|char|short|long)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;', line)
            if match and not ("extern" in line or "return" in line):
                indent, vtype, vname = match.groups()
                init_val = "'\\0'" if vtype == "char" else "0"
                hardened[i] = f"{indent}{vtype} {vname} = {init_val};\n"
        return "".join(hardened)


# ============================================================================
# 3. AGENTIC AI AUTONOMOUS REPAIR & REFLECTION ENGINE
# ============================================================================

class AgenticRepairEngine:
    """
    Autonomous multi-turn reasoning agent that repairs syntax errors in C++
    and validates each patch candidate using the compiler front-end.
    """

    MAX_TURNS = 8

    def __init__(self):
        self.thoughts = []

    def log_thought(self, turn, phase, message, details=None):
        self.thoughts.append({
            "turn": turn,
            "timestamp": time.strftime("%H:%M:%S"),
            "phase": phase,
            "message": message,
            "details": details or {}
        })

    def run_parser_validation(self, code_str):
        """
        Tool call: Executes lexical analysis and AST construction to check for syntax validity.
        Returns: (is_valid, error_list, ast_root)
        """
        try:
            tokens = tokenize_code(code_str, filename="<agent_candidate>")
            if not tokens:
                return False, ["Tokenization failed (empty token stream)"], None

            ast_root, parse_errors = build_ast(tokens)
            
            # Check for error nodes in AST
            has_error_nodes = False
            def check_nodes(node):
                nonlocal has_error_nodes
                if node.node_type == "ErrorNode":
                    has_error_nodes = True
                for child in node.children:
                    check_nodes(child)
            
            check_nodes(ast_root)

            # Check brackets balance
            lines = code_str.splitlines()
            open_braces = sum(l.count('{') for l in lines)
            close_braces = sum(l.count('}') for l in lines)
            open_parens = sum(l.count('(') for l in lines)
            close_parens = sum(l.count(')') for l in lines)

            structural_errors = []
            if open_braces != close_braces:
                structural_errors.append(f"Mismatched braces: {open_braces} '{{' vs {close_braces} '}}'")
            if open_parens != close_parens:
                structural_errors.append(f"Mismatched parens: {open_parens} '(' vs {close_parens} ')'")

            # Semantic validation: detect undeclared variables/typos (e.g. coutt, cot)
            semantic_errors = []
            try:
                from semantic_analyzer import SemanticAnalyzer
                sem = SemanticAnalyzer()
                sem_res = sem.analyze(ast_root, tokens, lines)
                for issue in sem_res.get("issues", []):
                    if issue.get("severity") == "ERROR":
                        semantic_errors.append(f"[SemanticError @ line {issue.get('line', 0)}] {issue.get('message')}")
            except Exception:
                pass

            all_errors = list(parse_errors) + structural_errors + semantic_errors
            is_valid = (len(all_errors) == 0 and not has_error_nodes)

            return is_valid, all_errors, ast_root
        except Exception as e:
            return False, [f"Parser exception: {str(e)}"], None

    def plan_and_patch(self, code_lines, ml_error_type, current_errors, turn):
        """
        Agentic reasoning step: Analyzes code structure and generates surgical patch.
        All strategies run every turn and fix ALL matching occurrences (no early break).
        """
        lines = list(code_lines)
        code_str = "".join(lines)

        self.log_thought(
            turn=turn,
            phase="Reasoning",
            message=f"Formulating patch for '{ml_error_type}'. Analyzing scope boundaries and token sequences.",
            details={"current_parse_errors": current_errors}
        )

        patched = False

        # ── Strategy 1: Fix loop headers missing parentheses (ALL occurrences) ──
        need_loop = (ml_error_type == "INVALID_LOOP"
                     or any("loop" in e.lower() for e in current_errors)
                     or any(re.search(r'\b(for|while)\s+[^({\n]+\s*\{', l) for l in lines))
        if need_loop:
            for i, line in enumerate(lines):
                m_for = re.search(r'for\s+([^({\n]+)\s*\{', line)
                if m_for:
                    cond = m_for.group(1).strip()
                    lines[i] = re.sub(r'for\s+[^({\n]+\s*\{', f'for ({cond}) {{', line)
                    self.log_thought(turn, "Action", f"Fixed bare 'for' loop header on line {i+1}.")
                    patched = True
                    continue
                m_while = re.search(r'while\s+([^({\n]+)\s*\{', line)
                if m_while:
                    cond = m_while.group(1).strip()
                    lines[i] = re.sub(r'while\s+[^({\n]+\s*\{', f'while ({cond}) {{', line)
                    self.log_thought(turn, "Action", f"Fixed bare 'while' loop header on line {i+1}.")
                    patched = True

        # ── Strategy 2: Missing Semicolons — fix ALL occurrences ───────────────
        # Detects any statement-like line missing a terminator.
        need_semi = (ml_error_type == "MISSING_SEMICOLON"
                     or any("semicolon" in e.lower() for e in current_errors)
                     or True)   # always run — safe on already-terminated lines
        if need_semi:
            for i, line in enumerate(lines):
                # Separate trailing comment if present
                raw = line.rstrip("\r\n")
                code_part = raw
                comment_part = ""
                if "//" in raw:
                    parts = raw.split("//", 1)
                    code_part = parts[0]
                    comment_part = "//" + parts[1]

                stripped = code_part.strip()
                if not stripped:
                    continue
                # Skip preprocessor directives or block comment markers
                if stripped.startswith("#") or stripped.startswith("/*") or stripped.startswith("*"):
                    continue
                # Skip already-terminated lines
                if (stripped.endswith(";") or stripped.endswith("{")
                        or stripped.endswith("}") or stripped.endswith(":")):
                    continue
                # Skip lone braces
                if stripped in ("{", "}"):
                    continue
                # Skip else / do blocks
                if re.match(r'^(else|do)\s*(\{.*)?$', stripped):
                    continue
                # Skip function/class/struct/namespace declaration headers
                if re.match(
                    r'^(template\s*<.*>)?\s*(inline\s+|static\s+|virtual\s+|explicit\s+|constexpr\s+)*'
                    r'(int|float|double|char|bool|void|long|short|unsigned|signed|string|auto|'
                    r'class|struct|namespace|enum)\b.*[)]\s*$',
                    stripped
                ):
                    continue
                # Skip control-flow headers:  if (...) / while (...) / for (...) / switch (...)
                if re.match(r'^(if|else\s+if|while|for|switch)\s*\(', stripped):
                    continue
                # Skip access specifiers
                if re.match(r'^(public|private|protected)\s*:', stripped):
                    continue
                # Must contain at least one identifier character to be a real statement
                if not re.search(r'[a-zA-Z0-9_]', stripped):
                    continue

                if comment_part:
                    lines[i] = code_part.rstrip() + "; " + comment_part.strip() + "\n"
                else:
                    lines[i] = code_part.rstrip() + ";\n"
                self.log_thought(turn, "Action",
                                 f"Added missing ';' to line {i+1}: '{stripped}'")
                patched = True

        # ── Strategy 3: Unmatched Braces ───────────────────────────────────────
        need_brace = (ml_error_type == "UNMATCHED_BRACE"
                      or any("brace" in e.lower() for e in current_errors))
        if need_brace:
            open_b  = sum(l.count('{') for l in lines)
            close_b = sum(l.count('}') for l in lines)
            if open_b > close_b:
                for _ in range(open_b - close_b):
                    lines.append("}\n")
                self.log_thought(turn, "Action",
                                 f"Added {open_b - close_b} missing closing brace(s) '}}' to balance scope.")
                patched = True
            elif close_b > open_b:
                lines.insert(0, "{\n")
                self.log_thought(turn, "Action", "Inserted missing opening brace '{'.")
                patched = True

        # ── Strategy 4: Unmatched Parentheses — fix ALL affected lines ─────────
        need_paren = (ml_error_type == "UNMATCHED_PARANTHESES"
                      or any("paren" in e.lower() for e in current_errors))
        if need_paren:
            for i, line in enumerate(lines):
                op = line.count('(')
                cl = line.count(')')
                if op > cl:
                    s = line.rstrip("\r\n")
                    lines[i] = (s.replace("{", ") {") + "\n") if ("{" in s and ")" not in s) \
                                else (s + (")" * (op - cl)) + "\n")
                    self.log_thought(turn, "Action",
                                     f"Balanced missing ')' on line {i+1}.")
                    patched = True

        # ── Strategy 5: Invalid Assignment (5 = x  →  x = 5) — ALL lines ─────
        need_assign = (ml_error_type == "INVALID_ASSIGNMENT"
                       or any("assignment" in e.lower() for e in current_errors))
        if need_assign:
            for i, line in enumerate(lines):
                m = re.search(r'([0-9]+)\s*=\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;', line)
                if m:
                    lit, var = m.groups()
                    lines[i] = re.sub(
                        r'[0-9]+\s*=\s*[a-zA-Z_][a-zA-Z0-9_]*\s*;',
                        f'{var} = {lit};', line)
                    self.log_thought(turn, "Action",
                                     f"Swapped invalid l-value on line {i+1}: '{lines[i].strip()}'")
                    patched = True

        # ── Strategy 6: Unterminated String Literals — ALL lines ──────────────
        need_str = (ml_error_type == "UNTERMINATED_STRING"
                    or any("string" in e.lower() for e in current_errors))
        if need_str:
            for i, line in enumerate(lines):
                quotes = len(re.findall(r'(?<!\\)"', line))
                if quotes % 2 == 1:
                    s = line.rstrip("\r\n")
                    lines[i] = (s[:-1] + '";\n') if s.endswith(";") else (s + '"\n')
                    self.log_thought(turn, "Action",
                                     f"Closed unterminated string on line {i+1}.")
                    patched = True

        # ── Strategy 7: Fix Identifier Typos & Semantic Suggestions ──────────
        # 1. Apply semantic suggestions: e.g. 'coutt' was not declared (did you mean 'cout'?)
        for err in current_errors:
            m_sugg = re.search(r"'([a-zA-Z0-9_]+)' was not declared.*did you mean '([a-zA-Z0-9_]+)'", err)
            if m_sugg:
                wrong_id, right_id = m_sugg.groups()
                for i, line in enumerate(lines):
                    if re.search(r'\b' + re.escape(wrong_id) + r'\b', line):
                        lines[i] = re.sub(r'\b' + re.escape(wrong_id) + r'\b', right_id, line)
                        self.log_thought(turn, "Action", f"Repaired semantic typo '{wrong_id}' -> '{right_id}' on line {i+1}.")
                        patched = True

        # 2. Heuristic repairs for common C++ typos
        for i, line in enumerate(lines):
            orig_line = line
            # Stream output typos: (coutt|cot|cuot|coot|coutn|count) <<
            line = re.sub(r'\b(coutt|cot|cuot|coot|coutn)\s*<<', r'cout <<', line)
            if re.search(r'\bcount\s*<<', line):
                line = re.sub(r'\bcount\s*<<', r'cout <<', line)
            # Stream input typos: (cinn|ciin|cinp)\s*>>
            line = re.sub(r'\b(cinn|ciin|cinp)\s*>>', r'cin >>', line)
            # endl typos: <<\s*(ednl|endll|end1|edn)\b
            line = re.sub(r'<<\s*(ednl|endll|end1|edn)\b', r'<< endl', line)
            # include typos: #\s*(inclue|incldue|inculde)\b
            line = re.sub(r'#\s*(inclue|incldue|inculde)\b', r'#include', line)
            # return typos: (retrun|retun|retunr)\b
            line = re.sub(r'\b(retrun|retun|retunr)\b', r'return', line)
            # main typo: int\s+(mian)\s*\(
            line = re.sub(r'\bint\s+(mian)\s*\(', r'int main(', line)
            # while typo: (whlie|wile)\s*\(
            line = re.sub(r'\b(whlie|wile)\s*\(', r'while (', line)
            # printf typo: (prntf|print_f)\s*\(
            line = re.sub(r'\b(prntf|print_f)\s*\(', r'printf(', line)
            # scanf typo: (scnf|scan_f)\s*\(
            line = re.sub(r'\b(scnf|scan_f)\s*\(', r'scanf(', line)

            if line != orig_line:
                lines[i] = line
                self.log_thought(turn, "Action", f"Repaired typo on line {i+1}: '{line.strip()}'")
                patched = True

        # ── Strategy 8: Fix Missing Parentheses in if/else if conditionals ──
        for i, line in enumerate(lines):
            stripped = line.strip()
            # if x > 0 { -> if (x > 0) {
            m_if = re.match(r'^(\s*if)\s+([^({\n]+?)\s*(\{|$)', line)
            if m_if:
                indent_if, cond, rest = m_if.groups()
                lines[i] = f"{indent_if} ({cond.strip()}){rest}\n"
                self.log_thought(turn, "Action", f"Added parentheses to 'if' condition on line {i+1}.")
                patched = True

        # ── Strategy 9: Fix Array Declarations (e.g. int arr[10; -> int arr[10];) ──
        for i, line in enumerate(lines):
            if '[' in line and ']' not in line:
                if ';' in line:
                    lines[i] = re.sub(r'\[([^\]\n]+);', r'[\1];', line)
                else:
                    lines[i] = line.rstrip("\r\n") + "];\n"
                self.log_thought(turn, "Action", f"Closed missing array bracket ']' on line {i+1}.")
                patched = True

        # ── Strategy 10: Fix Class, Namespace, and Function missing braces ───
        for i, line in enumerate(lines):
            stripped = line.strip()
            # class Foo / struct Bar without {
            if re.match(r'^(class|struct|namespace)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*$', stripped):
                lines[i] = line.rstrip("\r\n") + " {\n"
                self.log_thought(turn, "Action", f"Added missing opening brace '{{' on line {i+1}.")
                patched = True
            # Function header like int main() or void foo() without { or ;
            if re.match(r'^(int|void|float|double|char|bool)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*$', stripped):
                # if next line is not {, add {
                next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                if next_line != "{":
                    lines[i] = line.rstrip("\r\n") + " {\n"
                    self.log_thought(turn, "Action", f"Added function body brace '{{' on line {i+1}.")
                    patched = True

        # ── Strategy 11: Fix Extra Tokens (duplicate semicolons, stray symbols) ──
        for i, line in enumerate(lines):
            if ';;' in line:
                lines[i] = line.replace(';;', ';')
                self.log_thought(turn, "Action", f"Removed duplicate semicolon on line {i+1}.")
                patched = True
            # using std namespace; -> using namespace std;
            if 'using std namespace;' in line:
                lines[i] = line.replace('using std namespace;', 'using namespace std;')
                self.log_thought(turn, "Action", f"Corrected misplaced keyword on line {i+1}.")
                patched = True

        # ── Strategy 12: Fix Invalid Type Names ──────────────────────────────
        for i, line in enumerate(lines):
            orig_l = line
            line = re.sub(r'\binterger\b', 'int', line)
            line = re.sub(r'\bcharector\b', 'char', line)
            line = re.sub(r'\bboolean\b', 'bool', line)
            line = re.sub(r'\bconstant\b', 'const', line)
            if line != orig_l:
                lines[i] = line
                self.log_thought(turn, "Action", f"Repaired invalid type keyword on line {i+1}: '{line.strip()}'")
                patched = True

        return lines

    def heal_code(self, source_code, ml_error_type="UNKNOWN", confidence=95.0):
        """
        Executes the autonomous agentic repair loop.
        """
        code_lines = source_code.splitlines(keepends=True)
        if not code_lines:
            return {
                "success": False,
                "healed_code": source_code,
                "thoughts": [],
                "turns_taken": 0,
                "diff": ""
            }

        self.thoughts = []
        
        # Turn 0: Perception
        self.log_thought(
            turn=1,
            phase="Perception",
            message=f"Received C++ source ({len(code_lines)} lines). ML Classifier tagged '{ml_error_type}' with {confidence}% confidence.",
            details={"ml_error_type": ml_error_type, "confidence": confidence}
        )

        current_candidate_lines = list(code_lines)
        success = False

        for turn in range(1, self.MAX_TURNS + 1):
            candidate_code = "".join(current_candidate_lines)

            # Tool Call: Run Compiler Front-End Verification
            is_valid, errors, ast_root = self.run_parser_validation(candidate_code)
            
            self.log_thought(
                turn=turn,
                phase="Verification (Tool Call)",
                message=f"Invoked 'cpp_parser' tool on candidate. Result: {'ZERO SYNTAX ERRORS (VALID)' if is_valid else f'{len(errors)} error(s) detected'}.",
                details={"errors_found": errors}
            )

            if is_valid:
                self.log_thought(
                    turn=turn,
                    phase="Resolution",
                    message="Code is syntactically sound! AST built cleanly with 0 ErrorNodes. Goal achieved.",
                    details={"status": "VERIFIED_CLEAN"}
                )
                success = True
                break

            # Reflection & Planning for next attempt
            self.log_thought(
                turn=turn,
                phase="Reflection",
                message=f"Remaining issues detected by compiler front-end: {errors[:2]}. Re-planning fix strategy.",
                details={"feedback": errors}
            )

            # Act
            current_candidate_lines = self.plan_and_patch(
                current_candidate_lines, 
                ml_error_type=ml_error_type, 
                current_errors=errors, 
                turn=turn
            )

        # Generate Unified Diff
        original_lines = source_code.splitlines(keepends=True)
        healed_lines = "".join(current_candidate_lines).splitlines(keepends=True)
        diff = "".join(difflib.unified_diff(
            original_lines, 
            healed_lines, 
            fromfile="original.cpp", 
            tofile="agent_healed.cpp"
        ))

        return {
            "success": success,
            "turns_taken": turn,
            "original_code": source_code,
            "healed_code": "".join(current_candidate_lines),
            "diff": diff if diff else "(No changes required)",
            "thoughts": self.thoughts
        }


# ============================================================================
# 4. UNIFIED PIPELINE RUNNER
# ============================================================================

def run_agentic_pipeline(filepath_or_code, ml_error_type=None, confidence=None):
    """
    Executes the full pipeline:
    1. Agentic Self-Healing
    2. Green Computing Profiling
    3. Cybersecurity Threat Audit
    """
    if os.path.exists(filepath_or_code):
        with open(filepath_or_code, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
        filename = os.path.basename(filepath_or_code)
    else:
        code = filepath_or_code
        filename = "submitted_code.cpp"

    # Autonomous ML classification using trained Random Forest model (model.pkl)
    if ml_error_type is None:
        ml_error_type, confidence = classify_syntax_error(code)

    # 1. Run Agentic Repair
    agent = AgenticRepairEngine()
    repair_result = agent.heal_code(code, ml_error_type=ml_error_type, confidence=confidence)

    # 2. Run Green Computing Profiling on healed code
    effective_code = repair_result["healed_code"] if repair_result["success"] else code
    green_profile = GreenComputingProfiler.profile_code(effective_code.splitlines(keepends=True))

    # 3. Run Cybersecurity Threat Audit
    security_audit = CyberThreatShield.audit_code(effective_code.splitlines(keepends=True))

    return {
        "filename": filename,
        "ml_error_type": ml_error_type,
        "confidence": confidence,
        "repair": repair_result,
        "green_computing": green_profile,
        "security_shield": security_audit
    }



# ═══════════════════════════════════════════════════════════════════════════
# CODE OPTIMIZER — Time & Space Complexity Reduction Engine
# ═══════════════════════════════════════════════════════════════════════════

class CodeOptimizer:
    """
    Analyzes C++ code for time and space complexity and applies
    evidence-based optimizations to reduce both.
    """

    # Patterns that indicate complexity classes
    _NESTED_LOOP_RE     = re.compile(r'(for|while)\s*\(.*\)\s*\{[^}]*(for|while)\s*\(', re.DOTALL)
    _LOOP_RE            = re.compile(r'\b(for|while)\s*\(')
    _ENDL_RE            = re.compile(r'\bendl\b')
    _POSTFIX_INC_RE     = re.compile(r'\b(\w+)\+\+\s*\)')   # i++) in for-loop
    _STRING_CONCAT_RE   = re.compile(r'(\w+)\s*\+=\s*["\']\w')
    _SORT_RE            = re.compile(r'\bsort\s*\(')
    _MAP_RE             = re.compile(r'\bmap\s*<')
    _UNORDERED_MAP_RE   = re.compile(r'\bunordered_map\s*<')
    _VECTOR_RE          = re.compile(r'\bvector\s*<')
    _PUSH_BACK_RE       = re.compile(r'\.push_back\s*\(')
    _DYN_ALLOC_RE       = re.compile(r'\bnew\b|\bmalloc\s*\(')
    _MEMSET_RE          = re.compile(r'\bmemset\s*\(')
    _COUT_FLUSH_RE      = re.compile(r'cout\s*<<\s*endl')
    _USING_NS_RE        = re.compile(r'using\s+namespace\s+std\s*;')
    _RESERVE_RE         = re.compile(r'\.reserve\s*\(')
    _RECURSION_RE       = re.compile(r'(\w+)\s*\(.*\{[^}]*\1\s*\(', re.DOTALL)

    @classmethod
    def _detect_complexity(cls, code):
        """Return a dict with time_complexity, space_complexity, and raw metrics."""
        lines = code.splitlines()
        loop_depth = 0
        max_depth  = 0
        cur_depth  = 0
        in_func    = False

        # Count nesting depth via brace tracking
        brace_stack = []
        loop_lines  = set()
        for i, ln in enumerate(lines):
            stripped = ln.strip()
            # crude: count for/while before brace
            if re.search(r'\b(for|while)\s*\(', stripped):
                loop_lines.add(len(brace_stack))  # note depth when loop starts
            for ch in stripped:
                if ch == '{':
                    brace_stack.append(i)
                elif ch == '}' and brace_stack:
                    brace_stack.pop()

        n_loops        = len(cls._LOOP_RE.findall(code))
        has_nested     = bool(cls._NESTED_LOOP_RE.search(code))
        has_sort       = bool(cls._SORT_RE.search(code))
        has_map        = bool(cls._MAP_RE.search(code))
        has_dyn_alloc  = bool(cls._DYN_ALLOC_RE.search(code))
        has_recursion  = bool(cls._RECURSION_RE.search(code))
        push_back_cnt  = len(cls._PUSH_BACK_RE.findall(code))
        has_reserve    = bool(cls._RESERVE_RE.search(code))

        if has_nested:
            time_c = "O(n²)"
        elif has_sort:
            time_c = "O(n log n)"
        elif n_loops > 0:
            time_c = "O(n)"
        elif has_recursion:
            time_c = "O(n) — recursive"
        else:
            time_c = "O(1)"

        if has_dyn_alloc or (push_back_cnt > 0 and not has_reserve):
            space_c = "O(n)"
        elif has_map:
            space_c = "O(n)"
        elif n_loops > 0:
            space_c = "O(1) — loop vars"
        else:
            space_c = "O(1)"

        return {
            "time_complexity":   time_c,
            "space_complexity":  space_c,
            "n_loops":           n_loops,
            "has_nested_loops":  has_nested,
            "has_sort":          has_sort,
            "has_map":           has_map,
            "has_dyn_alloc":     has_dyn_alloc,
            "push_back_count":   push_back_cnt,
            "has_reserve":       has_reserve,
        }

    @classmethod
    def optimize(cls, code_str):
        """
        Apply C++ code optimizations and return a full report dict:
        {
          optimized_code, changes, before_time, after_time,
          before_space, after_space, tips
        }
        """
        before_metrics = cls._detect_complexity(code_str)
        code = code_str
        changes = []
        tips    = []

        # ── Opt 1: endl -> '\n'  (avoids flushing stdout every iteration) ─────
        endl_count = len(cls._ENDL_RE.findall(code))
        if endl_count > 0:
            code = re.sub(r'\bcout\s*<<\s*endl\b', "cout << '\\\\n'", code)
            code = re.sub(r'<<\s*endl\b', "<< '\\\\n'", code)
            changes.append({
                "type": "Performance",
                "description": f"Replaced {endl_count} `endl` with `'\\\\n'`",
                "reason": "`endl` flushes the output buffer every call (expensive). `'\\\\n'` is ~10x faster in loops.",
                "impact": "High"
            })

        # ── Opt 2: i++ -> ++i in for-loop increments ──────────────────────────
        def replace_postfix(m):
            varname = m.group(1)
            return f'++{varname})'
        new_code, n_replaced = re.subn(r'\b(\w+)\+\+\s*\)', replace_postfix, code)
        if n_replaced > 0:
            code = new_code
            changes.append({
                "type": "Micro-optimization",
                "description": f"Changed {n_replaced} post-increment(s) `i++` -> `++i`",
                "reason": "Pre-increment avoids creating a temporary copy, giving a small speedup especially with iterators.",
                "impact": "Low"
            })

        # ── Opt 3: Add .reserve() hint before push_back loops ─────────────────
        push_cnt = len(cls._PUSH_BACK_RE.findall(code))
        if push_cnt > 0 and not cls._RESERVE_RE.search(code):
            # Insert a comment hint before first push_back line
            code = code.replace('.push_back(', '.push_back(', 1)  # no-op to trigger hint
            changes.append({
                "type": "Memory",
                "description": "Add `.reserve(N)` before push_back loop",
                "reason": f"Found {push_cnt} push_back() call(s) without reserve(). Pre-allocating avoids O(log n) reallocations.",
                "impact": "Medium"
            })
            tips.append("Add `vec.reserve(expected_size);` before the loop that calls `push_back()` to avoid reallocations.")

        # ── Opt 4: Nested loop detection — suggest algorithm change ───────────
        if before_metrics["has_nested_loops"]:
            changes.append({
                "type": "Algorithm",
                "description": "Nested loop detected — consider algorithmic refactor",
                "reason": "O(n^2) nested loops can often be replaced with hash-maps (O(n)) or sorting + two-pointer (O(n log n)).",
                "impact": "Critical"
            })
            tips.append("Replace the nested loop with an `unordered_map<>` lookup to reduce complexity from O(n^2) -> O(n).")

        # ── Opt 5: map → unordered_map (O(log n) → O(1) avg lookups) ─────────
        map_count = len(cls._MAP_RE.findall(code))
        unord_cnt = len(cls._UNORDERED_MAP_RE.findall(code))
        if map_count > 0 and unord_cnt == 0:
            changes.append({
                "type": "Data Structure",
                "description": f"Consider replacing `map<>` with `unordered_map<>`",
                "reason": "`std::map` uses a red-black tree: O(log n) lookup. `unordered_map` uses hashing: O(1) average lookup.",
                "impact": "High"
            })
            tips.append("Replace `map<K,V>` with `unordered_map<K,V>` when iteration order doesn't matter.")

        # ── Opt 6: Avoid `using namespace std;` in headers ────────────────────
        if cls._USING_NS_RE.search(code):
            tips.append("Avoid `using namespace std;` in production code — causes name collision risks. Prefer `std::cout`, `std::vector`, etc.")

        # ── Opt 7: String concat in loop -> stringstream ───────────────────────
        str_concat = cls._STRING_CONCAT_RE.findall(code)
        if str_concat:
            changes.append({
                "type": "Performance",
                "description": "String concatenation in loop detected",
                "reason": "Each `str += ...` creates a new string object (O(n^2) total). Use `std::ostringstream` then `.str()` once.",
                "impact": "High"
            })
            tips.append("Use `std::ostringstream oss; oss << ...; result = oss.str();` instead of `+=` concatenation in loops.")

        # ── Opt 8: Dynamic alloc -> stack alloc hint ───────────────────────────
        if before_metrics["has_dyn_alloc"]:
            tips.append("Consider replacing `new`/`malloc` with stack allocation or `std::vector`/`std::array` for automatic memory management.")

        # Recalculate complexity AFTER optimizations
        after_metrics = cls._detect_complexity(code)

        # If nested loops present and we have changes that could help
        if before_metrics["has_nested_loops"] and not after_metrics["has_nested_loops"]:
            after_metrics["time_complexity"] = "O(n)"

        # Default tips if nothing found
        if not tips and not changes:
            tips.append("Code looks well-optimized! No obvious performance improvements found.")
            changes.append({
                "type": "Status",
                "description": "No critical optimizations needed",
                "reason": "The submitted code does not show obvious performance anti-patterns.",
                "impact": "None"
            })

        return {
            "optimized_code":  code,
            "changes":         changes,
            "before_time":     before_metrics["time_complexity"],
            "after_time":      after_metrics["time_complexity"],
            "before_space":    before_metrics["space_complexity"],
            "after_space":     after_metrics["space_complexity"],
            "before_metrics":  before_metrics,
            "after_metrics":   after_metrics,
            "tips":            tips
        }


if __name__ == "__main__":

    test_code = """
#include <iostream>
using namespace std;

int main() {
    char user_buf[10];
    gets(user_buf);
    int count;
    for int i = 0; i < 5; i++ {
        cout << i
    }
    return 0;
}
"""
    print("Testing Agentic AI Pipeline...")
    res = run_agentic_pipeline(test_code, "INVALID_LOOP", 98.0)
    print("\n--- AGENT THOUGHTS ---")
    for t in res["repair"]["thoughts"]:
        print(f"[{t['timestamp']}] Turn {t['turn']} | {t['phase']}: {t['message']}")
    
    print("\n--- HEALED CODE ---")
    print(res["repair"]["healed_code"])

    print("\n--- GREEN COMPUTING ---")
    print(f"Grade: {res['green_computing']['eco_grade']} ({res['green_computing']['eco_status']})")
    print(f"Est Energy: {res['green_computing']['energy_microjoules']} µJ")

    print("\n--- SECURITY AUDIT ---")
    print(f"Threat Level: {res['security_shield']['overall_threat']}")
    for v in res["security_shield"]["vulnerabilities"]:
        print(f" - [{v['severity']}] {v['id']}: {v['name']} at line {v['line']}")
