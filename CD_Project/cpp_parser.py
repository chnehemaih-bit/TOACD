import pandas as pd
from dataclasses import dataclass, field
from typing import List, Any, Tuple



@dataclass
class ASTNode:
    node_type : str
    value     : str = "" 
    line      : int = 0
    children  : List[Any] = field(default_factory=list)

    def add(self, child):
        if child:
            self.children.append(child)

    def __repr__(self, indent=0):
        pad = "  " * indent
        s   = f"{pad}[{self.node_type}]"
        if self.value:
            s += f"  '{self.value}'"
        if self.line:
            s += f"  (line {self.line})"
        for c in self.children:
            s += "\n" + c.__repr__(indent + 1)
        return s


class Cursor:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else None

    def consume(self):
        t = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        self.pos += 1
        return t

    def done(self):
        return self.pos >= len(self.tokens)

    def is_type(self, *types):
        t = self.peek()
        return t is not None and t["token_type"] in types

    def is_value(self, *vals):
        t = self.peek()
        return t is not None and t["token_value"] in vals


# Variable types
TYPE_KW = {"int", "float", "double", "char", "bool", "void",
           "long", "short", "unsigned", "signed", "string", "auto"}


class Parser:
    def __init__(self, tokens):
        self.cur = Cursor(tokens)
        self.errors = []
        self.error_nodes = []

    def err(self, msg):
        t = self.cur.peek()
        loc = f"line {t['line']}" if t else "EOF"
        self.errors.append(f"[ParseError @ {loc}] {msg}")
        return loc

    def is_type_kw(self, tok):
        return tok and tok["token_type"] == "KEYWORD" and tok["token_value"] in TYPE_KW

    def is_func_decl(self):
        t0, t1, t2 = self.cur.peek(0), self.cur.peek(1), self.cur.peek(2)
        if not (t0 and t1 and t2):
            return False
        return (self.is_type_kw(t0) and
                t1["token_type"] == "IDENTIFIER" and
                t2["token_type"] == "OPEN_PAREN")

    def is_var_decl(self):
        t0, t1 = self.cur.peek(0), self.cur.peek(1)
        if not (t0 and t1):
            return False
        return self.is_type_kw(t0) and t1["token_type"] in ("IDENTIFIER", "KEYWORD", "OPEN_BRACKET")

    def is_class_decl(self):
        t0, t1 = self.cur.peek(0), self.cur.peek(1)
        if not (t0 and t1):
            return False
        return t0["token_type"] == "KEYWORD" and t0["token_value"] in ("class", "struct") and t1["token_type"] == "IDENTIFIER"

    def is_namespace_decl(self):
        t0, t1, t2 = self.cur.peek(0), self.cur.peek(1), self.cur.peek(2)
        if not (t0 and t1):
            return False
        # Avoid "using namespace" declarations
        if t0["token_type"] == "KEYWORD" and t0["token_value"] == "namespace" and t1["token_type"] == "IDENTIFIER":
            # Check if previous token was "using"
            prev_pos = self.cur.pos - 1
            if prev_pos >= 0 and self.cur.tokens[prev_pos]["token_value"] == "using":
                return False
            return True
        return False

    def parse(self):
        root = ASTNode("ProgramNode", line=1)
        while not self.cur.done():
            if self.cur.is_type("HASH"):
                self.skip_directive()
            elif self.is_func_decl():
                root.add(self.parse_func_decl())
            elif self.is_class_decl():
                root.add(self.parse_class_decl())
            elif self.is_namespace_decl():
                root.add(self.parse_namespace_decl())
            elif self.is_var_decl():
                root.add(self.parse_var_decl())
            else:
                self.cur.consume()
        return root

    def skip_directive(self):
        ln = self.cur.peek()["line"]
        while not self.cur.done() and self.cur.peek()["line"] == ln:
            self.cur.consume()

    def parse_func_decl(self):
        ret = self.cur.consume()
        name = self.cur.consume()
        node = ASTNode("FunctionDeclNode",
                       value=f"{ret['token_value']} {name['token_value']}",
                       line=ret["line"])
        if self.cur.is_type("OPEN_PAREN"):
            self.cur.consume()
            depth = 1
            while not self.cur.done() and depth > 0:
                if self.cur.is_type("OPEN_PAREN"):
                    depth += 1
                if self.cur.is_type("CLOSE_PAREN"):
                    depth -= 1
                self.cur.consume()
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_compound())
        else:
            line = name["line"] if name else 0
            self.err(f"Missing '{{' after function — INVALID_FUNCTION_DECL")
            node.add(ASTNode("ErrorNode", value="INVALID_FUNCTION_DECL", line=line))
        return node

    def parse_class_decl(self):
        kw_tok = self.cur.consume()  # class or struct
        name_tok = self.cur.consume()  # class name
        node = ASTNode("ClassDeclNode",
                       value=f"{kw_tok['token_value']} {name_tok['token_value']}",
                       line=kw_tok["line"])
        
        # Check for inheritance (optional)
        if self.cur.is_type("COLON"):
            self.cur.consume()
            # Parse inheritance list
            while not self.cur.done() and not self.cur.is_type("OPEN_BRACE", "SEMICOLON"):
                self.cur.consume()
        
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_class_body())
        else:
            self.err(f"Missing '{{' after class/struct declaration — INVALID_CLASS_DECL")
            node.add(ASTNode("ErrorNode", value="INVALID_CLASS_DECL", line=kw_tok["line"]))
        return node

    def parse_class_body(self):
        tok = self.cur.consume()
        node = ASTNode("ClassBodyNode", value="{}", line=tok["line"])
        while not self.cur.done() and not self.cur.is_type("CLOSE_BRACE"):
            if self.cur.is_type("KEYWORD") and self.cur.peek()["token_value"] in ("public", "private", "protected"):
                node.add(self.parse_access_specifier())
            elif self.is_func_decl():
                node.add(self.parse_func_decl())
            elif self.is_var_decl():
                node.add(self.parse_var_decl())
            else:
                self.cur.consume()
        if self.cur.is_type("CLOSE_BRACE"):
            self.cur.consume()
        else:
            self.err("Missing '}' after class body — UNMATCHED_BRACE")
            node.add(ASTNode("ErrorNode", value="UNMATCHED_BRACE", line=tok["line"]))
        return node

    def parse_access_specifier(self):
        tok = self.cur.consume()
        node = ASTNode("AccessSpecifierNode", value=tok["token_value"], line=tok["line"])
        if self.cur.is_type("COLON"):
            self.cur.consume()
        else:
            self.err("Missing ':' after access specifier — MISSING_SEMICOLON")
            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=tok["line"]))
        return node

    def parse_namespace_decl(self):
        kw_tok = self.cur.consume()  # namespace
        name_tok = self.cur.consume()  # namespace name
        node = ASTNode("NamespaceDeclNode",
                       value=f"namespace {name_tok['token_value']}",
                       line=kw_tok["line"])
        
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_namespace_body())
        else:
            self.err(f"Missing '{{' after namespace declaration — INVALID_NAMESPACE_DECL")
            node.add(ASTNode("ErrorNode", value="INVALID_NAMESPACE_DECL", line=kw_tok["line"]))
        return node

    def parse_namespace_body(self):
        tok = self.cur.consume()
        node = ASTNode("NamespaceBodyNode", value="{}", line=tok["line"])
        while not self.cur.done() and not self.cur.is_type("CLOSE_BRACE"):
            if self.is_func_decl():
                node.add(self.parse_func_decl())
            elif self.is_class_decl():
                node.add(self.parse_class_decl())
            elif self.is_var_decl():
                node.add(self.parse_var_decl())
            else:
                self.cur.consume()
        if self.cur.is_type("CLOSE_BRACE"):
            self.cur.consume()
        else:
            self.err("Missing '}' after namespace body — UNMATCHED_BRACE")
            node.add(ASTNode("ErrorNode", value="UNMATCHED_BRACE", line=tok["line"]))
        return node

    def parse_compound(self):
        tok = self.cur.consume()
        node = ASTNode("CompoundStmtNode", value="{}", line=tok["line"])
        while not self.cur.done() and not self.cur.is_type("CLOSE_BRACE"):
            node.add(self.parse_stmt())
        if self.cur.is_type("CLOSE_BRACE"):
            self.cur.consume()
        else:
            self.err("Missing '}' — UNMATCHED_BRACE")
            node.add(ASTNode("ErrorNode", value="UNMATCHED_BRACE", line=tok["line"]))
        return node

    def parse_stmt(self):
        t = self.cur.peek()
        if not t:
            return None
        ty, val = t["token_type"], t["token_value"]
        if ty == "HASH":
            self.skip_directive()
            return None
        if ty == "KEYWORD" and val == "if":
            return self.parse_if()
        if ty == "KEYWORD" and val == "else":
            return self.parse_else()
        if ty == "KEYWORD" and val == "while":
            return self.parse_while()
        if ty == "KEYWORD" and val == "for":
            return self.parse_for()
        if ty == "KEYWORD" and val == "switch":
            return self.parse_switch()
        if ty == "KEYWORD" and val == "case":
            return self.parse_case()
        if ty == "KEYWORD" and val == "default":
            return self.parse_default()
        if ty == "KEYWORD" and val == "return":
            return self.parse_return()
        if ty == "OPEN_BRACE":
            return self.parse_compound()
        if self.is_func_decl():
            return self.parse_func_decl()
        if self.is_var_decl():
            return self.parse_var_decl()
        return self.parse_expr_stmt()

    def parse_if(self):
        tok = self.cur.consume()
        node = ASTNode("IfStmtNode", line=tok["line"])
        if self.cur.is_type("OPEN_PAREN"):
            node.add(self.parse_paren_expr())
        else:
            self.err("Missing '(' after if — INVALID_CONDITIONAL")
            node.add(ASTNode("ErrorNode", value="INVALID_CONDITIONAL", line=tok["line"]))
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_compound())
        else:
            node.add(self.parse_stmt())
        return node

    def parse_else(self):
        tok = self.cur.consume()
        node = ASTNode("ElseStmtNode", line=tok["line"])
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_compound())
        elif self.cur.is_value("if"):
            node.add(self.parse_if())
        else:
            node.add(self.parse_stmt())
        return node

    def parse_while(self):
        tok = self.cur.consume()
        node = ASTNode("WhileStmtNode", line=tok["line"])
        if self.cur.is_type("OPEN_PAREN"):
            node.add(self.parse_paren_expr())
        else:
            self.err("Missing '(' after while — INVALID_LOOP")
            node.add(ASTNode("ErrorNode", value="INVALID_LOOP", line=tok["line"]))
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_compound())
        return node

    def parse_for(self):
        tok = self.cur.consume()
        node = ASTNode("ForStmtNode", line=tok["line"])
        if self.cur.is_type("OPEN_PAREN"):
            node.add(self.parse_paren_expr())
        else:
            self.err("Missing '(' after for — INVALID_LOOP")
            node.add(ASTNode("ErrorNode", value="INVALID_LOOP", line=tok["line"]))
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_compound())
        return node

    def parse_switch(self):
        tok = self.cur.consume()
        node = ASTNode("SwitchStmtNode", line=tok["line"])
        if self.cur.is_type("OPEN_PAREN"):
            node.add(self.parse_paren_expr())
        else:
            self.err("Missing '(' after switch — INVALID_CONDITIONAL")
            node.add(ASTNode("ErrorNode", value="INVALID_CONDITIONAL", line=tok["line"]))
        if self.cur.is_type("OPEN_BRACE"):
            node.add(self.parse_switch_body())
        else:
            self.err("Missing '{' after switch condition — INVALID_FUNCTION_DECL")
            node.add(ASTNode("ErrorNode", value="INVALID_FUNCTION_DECL", line=tok["line"]))
        return node

    def parse_switch_body(self):
        tok = self.cur.consume()
        node = ASTNode("SwitchBodyNode", value="{}", line=tok["line"])
        while not self.cur.done() and not self.cur.is_type("CLOSE_BRACE"):
            if self.cur.is_type("KEYWORD") and self.cur.peek()["token_value"] in ("case", "default"):
                if self.cur.peek()["token_value"] == "case":
                    node.add(self.parse_case())
                else:
                    node.add(self.parse_default())
            else:
                node.add(self.parse_stmt())
        if self.cur.is_type("CLOSE_BRACE"):
            self.cur.consume()
        else:
            self.err("Missing '}' after switch — UNMATCHED_BRACE")
            node.add(ASTNode("ErrorNode", value="UNMATCHED_BRACE", line=tok["line"]))
        return node

    def parse_case(self):
        tok = self.cur.consume()
        node = ASTNode("CaseStmtNode", line=tok["line"])
        # Parse case value
        while not self.cur.done() and not self.cur.is_type("COLON", "CLOSE_BRACE"):
            t = self.cur.consume()
            node.add(ASTNode("ExprNode", value=t["token_value"], line=t["line"]))
        if self.cur.is_type("COLON"):
            self.cur.consume()
        else:
            self.err("Missing ':' after case — INVALID_SWITCH")
            node.add(ASTNode("ErrorNode", value="INVALID_SWITCH", line=tok["line"]))
        return node

    def parse_default(self):
        tok = self.cur.consume()
        node = ASTNode("DefaultStmtNode", line=tok["line"])
        if self.cur.is_type("COLON"):
            self.cur.consume()
        else:
            self.err("Missing ':' after default — MISSING_SEMICOLON")
            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=tok["line"]))
        return node

    def parse_return(self):
        tok = self.cur.consume()
        node = ASTNode("ReturnStmtNode", line=tok["line"])
        
        # Check for misplaced keywords after return
        if self.cur.is_type("KEYWORD") and self.cur.peek()["token_value"] in ("if", "while", "for", "else", "switch", "case", "default", "break", "continue", "goto"):
            kw_tok = self.cur.peek()
            self.err(f"Misplaced keyword '{kw_tok['token_value']}' after return — MISPLACED_KEYWORD")
            node.add(ASTNode("ErrorNode", value="MISPLACED_KEYWORD", line=kw_tok["line"]))
        
        while not self.cur.done() and not self.cur.is_type("SEMICOLON", "CLOSE_BRACE"):
            t = self.cur.consume()
            node.add(ASTNode("ExprNode", value=t["token_value"], line=t["line"]))
        if self.cur.is_type("SEMICOLON"):
            self.cur.consume()
        else:
            self.err("Missing ';' after return — MISSING_SEMICOLON")
            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=tok["line"]))
        return node

    def parse_var_decl(self):
        type_tok = self.cur.consume()
        node = ASTNode("VarDeclNode", value=type_tok["token_value"], line=type_tok["line"])

        # Check for consecutive type keywords (INVALID_TYPE)
        if self.cur.is_type("KEYWORD") and self.cur.peek()["token_value"] in TYPE_KW:
            extra = self.cur.consume()
            node.add(ASTNode("ErrorNode", value="INVALID_TYPE", line=extra["line"]))
            self.err(f"Consecutive type keywords — INVALID_TYPE at line {extra['line']}")

        if self.cur.is_type("IDENTIFIER"):
            name_tok = self.cur.consume()
            node.value += f" {name_tok['token_value']}"

            if self.cur.is_type("OPEN_BRACKET"):
                arr = ASTNode("ArrayDeclNode", value=name_tok["token_value"], line=name_tok["line"])
                self.cur.consume()
                if self.cur.is_type("CLOSE_BRACKET"):
                    self.cur.consume()
                else:
                    self.err("Missing ']' — INVALID_ARRAY_DECL")
                    arr.add(ASTNode("ErrorNode", value="INVALID_ARRAY_DECL", line=name_tok["line"]))
                node.add(arr)

            elif self.cur.is_type("OPERATOR") and self.cur.peek()["token_value"] == "=":
                op = self.cur.consume()
                asgn = ASTNode("AssignExprNode", value="=", line=op["line"])
                while not self.cur.done() and not self.cur.is_type("SEMICOLON", "CLOSE_BRACE"):
                    r = self.cur.consume()
                    asgn.add(ASTNode("ExprNode", value=r["token_value"], line=r["line"]))
                node.add(asgn)

        elif self.cur.is_type("INTEGER", "STRING"):
            lit = self.cur.consume()
            node.add(ASTNode("ErrorNode", value="INVALID_ASSIGNMENT", line=lit["line"]))
            self.err(f"Literal as lvalue — INVALID_ASSIGNMENT at line {lit['line']}")

        if self.cur.is_type("SEMICOLON"):
            self.cur.consume()
        elif not self.cur.is_type("CLOSE_BRACE"):
            ln = self.cur.peek()["line"] if self.cur.peek() else "?"
            self.err(f"Missing ';' — MISSING_SEMICOLON at line {ln}")
            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=type_tok["line"]))
        return node

    def parse_expr_stmt(self):
        t = self.cur.peek()
        node = ASTNode("ExprStmtNode", line=t["line"] if t else 0)

        if self.cur.is_type("INTEGER", "STRING"):
            lit = self.cur.consume()
            if self.cur.is_type("OPERATOR") and self.cur.peek()["token_value"] == "=":
                self.cur.consume()
                node.add(ASTNode("ErrorNode", value="INVALID_ASSIGNMENT", line=lit["line"]))
                self.err(f"Literal lvalue — INVALID_ASSIGNMENT at line {lit['line']}")

        while not self.cur.done() and not self.cur.is_type("SEMICOLON", "CLOSE_BRACE", "OPEN_BRACE"):
            tok = self.cur.consume()
            node.add(ASTNode("ExprNode", value=tok["token_value"], line=tok["line"]))

        if self.cur.is_type("SEMICOLON"):
            self.cur.consume()
        elif not self.cur.is_type("CLOSE_BRACE", "OPEN_BRACE"):
            self.err("Missing ';' — MISSING_SEMICOLON")
            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON",
                             line=self.cur.peek()["line"] if self.cur.peek() else 0))
        return node

    def parse_paren_expr(self):
        tok = self.cur.consume()
        node = ASTNode("ConditionNode", line=tok["line"])
        depth = 1
        while not self.cur.done() and depth > 0:
            t = self.cur.peek()
            if t["token_type"] == "OPEN_PAREN":
                depth += 1
            if t["token_type"] == "CLOSE_PAREN":
                depth -= 1
                if depth == 0:
                    self.cur.consume()
                    break
            ct = self.cur.consume()
            node.add(ASTNode("ExprNode", value=ct["token_value"], line=ct["line"]))
        if depth != 0:
            self.err("Unmatched '(' — UNMATCHED_PARANTHESES")
            node.add(ASTNode("ErrorNode", value="UNMATCHED_PARANTHESES", line=tok["line"]))
        return node


def build_ast(token_rows):
    """
    token_rows : list of dicts for ONE file from tokens.csv
    returns    : (ASTNode root, list of parse error strings)
    """
    p = Parser(token_rows)
    root = p.parse()
    return root, p.errors


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "tokens.csv"
    df = pd.read_csv(path)

    first = df["file_name"].iloc[0]
    rows = df[df["file_name"] == first].to_dict("records")

    print(f"\n[FILE]   {first}")
    print(f"[TOKENS] {len(rows)}\n")

    ast, errs = build_ast(rows)
    print("── AST ──")
    print(ast)
    if errs:
        print("\n── PARSE ERRORS ──")
        for e in errs:
            print(" ", e)
