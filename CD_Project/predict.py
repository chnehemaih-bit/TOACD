import sys
import os
import re
import csv
import tempfile
import subprocess
import shutil
import argparse
import joblib
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from collections import defaultdict, Counter


DIAGNOSTICS = {

    "MISSING_SEMICOLON": {
        "description": "A semicolon ';' is missing at the end of a statement or declaration.",
        "fix": (
            "Check the end of every statement inside your function.\n"
            "  Every variable declaration and expression must end with ';'"
        ),
        "example": (
            "  int x = 5      ← missing semicolon\n"
            "  int x = 5;     ← correct"
        ),
    },

    "UNMATCHED_BRACE": {
        "description": "A curly brace '{' or '}' is missing or mismatched.",
        "fix": (
            "Count your opening '{' and closing '}' braces.\n"
            "  Every function body, if/else block, loop, and class must have\n"
            "  a matching pair of curly braces."
        ),
        "example": (
            "  void foo() {        ← opening brace\n"
            "      int x = 5;      \n"
            "                      ← missing closing brace }\n"
            "  void foo() {        ← correct\n"
            "      int x = 5;\n"
            "  }"
        ),
    },

    "UNMATCHED_PARANTHESES": {
        "description": "A parenthesis '(' or ')' is missing or mismatched.",
        "fix": (
            "Check all your function calls, if/while/for conditions.\n"
            "  Every opening '(' must have a matching closing ')'"
        ),
        "example": (
            "  if (x > 5 {        ← missing closing parenthesis\n"
            "  if (x > 5) {       ← correct"
        ),
    },

    "INVALID_ASSIGNMENT": {
        "description": "An invalid assignment expression was detected. A literal or constant is being used as the left-hand side of an assignment.",
        "fix": (
            "The left side of '=' must always be a variable, not a literal.\n"
            "  Check that you haven't swapped the variable and value."
        ),
        "example": (
            "  5 = x;      ← invalid: literal on left side\n"
            "  x = 5;      ← correct"
        ),
    },

    "INVALID_DECLARATION": {
        "description": "An invalid variable declaration was detected. The variable may have an incorrect type, missing name, or invalid syntax.",
        "fix": (
            "A variable declaration must follow the pattern:\n"
            "  <type> <name>;\n"
            "  or <type> <name> = <value>;\n"
            "  Check for missing variable names or invalid type keywords."
        ),
        "example": (
            "  int ;         ← invalid: missing variable name\n"
            "  int x;        ← correct\n"
            "  int int x;    ← invalid: duplicate type keyword\n"
            "  int x = 5;    ← correct"
        ),
    },

    "INVALID_CONDITIONAL": {
        "description": "An invalid conditional statement was detected. The 'if' statement is missing its condition in parentheses.",
        "fix": (
            "An if statement must always have a condition inside parentheses:\n"
            "  if (<condition>) { ... }\n"
            "  Make sure the opening '(' comes right after 'if'."
        ),
        "example": (
            "  if x > 5 {         ← invalid: missing parentheses\n"
            "  if (x > 5) {       ← correct"
        ),
    },

    "INVALID_LOOP": {
        "description": "An invalid loop was detected. A 'for' or 'while' loop is missing its condition in parentheses.",
        "fix": (
            "A loop must always have its condition inside parentheses:\n"
            "  for (<init>; <cond>; <update>) { ... }\n"
            "  while (<condition>) { ... }\n"
            "  Make sure '(' comes right after 'for' or 'while'."
        ),
        "example": (
            "  for int i=0; i<5; i++ {    ← invalid: missing parentheses\n"
            "  for (int i=0; i<5; i++) {  ← correct"
        ),
    },

    "INVALID_TYPE": {
        "description": "An invalid type declaration was detected. Two type keywords appear consecutively, or an unknown type is used.",
        "fix": (
            "A variable declaration can only have ONE type keyword.\n"
            "  Remove the duplicate type, or check for a typo in the type name."
        ),
        "example": (
            "  int float x;    ← invalid: two types\n"
            "  float x;        ← correct"
        ),
    },

    "INVALID_ARRAY_DECL": {
        "description": "An invalid array declaration was detected. The array brackets '[]' are missing the closing ']'.",
        "fix": (
            "An array declaration must have properly closed brackets:\n"
            "  <type> <name>[<size>];\n"
            "  Make sure every '[' has a matching ']'."
        ),
        "example": (
            "  int arr[5;      ← invalid: missing closing bracket\n"
            "  int arr[5];     ← correct"
        ),
    },

    "INVALID_FUNCTION_DECL": {
        "description": "An invalid function declaration was detected. The function body opening brace '{' is missing, or the function has no return statement.",
        "fix": (
            "A function declaration must have:\n"
            "  1. A return type\n"
            "  2. A function name\n"
            "  3. Parentheses () for parameters\n"
            "  4. A body enclosed in { }\n"
            "  5. A return statement if the return type is not void"
        ),
        "example": (
            "  int foo()           ← invalid: missing body { }\n"
            "  int foo() { }       ← valid structure\n"
            "  int foo() {         ← correct\n"
            "      return 0;\n"
            "  }"
        ),
    },

    "EXTRA_TOKENS": {
        "description": "Extra or unexpected tokens were detected in the code. There may be stray characters, duplicate keywords, or misplaced symbols.",
        "fix": (
            "Look for extra symbols, repeated keywords, or characters that\n"
            "  don't belong. Common causes:\n"
            "  - Duplicate semicolons (;;)\n"
            "  - Extra closing braces or brackets\n"
            "  - Stray operators or symbols"
        ),
        "example": (
            "  int x = 5;; extra    ← invalid: extra token after semicolon\n"
            "  int x = 5;           ← correct"
        ),
    },

    "MISPLACED_KEYWORD": {
        "description": "A keyword is used in the wrong place or context. Common causes include 'else' without 'if', keywords in expressions, or control flow keywords where they don't belong.",
        "fix": (
            "Check the context where the keyword is used.\n"
            "  - 'else' must follow an 'if' statement\n"
            "  - Control flow keywords ('if', 'while', 'for') cannot be used in expressions\n"
            "  - Keywords like 'return', 'break', 'continue' must be in appropriate contexts"
        ),
        "example": (
            "  return if (x > 0);     ← invalid: 'if' in return statement\n"
            "  if (x > 0) return 1;   ← correct: proper if statement\n"
            "  \n"
            "  else { ... }           ← invalid: else without if\n"
            "  if (x > 0) { ... }     ← correct: if-then structure\n"
            "  else { ... }"
        ),
    },

    "UNTERMINATED_STRING": {
        "description": "An unterminated string literal was detected. A string is opened with '\"' but never closed.",
        "fix": (
            "Every string literal must start and end with a double quote '\"'.\n"
            "  Check that you haven't accidentally left a string unclosed."
        ),
        "example": (
            '  cout << "hello;      ← invalid: string never closed\n'
            '  cout << "hello";     ← correct'
        ),
    },

    "INVALID_SWITCH": {
        "description": "An invalid switch statement was detected. Switch statements require proper case/default labels and structure.",
        "fix": (
            "Switch statements must follow this structure:\n"
            "  switch (expression) {\n"
            "      case value1:\n"
            "          // code\n"
            "          break;\n"
            "      case value2:\n"
            "          // code\n"
            "          break;\n"
            "      default:\n"
            "          // code\n"
            "  }\n"
            "  Check for missing colons after case/default, or missing opening/closing braces."
        ),
        "example": (
            "  switch (x) {         ← correct structure\n"
            "      case 1:\n"
            "          break;\n"
            "      default:\n"
            "          break;\n"
            "  }\n"
            "  \n"
            "  switch x {           ← invalid: missing parentheses\n"
            "      case 1           ← invalid: missing colon\n"
            "          break;\n"
            "  }"
        ),
    },

    "INVALID_CLASS_DECL": {
        "description": "An invalid class or struct declaration was detected. Class/struct declarations require proper opening and closing braces.",
        "fix": (
            "Class/struct declarations must follow this structure:\n"
            "  class ClassName {\n"
            "  public:\n"
            "      // members\n"
            "  private:\n"
            "      // members\n"
            "  };\n"
            "  Check for missing opening/closing braces or semicolons."
        ),
        "example": (
            "  class MyClass {      ← correct structure\n"
            "  public:\n"
            "      int x;\n"
            "  };\n"
            "  \n"
            "  class MyClass        ← invalid: missing opening brace\n"
            "  public:\n"
            "      int x;\n"
            "  ;"
        ),
    },

    "INVALID_NAMESPACE_DECL": {
        "description": "An invalid namespace declaration was detected. Namespace declarations require proper opening and closing braces.",
        "fix": (
            "Namespace declarations must follow this structure:\n"
            "  namespace MyNamespace {\n"
            "      // declarations\n"
            "  }\n"
            "  Check for missing opening/closing braces."
        ),
        "example": (
            "  namespace MyNS {     ← correct structure\n"
            "      int x;\n"
            "  }\n"
            "  \n"
            "  namespace MyNS       ← invalid: missing opening brace\n"
            "      int x;\n"
            "  "
        ),
    },
}


CPP_KEYWORDS = {
    "int","float","double","char","bool","void","long","short",
    "unsigned","signed","const","static","extern","register","volatile",
    "if","else","while","for","do","switch","case","default",
    "break","continue","return","goto",
    "class","struct","union","enum","typedef","namespace","using",
    "public","private","protected","virtual","override","final",
    "new","delete","this","nullptr","NULL","true","false",
    "include","define","ifdef","ifndef","endif","pragma",
    "template","typename","operator","sizeof","typeof",
    "try","catch","throw","auto","inline","explicit","friend","mutable",
}

TOKEN_SPEC = [
    ("HASH",          r"#"),
    ("STRING",        r'"(?:[^"\\]|\\.)*"?'),
    ("CHAR",          r"'(?:[^'\\]|\\.)*'?"),
    ("FLOAT",         r"\b\d+\.\d*([eE][+-]?\d+)?\b|\b\d*\.\d+([eE][+-]?\d+)?\b"),
    ("INTEGER",       r"\b\d+\b"),
    ("IDENTIFIER",    r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("SEMICOLON",     r";"),
    ("OPEN_PAREN",    r"\("),
    ("CLOSE_PAREN",   r"\)"),
    ("OPEN_BRACE",    r"\{"),
    ("CLOSE_BRACE",   r"\}"),
    ("OPEN_BRACKET",  r"\["),
    ("CLOSE_BRACKET", r"\]"),
    ("OPERATOR",      r"[+\-*/%=<>!&|^~?:.,]+"),
    ("NEWLINE",       r"\n"),
    ("WHITESPACE",    r"[ \t\r]+"),
    ("UNKNOWN",       r"."),
]

import re as _re
MASTER_REGEX = _re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)

def strip_comments(code):
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code

def detect_syntax_errors_in_code(code_lines):
    """Detect syntax errors at the source code level and return error info."""
    errors = {}
    
    # Check for unmatched braces
    brace_count = 0
    paren_count = 0
    bracket_count = 0
    unterminated_string_lines = []
    
    for line_no, line in enumerate(code_lines, 1):
        # Skip comments
        line_clean = re.sub(r'//.*', '', line)
        line_clean = re.sub(r'/\*.*?\*/', '', line_clean, flags=re.DOTALL)
        
        # Check for unterminated strings
        if '"' in line_clean:
            str_count = 0
            i = 0
            while i < len(line_clean):
                if line_clean[i] == '"' and (i == 0 or line_clean[i-1] != '\\'):
                    str_count += 1
                i += 1
            if str_count % 2 == 1:
                unterminated_string_lines.append(line_no)
                errors['UNTERMINATED_STRING'] = {'line': line_no, 'context': line.strip()}
        
        # Count braces
        for char in line_clean:
            if char == '{': brace_count += 1
            elif char == '}': brace_count -= 1
            elif char == '(': paren_count += 1
            elif char == ')': paren_count -= 1
            elif char == '[': bracket_count += 1
            elif char == ']': bracket_count -= 1
        
        # Check for missing semicolon at line end
        line_stripped = line.rstrip()
        if line_stripped and not line_stripped.endswith(';') and not line_stripped.endswith('{') and not line_stripped.endswith('}') and not line_stripped.endswith(':'):
            # Heuristic: if line has assignment or declaration without semicolon
            # BUT skip lines that are for/while/if statements (they need parens, not semicolons)
            stripped_clean = re.sub(r'//.*', '', line_stripped).strip()
            is_control_flow = re.match(r'^\s*(for|while|if|else\s+if)\b', stripped_clean)
            if not is_control_flow and re.search(r'\b(int|float|double|char|bool|void|string)\b.*[^{};]$', line_stripped):
                if 'MISSING_SEMICOLON' not in errors:
                    errors['MISSING_SEMICOLON'] = {'line': line_no, 'context': line.strip()}
    
    # Check for mismatched braces/parens
    if brace_count != 0:
        errors['UNMATCHED_BRACE'] = {'line': -1, 'context': f'Unmatched braces: {brace_count}'}
    if paren_count != 0:
        errors['UNMATCHED_PARANTHESES'] = {'line': -1, 'context': f'Unmatched parentheses: {paren_count}'}
    if bracket_count != 0:
        errors['INVALID_ARRAY_DECL'] = {'line': -1, 'context': f'Unmatched brackets: {bracket_count}'}
    
    return errors


def infer_error_line(parse_errors, source_errors, error_type=None, code_lines=None):
    """Infer error line from parse/source errors, or scan code for the error pattern."""
    # First try parse errors
    for error in parse_errors:
        match = re.search(r"line\s+(\d+)", error)
        if match:
            line_num = int(match.group(1))
            # For INVALID_SWITCH with case error, search backward from reported line for actual 'case' line
            if error_type == 'INVALID_SWITCH' and code_lines and 'case' in error.lower():
                for i in range(max(0, line_num-10), min(len(code_lines), line_num+1)):
                    if code_lines[i].lstrip().startswith('case') and ':' not in code_lines[i]:
                        return i + 1
            return line_num
    # Then try source errors
    for error_info in source_errors.values():
        if error_info.get('line', 0) > 0:
            return error_info['line']
    # If no explicit line info, try to find the error by scanning code
    if error_type and code_lines:
        if error_type == 'INVALID_LOOP':
            for i, line in enumerate(code_lines, 1):
                stripped = line.lstrip()
                if (stripped.startswith('for') or stripped.startswith('while')) and '(' not in line:
                    return i
        elif error_type == 'INVALID_CONDITIONAL':
            for i, line in enumerate(code_lines, 1):
                stripped = line.lstrip()
                if stripped.startswith('if') and '(' not in line:
                    return i
        elif error_type == 'MISSING_SEMICOLON':
            for i, line in enumerate(code_lines, 1):
                stripped = line.rstrip()
                if stripped and not stripped.endswith(';') and not stripped.endswith('{') and not stripped.endswith('}'):
                    if re.search(r'\b(int|float|double|char|bool|void|string)\b.*[^{};]$', stripped):
                        return i
        elif error_type == 'INVALID_SWITCH':
            for i, line in enumerate(code_lines, 1):
                stripped = line.lstrip()
                # Look for case without colon
                if stripped.startswith('case') and ':' not in line:
                    return i
                # Look for switch without opening brace
                if stripped.startswith('switch') and '{' not in line and '(' in line:
                    return i
    return None


def apply_autofix(code_lines, error_type, parse_errors, source_errors):
    fixed_lines = list(code_lines)
    changes = []
    line_no = infer_error_line(parse_errors, source_errors, error_type, code_lines)
    idx = line_no - 1 if line_no and line_no <= len(fixed_lines) else None

    def replace_line(new_text, reason, index):
        if index is None or index < 0 or index >= len(fixed_lines):
            return
        current = fixed_lines[index].rstrip('\n')
        candidate = new_text.rstrip('\n')
        if current != candidate:
            fixed_lines[index] = candidate + '\n'
            changes.append(f"Line {index+1}: {reason}\n    - {current}\n    + {candidate}")

    def append_line(text, reason):
        fixed_text = text if text.endswith('\n') else text + '\n'
        fixed_lines.append(fixed_text)
        changes.append(f"Appended line: {reason}\n    + {text.rstrip()}")

    def add_missing_brace():
        open_count = sum(line.count('{') for line in fixed_lines)
        close_count = sum(line.count('}') for line in fixed_lines)
        if open_count > close_count:
            append_line('}', 'Added missing closing brace')
        elif close_count > open_count:
            fixed_lines.insert(0, '{\n')
            changes.append('Inserted missing opening brace at top of file')

    def add_missing_paren():
        open_count = sum(line.count('(') for line in fixed_lines)
        close_count = sum(line.count(')') for line in fixed_lines)
        if open_count > close_count:
            # Find the specific line that's missing a closing paren
            for i, line in enumerate(fixed_lines):
                line_open = line.count('(')
                line_close = line.count(')')
                if line_open > line_close and line_open > 0:
                    stripped = line.rstrip('\n')
                    # Add ) before the { if present
                    if '{' in stripped and ')' not in stripped:
                        new_line = stripped.replace('{', ') {')
                        replace_line(new_line, 'Added missing closing parenthesis before brace', i)
                        return
                    elif not stripped.endswith(')'):
                        replace_line(stripped + ')', 'Added missing closing parenthesis', i)
                        return
            # Fallback
            append_line(')', 'Added missing closing parenthesis')
        elif close_count > open_count:
            fixed_lines.insert(0, '(\n')
            changes.append('Inserted missing opening parenthesis at top of file')

    if error_type == 'MISSING_SEMICOLON' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if line and not line.rstrip().endswith(';') and not line.rstrip().endswith('{') and not line.rstrip().endswith('}'):
            replace_line(line + ';', 'Added missing semicolon', idx)

    if error_type == 'UNMATCHED_BRACE':
        add_missing_brace()

    if error_type == 'UNMATCHED_PARANTHESES':
        add_missing_paren()

    if error_type == 'UNTERMINATED_STRING' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        # Count unescaped quotes
        quote_count = len(re.findall(r'(?<!\\)"', line))
        if quote_count % 2 == 1:
            replace_line(line + '"', 'Closed unterminated string literal', idx)

    if error_type == 'MISPLACED_KEYWORD' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if re.search(r"\breturn\s+if\s*\(", line):
            replace_line(re.sub(r"\breturn\s+if\s*\(", 'return (', line), "Removed misplaced 'if' after return", idx)
        elif re.search(r"\breturn\s+else\b", line):
            replace_line(re.sub(r"\breturn\s+else\b", 'return', line), "Removed misplaced 'else' after return", idx)

    if error_type == 'INVALID_SWITCH' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        stripped = line.lstrip()
        if stripped.startswith('case') and not stripped.rstrip().endswith(':'):
            replace_line(line + ':', "Added missing ':' after case label", idx)
        elif stripped.startswith('switch') and '{' not in line:
            replace_line(line + ' {', "Added missing opening brace for switch", idx)

    if error_type == 'INVALID_CLASS_DECL' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if re.match(r"^\s*(class|struct)\b", line) and '{' not in line:
            replace_line(line + ' {', "Added missing opening brace for class/struct", idx)

    if error_type == 'INVALID_NAMESPACE_DECL' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if line.lstrip().startswith('namespace') and '{' not in line:
            replace_line(line + ' {', "Added missing opening brace for namespace", idx)

    if error_type == 'INVALID_CONDITIONAL' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if re.match(r"^\s*if\s+[^\(]", line):
            replace_line(re.sub(r"^(\s*if)\s+(.+?)(\s*\{|$)", lambda m: f"{m.group(1)} ({m.group(2).strip()}){m.group(3)}", line), "Added missing parentheses for if condition", idx)

    if error_type == 'INVALID_LOOP' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        # Strip inline comments before parsing
        code_part = re.sub(r'//.*$', '', stripped).rstrip()
        
        if code_part.startswith('while') and '(' not in code_part:
            # "while x > 0 {" → "while (x > 0) {"
            match = re.match(r"while\s+(.+?)(\s*\{)\s*$", code_part)
            if not match:
                match = re.match(r"while\s+(.+)$", code_part)
            if match:
                condition = match.group(1).strip().rstrip('{').strip()
                has_brace = '{' in code_part
                rest = ' {' if has_brace else ''
                new_line = f"{indent}while ({condition}){rest}"
                replace_line(new_line, "Added missing parentheses for while condition", idx)
        
        elif code_part.startswith('for') and '(' not in code_part:
            # "for int i = 0; i < 5; i++ {" → "for (int i = 0; i < 5; i++) {"
            match = re.match(r"for\s+(.+?)(\s*\{)\s*$", code_part)
            if not match:
                match = re.match(r"for\s+(.+)$", code_part)
            if match:
                condition = match.group(1).strip().rstrip('{').strip()
                has_brace = '{' in code_part
                rest = ' {' if has_brace else ''
                new_line = f"{indent}for ({condition}){rest}"
                replace_line(new_line, "Added missing parentheses for for loop", idx)

    if error_type == 'INVALID_ARRAY_DECL' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if '[' in line and ']' not in line:
            # Fix: int arr[10; → int arr[10];
            # Match pattern: [ ... ; and replace with [ ... ];
            new_line = re.sub(r'\[([^\]]+);', r'[\1];', line)
            if new_line != line:
                replace_line(new_line, "Closed missing array bracket", idx)
            elif line.rstrip().endswith(';'):
                # Fallback: add ] before final ;
                replace_line(line.rstrip()[:-1] + '];', "Closed missing array bracket", idx)
            else:
                # No semicolon, just add ]
                replace_line(line + ']', "Closed missing array bracket", idx)

    if error_type == 'INVALID_FUNCTION_DECL' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if line.rstrip().endswith(')'):
            replace_line(line + ' {', "Added missing function body brace", idx)

    if error_type == 'EXTRA_TOKENS' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        if ';;' in line:
            replace_line(line.replace(';;', ';'), "Removed duplicate semicolon", idx)
        elif '$$' in line or '@@' in line or '##' in line:
            replace_line(re.sub(r"\$\$|@@|##", '', line), "Removed stray extra token", idx)

    if error_type == 'INVALID_TYPE' and idx is not None:
        line = fixed_lines[idx].rstrip('\n')
        pattern = r"\b(int|float|double|char|long|short|unsigned|signed|bool|void)\s+(int|float|double|char|long|short|unsigned|signed|bool|void)\b"
        replace_line(re.sub(pattern, lambda m: m.group(1), line), "Removed duplicate type keyword", idx)

    return fixed_lines, changes


def compile_and_run_cpp(filepath):
    if not shutil.which('g++'):
        return False, 'g++ not found on system', None
    with tempfile.TemporaryDirectory() as td:
        exe_path = os.path.join(td, 'a.out')
        compile_proc = subprocess.run(['g++', '-std=c++17', filepath, '-o', exe_path], capture_output=True, text=True)
        if compile_proc.returncode != 0:
            return False, compile_proc.stderr.strip(), None
        run_proc = subprocess.run([exe_path], capture_output=True, text=True, timeout=15)
        output = run_proc.stdout.strip()
        if run_proc.stderr.strip():
            output = output + '\n' + run_proc.stderr.strip() if output else run_proc.stderr.strip()
        return True, output if output else 'Program ran successfully with no output.', run_proc.returncode


def tokenize(filepath):
    """Tokenize a single .cpp file. Returns list of token dicts."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception as e:
        print(f"ERROR reading file: {e}")
        sys.exit(1)

    code = strip_comments(code)
    tokens = []
    token_index = 0
    line = 1
    line_start = 0

    for mo in MASTER_REGEX.finditer(code):
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
            "file_name":    os.path.basename(filepath),
            "label":        "UNKNOWN",
            "token_index":  token_index,
            "token_type":   kind,
            "token_value":  value,
            "line":         line,
            "column":       col,
        })
        token_index += 1

    return tokens


try:
    from cpp_parser import build_ast
except ImportError:
    try:
        from parser import build_ast
    except ImportError:
        print("ERROR: Could not find cpp_parser.py or parser.py")
        print("Make sure cpp_parser.py is in the same folder as predict.py")
        sys.exit(1)

try:
    from ast_features import extract_features
except ImportError:
    print("ERROR: Could not find ast_features.py")
    print("Make sure ast_features.py is in the same folder as predict.py")
    sys.exit(1)


def generate_performance_analysis(performance_data, output_dir="performance_analysis"):
    """Generate comprehensive performance analysis with graphs."""
    os.makedirs(output_dir, exist_ok=True)

    # Extract data
    error_types = list(performance_data['error_counts'].keys())
    error_counts = list(performance_data['error_counts'].values())
    fix_success_rates = [performance_data['fix_success_rates'].get(et, 0) for et in error_types]
    detection_times = list(performance_data['detection_times'])
    confidence_scores = list(performance_data['confidence_scores'])

    # Set up the plotting style
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('C++ Syntax Error Classifier Performance Analysis', fontsize=16, fontweight='bold')

    # 1. Error Type Distribution
    axes[0, 0].bar(error_types, error_counts, color='skyblue', alpha=0.8)
    axes[0, 0].set_title('Error Type Distribution', fontweight='bold')
    axes[0, 0].set_xlabel('Error Types')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].tick_params(axis='x', rotation=45)

    # Add value labels on bars
    for i, v in enumerate(error_counts):
        axes[0, 0].text(i, v + 0.1, str(v), ha='center', va='bottom')

    # 2. Fix Success Rates
    bars = axes[0, 1].bar(error_types, fix_success_rates, color='lightgreen', alpha=0.8)
    axes[0, 1].set_title('Auto-Fix Success Rates', fontweight='bold')
    axes[0, 1].set_xlabel('Error Types')
    axes[0, 1].set_ylabel('Success Rate (%)')
    axes[0, 1].set_ylim(0, 100)
    axes[0, 1].tick_params(axis='x', rotation=45)

    # Color bars based on success rate
    for bar, rate in zip(bars, fix_success_rates):
        if rate >= 80:
            bar.set_color('darkgreen')
        elif rate >= 60:
            bar.set_color('orange')
        else:
            bar.set_color('red')

    # Add percentage labels
    for i, v in enumerate(fix_success_rates):
        axes[0, 1].text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')

    # 3. Detection Time Distribution
    if detection_times:
        axes[1, 0].hist(detection_times, bins=10, color='lightcoral', alpha=0.8, edgecolor='black')
        axes[1, 0].set_title('Detection Time Distribution', fontweight='bold')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].axvline(np.mean(detection_times), color='red', linestyle='--', linewidth=2,
                          label=f'Mean: {np.mean(detection_times):.3f}s')
        axes[1, 0].legend()

    # 4. Model Confidence Scores
    if confidence_scores:
        axes[1, 1].boxplot(confidence_scores, patch_artist=True,
                          boxprops=dict(facecolor='lightblue', color='blue'),
                          medianprops=dict(color='red', linewidth=2))
        axes[1, 1].set_title('Model Confidence Score Distribution', fontweight='bold')
        axes[1, 1].set_ylabel('Confidence Score')
        axes[1, 1].set_xticks([1], ['ML Model'])
        axes[1, 1].grid(True, alpha=0.3)

        # Add statistics
        if confidence_scores:
            mean_conf = np.mean(confidence_scores)
            median_conf = np.median(confidence_scores)
            axes[1, 1].text(0.5, 0.95, f'Mean: {mean_conf:.3f}\nMedian: {median_conf:.3f}',
                           transform=axes[1, 1].transAxes, ha='center', va='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    performance_plot_path = os.path.join(output_dir, 'performance_analysis.png')
    plt.savefig(performance_plot_path, dpi=300, bbox_inches='tight')
    plt.close()

    # Generate detailed metrics report
    report_path = os.path.join(output_dir, 'performance_report.txt')
    with open(report_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("C++ SYNTAX ERROR CLASSIFIER PERFORMANCE REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("EXECUTION SUMMARY:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total execution time: {performance_data['total_time']:.3f} seconds\n")
        f.write(f"Files processed: {performance_data['files_processed']}\n")
        f.write(f"Errors detected: {sum(error_counts)}\n")
        f.write(f"Auto-fixes applied: {performance_data['fixes_applied']}\n")
        f.write(f"Successful compilations: {performance_data['successful_compilations']}\n\n")

        f.write("ERROR TYPE BREAKDOWN:\n")
        f.write("-" * 20 + "\n")
        for error_type, count in performance_data['error_counts'].items():
            success_rate = performance_data['fix_success_rates'].get(error_type, 0)
            f.write(f"{error_type:25} | Count: {count:3} | Fix Success: {success_rate:5.1f}%\n")

        f.write("\nPERFORMANCE METRICS:\n")
        f.write("-" * 20 + "\n")
        if detection_times:
            f.write(f"Average detection time: {np.mean(detection_times):.3f} seconds\n")
            f.write(f"Min detection time: {min(detection_times):.3f} seconds\n")
            f.write(f"Max detection time: {max(detection_times):.3f} seconds\n")

        if confidence_scores:
            f.write(f"Average confidence score: {np.mean(confidence_scores):.3f}\n")
            f.write(f"Median confidence score: {np.median(confidence_scores):.3f}\n")
            f.write(f"Confidence score range: {min(confidence_scores):.3f} - {max(confidence_scores):.3f}\n")

        overall_success_rate = (performance_data['successful_compilations'] / max(performance_data['files_processed'], 1)) * 100
        f.write(f"\nOverall success rate: {overall_success_rate:.1f}%\n")

    print(f"\n📊 PERFORMANCE ANALYSIS GENERATED:")
    print(f"   📈 Charts saved to: {performance_plot_path}")
    print(f"   📋 Report saved to: {report_path}")

    return performance_plot_path, report_path


def predict(filepath, self_heal=False, performance_data=None):
    if performance_data is None:
        performance_data = {
            'error_counts': Counter(),
            'fix_success_rates': {},
            'detection_times': [],
            'confidence_scores': [],
            'total_time': 0,
            'files_processed': 0,
            'fixes_applied': 0,
            'successful_compilations': 0
        }

    start_time = time.time()
    performance_data['files_processed'] += 1
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    if not filepath.endswith(".cpp"):
        print(f"WARNING: File does not end with .cpp — proceeding anyway.")

    # Read the original source code for syntax error detection
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            code_lines = f.readlines()
    except Exception as e:
        print(f"ERROR reading source code: {e}")
        sys.exit(1)

    for f in ["model.pkl", "scaler.pkl", "label_encoder.pkl"]:
        if not os.path.exists(f):
            print(f"ERROR: {f} not found. Run train.py first.")
            sys.exit(1)


    rf = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    le = joblib.load("label_encoder.pkl")

    # Detect syntax errors at source code level
    source_errors = detect_syntax_errors_in_code(code_lines)

    # tokenize
    tokens = tokenize(filepath)
    if not tokens:
        print("ERROR: No tokens found in file. Is it empty?")
        sys.exit(1)

    # build AST
    ast_root, parse_errors = build_ast(tokens)

    # extract features
    feats = extract_features(ast_root, parse_errors)

    # get feature order from training
    feature_cols = [
        "num_function_decls","num_var_decls","num_assign_exprs",
        "num_array_decls","num_if_stmts","num_else_stmts",
        "num_while_stmts","num_for_stmts","num_return_stmts",
        "num_compound_stmts","num_expr_stmts","total_nodes",
        "max_depth","avg_depth","num_leaf_nodes",
        "error_invalid_assignment","error_unmatched_brace",
        "error_unmatched_paren","error_missing_semicolon",
        "error_invalid_conditional","error_invalid_loop",
        "error_invalid_type","error_invalid_array",
        "error_invalid_func_decl","total_error_nodes",
        "scope_depth_max","has_orphan_else","func_missing_return",
        "assign_in_condition","nested_func_decl"
    ]

    X = np.array([[feats.get(col, 0) for col in feature_cols]])
    X_scaled = scaler.transform(X)

    # predict
    detection_start = time.time()
    pred_encoded = rf.predict(X_scaled)[0]
    pred_label   = le.inverse_transform([pred_encoded])[0]
    proba        = rf.predict_proba(X_scaled)[0]
    confidence   = proba[pred_encoded] * 100
    detection_time = time.time() - detection_start

    # Track performance data
    performance_data['detection_times'].append(detection_time)
    performance_data['confidence_scores'].append(confidence)

    # Check if parser errors override prediction (parser is most specific)
    parser_error_type = None
    if parse_errors:
        for error in parse_errors:
            # Extract error type from parse error message
            for etype in [
                "MISPLACED_KEYWORD", "INVALID_ASSIGNMENT", "INVALID_CONDITIONAL",
                "INVALID_LOOP", "INVALID_TYPE", "INVALID_ARRAY_DECL",
                "INVALID_FUNCTION_DECL", "INVALID_SWITCH", "INVALID_CLASS_DECL",
                "INVALID_NAMESPACE_DECL", "UNMATCHED_BRACE", "UNMATCHED_PARANTHESES",
                "MISSING_SEMICOLON"
            ]:
                if etype in error:
                    parser_error_type = etype
                    break
            if parser_error_type:
                break
    
    if parser_error_type:
        pred_label = parser_error_type
        confidence = 95.0
    elif source_errors:
        # Source-level heuristics only used when parser didn't find anything specific
        for error_type, error_info in source_errors.items():
            pred_label = error_type
            confidence = 95.0
            break

    # Track error count
    performance_data['error_counts'][pred_label] += 1

    # get diagnostics
    diag = DIAGNOSTICS.get(pred_label, {
        "description": "Unknown error type detected.",
        "fix": "Review your code carefully for syntax issues.",
        "example": ""
    })

    # print output
    print(f"\n  DIAGNOSTIC:")
    print(f"  {diag['description']}")
    
    # Show error location if found
    if pred_label in source_errors:
        error_info = source_errors[pred_label]
        if error_info['line'] > 0:
            print(f"\n  ERROR LOCATION:")
            print(f"  Line {error_info['line']}: {error_info['context']}")
    elif parse_errors:
        # Show first parser error
        print(f"\n  ERROR LOCATION:")
        print(f"  {parse_errors[0]}")
    
    print(f"\n  SUGGESTED FIX:")
    print(f"  {diag['fix']}")
    if diag.get("example"):
        print(f"\n  EXAMPLE:")
        print(f"{diag['example']}")

    # show parse errors if any
    if parse_errors and pred_label not in source_errors:
        print(f"\n  PARSER DETECTED {len(parse_errors)} ISSUE(S):")
        for e in parse_errors[:5]:
            print(f"    {e}")

    fix_compiled = False
    fix_attempted = self_heal

    if self_heal:
        fixed_lines, changes = apply_autofix(code_lines, pred_label, parse_errors, source_errors)
        if changes:
            performance_data['fixes_applied'] += 1
            print(f"\n  AUTO-FIX CHANGES ({len(changes)}):")
            for change in changes:
                formatted = change.replace('\n', '\n      ')
                print(f"    - {formatted}")
            fixed_path = os.path.splitext(filepath)[0] + ".fixed.cpp"
            with open(fixed_path, "w", encoding="utf-8", errors="ignore") as f:
                f.writelines(fixed_lines)
            print(f"\n  Saved repaired file to: {fixed_path}")
            compiled, output, rc = compile_and_run_cpp(fixed_path)
            if compiled:
                fix_compiled = True
                performance_data['successful_compilations'] += 1
                print("\n  COMPILE/RUN SUCCESS:")
                print(f"    {output}")
                # Update success rate for this error type
                if pred_label in performance_data['fix_success_rates']:
                    performance_data['fix_success_rates'][pred_label] = (
                        performance_data['fix_success_rates'][pred_label] + 100.0
                    ) / 2  # Simple moving average
                else:
                    performance_data['fix_success_rates'][pred_label] = 100.0
            else:
                print("\n  AUTO-FIX RESULT: compilation failed")
                print(f"    {output}")
                # Update success rate for this error type
                if pred_label in performance_data['fix_success_rates']:
                    performance_data['fix_success_rates'][pred_label] = (
                        performance_data['fix_success_rates'][pred_label] + 0.0
                    ) / 2  # Simple moving average
                else:
                    performance_data['fix_success_rates'][pred_label] = 0.0
        else:
            print("\n  AUTO-FIX: No automatic repair could be applied for this error type.")
            # No fix attempted, so no change to success rate

    # Record total execution time
    end_time = time.time()
    performance_data['total_time'] = end_time - start_time

    # Emit structured performance JSON for the server to parse
    import json as _json
    perf_json = {
        "error_type": pred_label,
        "confidence": float(confidence),
        "detection_time": float(detection_time),
        "fix_attempted": fix_attempted,
        "fix_compiled": fix_compiled,
        "total_time": float(performance_data['total_time']),
    }
    print(f"PERF_JSON:{_json.dumps(perf_json)}")

    # Generate performance analysis if this is the main execution
    if performance_data['files_processed'] == 1:
        generate_performance_analysis(performance_data)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Diagnose C++ syntax errors and optionally auto-fix them.')
    parser.add_argument('filepath', help='Path to the C++ source file')
    parser.add_argument('--self-heal', action='store_true', help='Attempt an automatic repair and compile/run the fixed file')
    parser.add_argument('--analyze-performance', action='store_true', help='Generate performance analysis with graphs after execution')
    args = parser.parse_args()

    performance_data = {
        'error_counts': Counter(),
        'fix_success_rates': {},
        'detection_times': [],
        'confidence_scores': [],
        'total_time': 0,
        'files_processed': 0,
        'fixes_applied': 0,
        'successful_compilations': 0
    }

    predict(args.filepath, self_heal=args.self_heal, performance_data=performance_data)

    # Generate performance analysis if requested
    if args.analyze_performance:
        generate_performance_analysis(performance_data)
