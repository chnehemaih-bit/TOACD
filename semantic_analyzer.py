"""
semantic_analyzer.py
====================
Semantic analysis pass over the C++ AST produced by cpp_parser.py.

Checks performed:
  1. Duplicate variable declaration in the same scope
  2. Uninitialized variable declaration
  3. Missing return statement in non-void function
  4. Empty function body
  5. 'void' used as a variable type (not a function return)
  6. Undeclared identifier usage (best-effort heuristic)
"""

import re
from typing import List, Dict, Any

# ── identifiers that are always implicitly in scope ───────────────────────────
BUILTIN_NAMES = {
    "cout", "cin", "cerr", "clog", "endl", "flush", "ws",
    "std", "string", "vector", "map", "set", "list", "array",
    "NULL", "nullptr", "true", "false",
    "main", "printf", "scanf", "fprintf", "fscanf", "sprintf",
    "malloc", "calloc", "realloc", "free",
    "new", "delete", "sizeof", "typeof",
    "INT_MAX", "INT_MIN", "UINT_MAX", "SIZE_MAX",
    "exit", "abort", "assert",
    "memcpy", "memset", "memmove", "memcmp",
    "strlen", "strcpy", "strncpy", "strcat", "strcmp",
    "fopen", "fclose", "fread", "fwrite", "fgets", "fputs",
    "pow", "sqrt", "abs", "fabs", "ceil", "floor",
    "max", "min", "swap",
}

# token types treated as "value" tokens when scanning for identifier usage
_VALUE_TYPES = {"IDENTIFIER"}


class _Scope:
    """Represents one lexical scope (function body, block, etc.)."""

    def __init__(self, name: str = "<block>"):
        self.name = name
        # name → {'type': str, 'line': int, 'initialized': bool}
        self.vars: Dict[str, dict] = {}

    def declare(self, name: str, vtype: str, line: int, initialized: bool):
        self.vars[name] = {"type": vtype, "line": line, "initialized": initialized}

    def has(self, name: str) -> bool:
        return name in self.vars


class SemanticAnalyzer:
    """
    Walk a cpp_parser ASTNode tree and collect semantic diagnostics.
    """

    def analyze(self, ast_root, tokens: List[dict], source_lines: List[str]) -> dict:
        self._issues: List[dict] = []
        self._symbol_table: List[dict] = []
        self._scope_stack: List[_Scope] = [_Scope("<global>")]
        self._function_count = 0

        try:
            self._walk(ast_root, current_func_return=None, source_lines=source_lines)
        except Exception as exc:
            self._issues.append({
                "severity": "INFO",
                "type": "Analyzer Internal Error",
                "message": f"Semantic walk stopped early: {exc}",
                "line": 0, "column": 0,
                "snippet": "",
                "suggestion": "This is a limitation of the static analyzer, not a code error.",
            })

        scope_summary = {
            "total_scopes": self._function_count + 1,
            "functions": [
                e["name"] for e in self._symbol_table if e.get("kind") == "function"
            ],
            "variables": [
                e["name"] for e in self._symbol_table if e.get("kind") == "variable"
            ],
        }

        return {
            "issues": self._issues,
            "symbol_table": self._symbol_table,
            "scope_summary": scope_summary,
        }

    # ── internal helpers ──────────────────────────────────────────────────────

    def _current_scope(self) -> _Scope:
        return self._scope_stack[-1]

    def _push_scope(self, name: str):
        self._scope_stack.append(_Scope(name))

    def _pop_scope(self):
        if len(self._scope_stack) > 1:
            self._scope_stack.pop()

    def _is_declared(self, name: str) -> bool:
        """Check all scopes from innermost to outermost."""
        for scope in reversed(self._scope_stack):
            if scope.has(name):
                return True
        return name in BUILTIN_NAMES

    def _add_issue(self, severity, itype, message, line, snippet="", suggestion=""):
        self._issues.append({
            "severity": severity,
            "type": itype,
            "message": message,
            "line": line,
            "column": 0,
            "snippet": snippet.strip(),
            "suggestion": suggestion,
        })

    def _get_line(self, source_lines: List[str], line: int) -> str:
        if 1 <= line <= len(source_lines):
            return source_lines[line - 1]
        return ""

    def _scope_name(self) -> str:
        return " > ".join(s.name for s in self._scope_stack)

    # ── AST walker ────────────────────────────────────────────────────────────

    def _walk(self, node, current_func_return, source_lines):
        if node is None:
            return

        nt = node.node_type

        # ── Function declaration ──────────────────────────────────────────────
        if nt == "FunctionDeclNode":
            self._function_count += 1
            func_name = node.value  # e.g. "int main"
            parts = func_name.split()
            ret_type = parts[0] if parts else "unknown"
            name = parts[-1] if len(parts) >= 2 else func_name

            # Register in symbol table
            self._symbol_table.append({
                "kind": "function",
                "name": name,
                "type": ret_type,
                "scope": self._scope_name(),
                "line": node.line,
                "initialized": True,
            })

            # Declare function name in current scope
            self._current_scope().declare(name, ret_type, node.line, True)

            self._push_scope(f"fn:{name}")

            # Walk children — track if there's a return statement
            has_return = self._children_have_return(node)
            if ret_type not in ("void", "unknown", "") and not has_return:
                self._add_issue(
                    "WARNING", "Missing Return Statement",
                    f"Function '{name}' has return type '{ret_type}' but no return statement was found.",
                    node.line,
                    func_name,
                    f"Add 'return <value>;' at the end of '{name}'.",
                )

            # Check for empty body
            compound = next(
                (c for c in node.children if c.node_type == "CompoundStmtNode"), None
            )
            if compound is not None and len(compound.children) == 0:
                self._add_issue(
                    "INFO", "Empty Function Body",
                    f"Function '{name}' has an empty body.",
                    node.line, func_name,
                    "Implement the function or add a comment explaining the intent.",
                )

            for child in node.children:
                self._walk(child, ret_type, source_lines)

            self._pop_scope()
            return

        # ── Compound / block statement ────────────────────────────────────────
        if nt == "CompoundStmtNode":
            self._push_scope("<block>")
            for child in node.children:
                self._walk(child, current_func_return, source_lines)
            self._pop_scope()
            return

        # ── Variable declaration ──────────────────────────────────────────────
        if nt == "VarDeclNode":
            raw = node.value  # e.g. "int a" or "float x"
            parts = raw.split()
            vtype = parts[0] if parts else "unknown"
            vname = parts[-1] if len(parts) >= 2 else raw

            snippet = self._get_line(source_lines, node.line)
            has_assign = any(c.node_type == "AssignExprNode" for c in node.children)

            # Check: void variable
            if vtype == "void":
                self._add_issue(
                    "ERROR", "Invalid Type: void Variable",
                    f"Variable '{vname}' cannot have type 'void'.",
                    node.line, snippet,
                    f"Change the type of '{vname}' to a valid type (e.g. int, float, char).",
                )

            # Check: duplicate declaration in same scope
            if self._current_scope().has(vname):
                existing = self._current_scope().vars[vname]
                self._add_issue(
                    "ERROR", "Duplicate Variable Declaration",
                    f"'{vname}' is already declared in this scope (first at line {existing['line']}).",
                    node.line, snippet,
                    f"Remove or rename the second declaration of '{vname}'.",
                )
            else:
                self._current_scope().declare(vname, vtype, node.line, has_assign)
                self._symbol_table.append({
                    "kind": "variable",
                    "name": vname,
                    "type": vtype,
                    "scope": self._scope_name(),
                    "line": node.line,
                    "initialized": has_assign,
                })

                # Warn: uninitialized
                if not has_assign and vtype not in ("void",):
                    self._add_issue(
                        "INFO", "Uninitialized Variable",
                        f"Variable '{vname}' of type '{vtype}' is declared but not initialized.",
                        node.line, snippet,
                        f"Initialize it: '{vtype} {vname} = 0;' (or appropriate default).",
                    )

            for child in node.children:
                self._walk(child, current_func_return, source_lines)
            return

        # ── Expression / statement nodes — scan for undeclared identifiers ────
        if nt in ("ExprStmtNode", "ExprNode", "AssignExprNode"):
            for child in node.children:
                if child.node_type == "ExprNode":
                    val = child.value
                    # Bare identifier that's not a builtin, keyword, or already declared
                    if (re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', val)
                            and not self._is_declared(val)):
                        import difflib
                        known = list(BUILTIN_NAMES)
                        for s in self._scope_stack:
                            known.extend(s.vars.keys())
                        matches = difflib.get_close_matches(val, known, n=1, cutoff=0.6)
                        did_mean = matches[0] if matches else None
                        snippet = self._get_line(source_lines, child.line)
                        msg = f"'{val}' was not declared in this scope" + (f" (did you mean '{did_mean}'?)" if did_mean else ".")
                        sugg = f"Replace '{val}' with '{did_mean}'." if did_mean else f"Declare '{val}' before using it, e.g. 'int {val} = 0;'."
                        self._add_issue(
                            "ERROR", "Undeclared Identifier",
                            msg,
                            child.line, snippet,
                            sugg,
                        )
                self._walk(child, current_func_return, source_lines)
            return

        # ── Default: recurse into children ────────────────────────────────────
        for child in node.children:
            self._walk(child, current_func_return, source_lines)

    def _children_have_return(self, node) -> bool:
        """Recursively check if any descendant is a ReturnStmtNode."""
        for child in node.children:
            if child.node_type == "ReturnStmtNode":
                return True
            if self._children_have_return(child):
                return True
        return False
