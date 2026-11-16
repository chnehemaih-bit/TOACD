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
        return tok is not None and tok["token_type"] == "KEYWORD" and tok["token_value"] in TYPE_KW

    def is_func_decl(self):
        if not self.is_type_kw(self.cur.peek(0)):
            return False
        offset = 1
        while self.cur.peek(offset) and (
            (self.cur.peek(offset)["token_type"] == "OPERATOR" and self.cur.peek(offset)["token_value"] in ("*", "&"))
            or (self.cur.peek(offset)["token_type"] == "KEYWORD" and self.cur.peek(offset)["token_value"] in ("const", "volatile"))
        ):
            offset += 1
        t_id = self.cur.peek(offset)
        t_paren = self.cur.peek(offset + 1)
        return (t_id is not None and t_id["token_type"] == "IDENTIFIER" and
                t_paren is not None and t_paren["token_type"] == "OPEN_PAREN")

    def is_var_decl(self):
        if not self.is_type_kw(self.cur.peek(0)):
            return False
        offset = 1
        while self.cur.peek(offset) and (
            (self.cur.peek(offset)["token_type"] == "OPERATOR" and self.cur.peek(offset)["token_value"] in ("*", "&"))
            or (self.cur.peek(offset)["token_type"] == "KEYWORD" and self.cur.peek(offset)["token_value"] in ("const", "volatile"))
        ):
            offset += 1
        t = self.cur.peek(offset)
        if not t:
            return False
        if t["token_type"] in ("IDENTIFIER", "KEYWORD", "OPEN_BRACKET"):
            next_t = self.cur.peek(offset + 1)
            if next_t and next_t["token_type"] == "OPEN_PAREN":
                return False
            return True
        return False

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
            pos_before = self.cur.pos
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
            if self.cur.pos == pos_before:
                self.cur.consume()
        return root

    def skip_directive(self):
        ln = self.cur.peek()["line"]
        while not self.cur.done() and self.cur.peek()["line"] == ln:
            self.cur.consume()

    def parse_func_decl(self):
        ret = self.cur.consume()
        val = ret["token_value"]
        while self.cur.is_type("OPERATOR") and self.cur.peek()["token_value"] in ("*", "&"):
            val += self.cur.consume()["token_value"]
        name = self.cur.consume() if not self.cur.done() else {"token_value": "anonymous", "line": ret["line"]}
        node = ASTNode("FunctionDeclNode",
                       value=f"{val} {name['token_value']}",
                       line=ret["line"])
        if self.cur.is_type("OPEN_PAREN"):
            self.cur.consume()
            depth = 1
            while not self.cur.done() and depth > 0:
                if self.cur.is_type("OPEN_PAREN"):
                    depth += 1
                if self.cur.is_type("CLOSE_PAREN"):
                    depth -= 1
                    if depth == 0:
                        self.cur.consume()
                        break
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
            pos_before = self.cur.pos
            if self.cur.is_type("KEYWORD") and self.cur.peek()["token_value"] in ("public", "private", "protected"):
                node.add(self.parse_access_specifier())
            elif self.is_func_decl():
                node.add(self.parse_func_decl())
            elif self.is_var_decl():
                node.add(self.parse_var_decl())
            else:
                self.cur.consume()
            if self.cur.pos == pos_before:
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
            pos_before = self.cur.pos
            if self.is_func_decl():
                node.add(self.parse_func_decl())
            elif self.is_class_decl():
                node.add(self.parse_class_decl())
            elif self.is_var_decl():
                node.add(self.parse_var_decl())
            else:
                self.cur.consume()
            if self.cur.pos == pos_before:
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
            pos_before = self.cur.pos
            node.add(self.parse_stmt())
            if self.cur.pos == pos_before:
                self.cur.consume()
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
            pos_before = self.cur.pos
            if self.cur.is_type("KEYWORD") and self.cur.peek()["token_value"] in ("case", "default"):
                if self.cur.peek()["token_value"] == "case":
                    node.add(self.parse_case())
                else:
                    node.add(self.parse_default())
            else:
                node.add(self.parse_stmt())
            if self.cur.pos == pos_before:
                self.cur.consume()
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

        # Consume any pointer/reference symbols like * or &
        while self.cur.is_type("OPERATOR") and self.cur.peek()["token_value"] in ("*", "&"):
            op_tok = self.cur.consume()
            node.value += op_tok["token_value"]

        if self.cur.is_type("IDENTIFIER"):
            name_tok = self.cur.consume()
            node.value += f" {name_tok['token_value']}"

            if self.cur.is_type("OPEN_BRACKET"):
                arr = ASTNode("ArrayDeclNode", value=name_tok["token_value"], line=name_tok["line"])
                self.cur.consume()
                while not self.cur.done() and not self.cur.is_type("CLOSE_BRACKET", "SEMICOLON", "CLOSE_BRACE"):
                    arr.add(ASTNode("ExprNode", value=self.cur.consume()["token_value"], line=name_tok["line"]))
                if self.cur.is_type("CLOSE_BRACKET"):
                    self.cur.consume()
                else:
                    self.err("Missing ']' — INVALID_ARRAY_DECL")
                    arr.add(ASTNode("ErrorNode", value="INVALID_ARRAY_DECL", line=name_tok["line"]))
                node.add(arr)

            if self.cur.is_type("OPERATOR") and self.cur.peek()["token_value"] == "=":
                op = self.cur.consume()
                asgn = ASTNode("AssignExprNode", value="=", line=op["line"])
                if self.cur.is_type("OPEN_BRACE"):
                    # Array or aggregate initializer list {1, 2, 3}
                    init_node = ASTNode("InitListNode", value="{...}", line=op["line"])
                    self.cur.consume()
                    while not self.cur.done() and not self.cur.is_type("CLOSE_BRACE", "SEMICOLON"):
                        init_node.add(ASTNode("ExprNode", value=self.cur.consume()["token_value"], line=op["line"]))
                    if self.cur.is_type("CLOSE_BRACE"):
                        self.cur.consume()
                    asgn.add(init_node)
                else:
                    # Track whether the last consumed RHS token was a "value" (identifier/literal)
                    # so we can detect two consecutive values with no operator = missing semicolon.
                    last_was_value = False
                    while not self.cur.done() and not self.cur.is_type("SEMICOLON", "CLOSE_BRACE"):
                        cur_tok = self.cur.peek()
                        if cur_tok is None:
                            break
                        cur_type  = cur_tok["token_type"]
                        cur_val   = cur_tok["token_value"]
                        # Break on explicit keyword/type boundaries
                        if cur_val in TYPE_KW or cur_val in ("return", "cout", "cin", "if", "for", "while", "else", "switch"):
                            self.err(f"Missing ';' — MISSING_SEMICOLON at line {op['line']}")
                            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=op['line']))
                            break
                        cur_is_value = cur_type in ("IDENTIFIER", "INTEGER", "FLOAT", "STRING", "CHAR")
                        # Two consecutive value tokens with no operator between them → new statement
                        if last_was_value and cur_is_value:
                            self.err(f"Missing ';' — MISSING_SEMICOLON at line {op['line']}")
                            node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=op['line']))
                            break
                        r = self.cur.consume()
                        asgn.add(ASTNode("ExprNode", value=r["token_value"], line=r["line"]))
                        # Operators reset the "last was value" flag; values set it
                        if cur_is_value:
                            last_was_value = True
                        elif cur_type != "WHITESPACE":
                            last_was_value = False
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

        last_was_value = False
        consumed_any = False
        while not self.cur.done() and not self.cur.is_type("SEMICOLON", "CLOSE_BRACE", "OPEN_BRACE"):
            cur_tok = self.cur.peek()
            if cur_tok is None:
                break
            cur_type = cur_tok["token_type"]
            cur_val  = cur_tok["token_value"]
            # TYPE_KW and control keywords always start a new statement (break only after at least 1 token consumed!)
            if consumed_any and (cur_val in TYPE_KW or cur_val in ("return", "if", "for", "while", "else", "switch")):
                self.err("Missing ';' — MISSING_SEMICOLON")
                node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=cur_tok["line"]))
                break
            # cout/cin only break mid-expression (not when they START one)
            if last_was_value and cur_val in ("cout", "cin"):
                self.err("Missing ';' — MISSING_SEMICOLON")
                node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=cur_tok["line"]))
                break
            cur_is_value = cur_type in ("IDENTIFIER", "INTEGER", "FLOAT", "STRING", "CHAR")
            # Two consecutive value tokens without an operator between them = new statement start
            if last_was_value and cur_is_value:
                self.err("Missing ';' — MISSING_SEMICOLON")
                node.add(ASTNode("ErrorNode", value="MISSING_SEMICOLON", line=cur_tok["line"]))
                break
            tok = self.cur.consume()
            consumed_any = True
            node.add(ASTNode("ExprNode", value=tok["token_value"], line=tok["line"]))
            if cur_is_value:
                last_was_value = True
            elif cur_type != "WHITESPACE":
                last_was_value = False

        if self.cur.is_type("SEMICOLON"):
            self.cur.consume()
        elif not self.cur.is_type("CLOSE_BRACE", "OPEN_BRACE"):
            if not consumed_any and not self.cur.done():
                self.cur.consume()
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


def build_ast(tokens_or_code):
    """
    tokens_or_code : list of token dicts OR raw C++ code string
    returns        : (ASTNode root, list of parse error strings)
    """
    if isinstance(tokens_or_code, str):
        from lexer import MASTER_REGEX, CPP_KEYWORDS
        token_rows = []
        token_index = 0
        line = 1
        line_start = 0
        for mo in MASTER_REGEX.finditer(tokens_or_code):
            kind = mo.lastgroup
            value = mo.group()
            col = mo.start() - line_start + 1
            if kind == "NEWLINE":
                line += 1
                line_start = mo.end()
                continue
            if kind == "WHITESPACE":
                continue
            if kind == "IDENTIFIER" and value in CPP_KEYWORDS:
                kind = "KEYWORD"
            token_rows.append({
                "token_index": token_index, "token_type": kind,
                "token_value": value, "line": line, "column": col
            })
            token_index += 1
    else:
        token_rows = tokens_or_code

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


# ============================================================================
# DEV-C++ / GCC (MINGW) COMPILER DIAGNOSTIC ENGINE & ERROR CLASSIFICATION
# ============================================================================

KEYWORD_TYPO_MAP = {
    "itn": "int",
    "intt": "int",
    "interger": "int",
    "flot": "float",
    "doubel": "double",
    "viod": "void",
    "charactor": "char",
    "charector": "char",
    "boolen": "bool",
    "boolean": "bool",
    "prinft": "printf",
    "prntf": "printf",
    "print_f": "printf",
    "scnf": "scanf",
    "scan_f": "scanf",
    "reutrn": "return",
    "retrun": "return",
    "retun": "return",
    "cuto": "cout",
    "coutt": "cout",
    "cot": "cout",
    "coot": "cout",
    "cinn": "cin",
    "ciin": "cin",
    "cinp": "cin",
    "ednl": "endl",
    "endll": "endl",
    "end1": "endl",
    "whlie": "while",
    "wile": "while",
    "fro": "for",
    "fopr": "for",
    "calss": "class",
    "clas": "class",
    "incldue": "include",
    "inclue": "include",
    "inculde": "include",
}

BUILTIN_IDENTIFIERS = {
    "cout", "cin", "cerr", "clog", "endl", "flush", "ws",
    "std", "string", "vector", "map", "set", "list", "array",
    "NULL", "nullptr", "true", "false",
    "main", "printf", "scanf", "fprintf", "fscanf", "sprintf",
    "malloc", "calloc", "realloc", "free", "new", "delete",
    "sizeof", "typeof", "INT_MAX", "INT_MIN", "exit", "abort",
    "abs", "sqrt", "pow", "max", "min", "swap", "size", "length"
}

def analyze_gcc_errors(code_str, filename="main.cpp"):
    """
    Front-end syntax error detector that matches the exact behavior of Dev-C++ (MinGW GCC).
    Uses a stack for balanced (), {}, [], quotes, and comments.
    Parses declarations, statements, conditionals, loops, and expressions.
    Reports first error at exact line and column like GCC, then continues diagnostics.
    """
    import re
    lines = code_str.splitlines()
    diagnostics = []
    
    # ── 0. Stray unknown characters (e.g. '@', '$', '`') ─────────────────────
    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line)
        for m_stray in re.finditer(r'[@$`]', clean_line):
            col = m_stray.start() + 1
            stray_char = m_stray.group(0)
            diagnostics.append({
                "type": "LEXICAL_ERROR",
                "message": f"stray '{stray_char}' in program",
                "line": line_idx,
                "column": col,
                "severity": "ERROR",
                "snippet": line.strip(),
                "suggestion": f"Remove invalid character '{stray_char}'.",
                "alternatives": [f"Remove '{stray_char}'"]
            })

    # ── 1. Stack check for brackets, quotes, and comments ────────────────────
    stack = []  # list of (char, line, col)
    in_block_comment = False
    comment_start = (0, 0)
    
    for line_idx, line in enumerate(lines, 1):
        col = 1
        i = 0
        while i < len(line):
            ch = line[i]
            col = i + 1
            
            if in_block_comment:
                if i + 1 < len(line) and line[i:i+2] == "*/":
                    in_block_comment = False
                    i += 2
                    continue
                i += 1
                continue
                
            # Line comment
            if i + 1 < len(line) and line[i:i+2] == "//":
                break
                
            # Block comment start
            if i + 1 < len(line) and line[i:i+2] == "/*":
                in_block_comment = True
                comment_start = (line_idx, col)
                i += 2
                continue
                
            # String literal
            if ch == '"':
                str_start_col = col
                i += 1
                escaped = False
                closed = False
                while i < len(line):
                    c = line[i]
                    if escaped:
                        escaped = False
                    elif c == '\\':
                        escaped = True
                    elif c == '"':
                        closed = True
                        i += 1
                        break
                    i += 1
                if not closed:
                    diagnostics.append({
                        "type": "UNTERMINATED_STRING",
                        "message": 'missing terminating " character',
                        "line": line_idx,
                        "column": str_start_col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": 'Add closing double quote " at end of string literal.',
                        "alternatives": ['Close string literal with "', 'Use \\n for multi-line string']
                    })
                continue

            # Char literal
            if ch == "'":
                char_start_col = col
                i += 1
                closed = False
                while i < len(line):
                    c = line[i]
                    if c == "'":
                        closed = True
                        i += 1
                        break
                    i += 1
                if not closed:
                    diagnostics.append({
                        "type": "UNTERMINATED_CHAR",
                        "message": "missing terminating \'\'\' character",
                        "line": line_idx,
                        "column": char_start_col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": "Add closing single quote at end of char literal.",
                        "alternatives": ["Close char literal with single quote"]
                    })
                continue

            # Brackets balance stack
            if ch in ('(', '{', '['):
                stack.append((ch, line_idx, col))
            elif ch == ')':
                if stack and stack[-1][0] == '(':
                    stack.pop()
                elif stack and stack[-1][0] == '{':
                    diagnostics.append({
                        "type": "UNMATCHED_PARANTHESES",
                        "message": "expected '}' before ')' token",
                        "line": line_idx,
                        "column": col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": "Check matching parenthesis or brace boundaries.",
                        "alternatives": ["Close '(' with ')' before '}'", "Recheck opening brace '{'"]
                    })
                else:
                    diagnostics.append({
                        "type": "UNMATCHED_PARANTHESES",
                        "message": "extra ')' before token",
                        "line": line_idx,
                        "column": col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": "Remove unmatched closing parenthesis ')'.",
                        "alternatives": ["Remove extra ')'", "Add corresponding opening '(' before expression"]
                    })
            elif ch == '}':
                if stack and stack[-1][0] == '{':
                    stack.pop()
                elif stack and stack[-1][0] == '(':
                    diagnostics.append({
                        "type": "UNMATCHED_BRACE",
                        "message": "expected ')' before '}' token",
                        "line": line_idx,
                        "column": col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": "Close open parenthesis before closing curly brace '}'.",
                        "alternatives": ["Add ')' before '}'", "Verify block structure"]
                    })
                else:
                    diagnostics.append({
                        "type": "UNMATCHED_BRACE",
                        "message": "extra '}' before token",
                        "line": line_idx,
                        "column": col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": "Remove extra closing brace '}'.",
                        "alternatives": ["Remove extra '}'", "Check if previous block was closed early"]
                    })
            elif ch == ']':
                if stack and stack[-1][0] == '[':
                    stack.pop()
                else:
                    diagnostics.append({
                        "type": "INVALID_ARRAY_DECL",
                        "message": "extra ']' before token",
                        "line": line_idx,
                        "column": col,
                        "severity": "ERROR",
                        "snippet": line.strip(),
                        "suggestion": "Remove unmatched bracket ']'.",
                        "alternatives": ["Remove extra ']'"]
                    })
            i += 1

    if in_block_comment:
        diagnostics.append({
            "type": "UNTERMINATED_COMMENT",
            "message": "unterminated comment '/*'",
            "line": comment_start[0],
            "column": comment_start[1],
            "severity": "ERROR",
            "snippet": lines[comment_start[0]-1].strip() if 1 <= comment_start[0] <= len(lines) else "",
            "suggestion": "Add matching '*/' to terminate multi-line comment.",
            "alternatives": ["Add '*/' at end of comment"]
        })

    while stack:
        bracket, s_line, s_col = stack.pop()
        expected = '}' if bracket == '{' else ')' if bracket == '(' else ']'
        etype = "UNMATCHED_BRACE" if bracket == '{' else "UNMATCHED_PARANTHESES" if bracket == '(' else "INVALID_ARRAY_DECL"
        last_line_idx = len(lines)
        last_line_len = len(lines[-1]) if lines else 1
        diagnostics.append({
            "type": etype,
            "message": f"expected '{expected}' at end of input",
            "line": last_line_idx,
            "column": max(1, last_line_len + 1),
            "severity": "ERROR",
            "snippet": lines[-1].strip() if lines else "",
            "suggestion": f"Add missing closing '{expected}' to balance '{bracket}' opened at line {s_line}:{s_col}.",
            "alternatives": [f"Add '{expected}' at end of function or block", f"Check scope opened at line {s_line}"]
        })

    # ── 2. Misspelled Keywords ───────────────────────────────────────────────
    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line)
        for word in re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', clean_line):
            if word in KEYWORD_TYPO_MAP:
                col = line.find(word) + 1
                correction = KEYWORD_TYPO_MAP[word]
                diagnostics.append({
                    "type": "MISSPELLED_KEYWORD",
                    "message": f"'{word}' was not declared in this scope; did you mean '{correction}'?",
                    "line": line_idx,
                    "column": col,
                    "severity": "ERROR",
                    "snippet": line.strip(),
                    "suggestion": f"Replace misspelled '{word}' with '{correction}'.",
                    "alternatives": [f"Correct spelling to '{correction}'", f"Declare '{word}' as a local variable"]
                })

    # ── 3. Missing #include Directives ─────────────────────────────────────────
    has_iostream = any("#include" in l and "iostream" in l for l in lines)
    has_stdio = any("#include" in l and ("stdio.h" in l or "cstdio" in l) for l in lines)
    has_string = any("#include" in l and ("string" in l or "iostream" in l) for l in lines)

    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line)
        if not has_iostream and re.search(r'\b(cout|cin|endl)\b', clean_line):
            m = re.search(r'\b(cout|cin|endl)\b', clean_line)
            col = m.start() + 1
            tok = m.group(1)
            diagnostics.append({
                "type": "MISSING_INCLUDE",
                "message": f"'{tok}' was not declared in this scope; did you mean '#include <iostream>'?",
                "line": line_idx,
                "column": col,
                "severity": "ERROR",
                "snippet": line.strip(),
                "suggestion": "Add '#include <iostream>' and 'using namespace std;' at the beginning of the file.",
                "alternatives": ["Add '#include <iostream>'", "Use C-style I/O: '#include <cstdio>' and printf()"]
            })
            has_iostream = True

        if not has_stdio and not has_iostream and re.search(r'\b(printf|scanf)\b', clean_line):
            m = re.search(r'\b(printf|scanf)\b', clean_line)
            col = m.start() + 1
            tok = m.group(1)
            diagnostics.append({
                "type": "MISSING_INCLUDE",
                "message": f"'{tok}' was not declared in this scope; did you mean '#include <cstdio>'?",
                "line": line_idx,
                "column": col,
                "severity": "ERROR",
                "snippet": line.strip(),
                "suggestion": "Add '#include <cstdio>' at the beginning of the file.",
                "alternatives": ["Add '#include <cstdio>'", "Add '#include <stdio.h>'"]
            })
            has_stdio = True

    # ── 4. Undeclared Variables ───────────────────────────────────────────────
    declared_vars = set(BUILTIN_IDENTIFIERS)
    for m in re.finditer(r'\b(?:int|float|double|char|bool|void|auto|string|long|short|unsigned|signed)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', code_str):
        declared_vars.add(m.group(1))

    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line).strip()
        m_assign = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', clean_line)
        if m_assign:
            var = m_assign.group(1)
            if var not in declared_vars and var not in KEYWORD_TYPO_MAP:
                col = line.find(var) + 1
                diagnostics.append({
                    "type": "UNDECLARED_IDENTIFIER",
                    "message": f"'{var}' was not declared in this scope",
                    "line": line_idx,
                    "column": col,
                    "severity": "ERROR",
                    "snippet": line.strip(),
                    "suggestion": f"Declare variable '{var}' before use, e.g. 'int {var} = 0;'.",
                    "alternatives": [f"Declare as: int {var} = 0;", f"Declare as: auto {var} = ...;", "Check for typographical error"]
                })

    # ── 5. Wrong Operator ('=' in conditions) ─────────────────────────────────
    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line)
        m_cond = re.search(r'\b(if|while)\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^=;)]+)\s*\)', clean_line)
        if m_cond:
            col = clean_line.find("=") + 1
            var_name = m_cond.group(2)
            val = m_cond.group(3).strip()
            diagnostics.append({
                "type": "WRONG_OPERATOR",
                "message": "suggest parentheses around assignment used as truth value [-Wparentheses]; did you mean '=='?",
                "line": line_idx,
                "column": col,
                "severity": "WARNING",
                "snippet": line.strip(),
                "suggestion": f"Change '=' to '==' for comparison: '{var_name} == {val}'.",
                "alternatives": [f"Use '==' comparison: if ({var_name} == {val})", f"Explicit assignment: if (({var_name} = {val}) != 0)"]
            })

    # ── 6. Missing quotes in printf ───────────────────────────────────────────
    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line)
        m_pf = re.search(r'\bprintf\s*\(\s*([a-zA-Z0-9_ ]+)\s*\)\s*;', clean_line)
        if m_pf:
            arg = m_pf.group(1).strip()
            if ' ' in arg and not (arg.startswith('"') and arg.endswith('"')):
                col = clean_line.find(arg) + 1
                diagnostics.append({
                    "type": "MISSING_PRINTF_QUOTES",
                    "message": "missing quotes in printf format string",
                    "line": line_idx,
                    "column": col,
                    "severity": "ERROR",
                    "snippet": line.strip(),
                    "suggestion": f'Enclose string literal in quotes: printf("{arg}");',
                    "alternatives": [f'printf("{arg}");', 'Pass a valid char* buffer or std::string']
                })

    # ── 7. Array Declaration Missing Bracket ──────────────────────────────────
    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line)
        if '[' in clean_line and ']' not in clean_line and ';' in clean_line:
            col = clean_line.find(';') + 1
            diagnostics.append({
                "type": "INVALID_ARRAY_DECL",
                "message": "expected ']' before ';' token",
                "line": line_idx,
                "column": col,
                "severity": "ERROR",
                "snippet": line.strip(),
                "suggestion": "Add ']' to close the array subscript before ';'.",
                "alternatives": ["Add ']' before ';'", "Specify valid array size: [N]"]
            })

    # ── 8. Missing Semicolon ──────────────────────────────────────────────────
    for line_idx, line in enumerate(lines, 1):
        clean_line = re.sub(r'//.*', '', line).strip()
        if not clean_line or clean_line.startswith("#") or clean_line.startswith("/*") or clean_line.startswith("*"):
            continue
        if clean_line.endswith(";") or clean_line.endswith("{") or clean_line.endswith("}") or clean_line.endswith(":"):
            continue
        if clean_line in ("{ ", "}", "{"):
            continue
        if re.match(r'^(if|else|while|for|switch|do)\b', clean_line):
            continue
        if re.match(r'^(public|private|protected)\s*:', clean_line):
            continue
        if re.match(r'^(template\s*<.*>)?\s*(inline\s+|static\s+)?(int|float|double|char|bool|void|auto)\b.*[)]\s*$', clean_line):
            continue
        if re.search(r'[a-zA-Z0-9_]', clean_line):
            col = len(line.rstrip()) + 1
            next_token = "newline"
            if line_idx < len(lines):
                next_clean = re.sub(r'//.*', '', lines[line_idx]).strip()
                if next_clean:
                    first_tok = next_clean.split()[0]
                    next_token = f"'{first_tok}'"
            diagnostics.append({
                "type": "MISSING_SEMICOLON",
                "message": f"expected ';' before {next_token} token",
                "line": line_idx,
                "column": col,
                "severity": "ERROR",
                "snippet": line.strip(),
                "suggestion": f"Add missing semicolon ';' at end of line {line_idx}.",
                "alternatives": ["Add ';' at statement end", "Combine statements with comma operator if applicable"]
            })

    # Format GCC diagnostics string
    for d in diagnostics:
        line_num = d["line"]
        col_num = d["column"]
        sev = d["severity"].lower()
        msg = d["message"]
        snippet = d.get("snippet", "")
        ln_str = f"{line_num:4d} | "
        pad = " " * (len(ln_str) + max(0, col_num - 1))
        d["gcc_formatted"] = f"{filename}:{line_num}:{col_num}: {sev}: {msg}\n{ln_str}{snippet}\n{pad}^"

    return diagnostics


def format_dev_cpp_log(diagnostics, filename="main.cpp"):
    """Format complete Dev-C++ / MinGW GCC compile log."""
    lines = [
        "-------------------- Compiler: MinGW GCC --------------------",
        "Compiler Build: g++.exe -Wall -std=c++20",
        f"File Target: {filename}",
        ""
    ]
    if not diagnostics:
        lines.append("Compilation successful: 0 errors, 0 warnings.")
        lines.append("Output binary created: main.exe (exit status: 0)")
    else:
        for d in diagnostics:
            lines.append(d.get("gcc_formatted", f"{filename}:{d.get('line',1)}:{d.get('column',1)}: error: {d.get('message')}"))
            lines.append("")
        err_count = sum(1 for d in diagnostics if d.get("severity") == "ERROR")
        warn_count = sum(1 for d in diagnostics if d.get("severity") == "WARNING")
        lines.append(f"Compilation failed with {err_count} error(s), {warn_count} warning(s).")
    lines.append("=" * 60)
    return "\n".join(lines)


def run_dev_cpp_gcc_diagnostics(code_or_tokens, filename="main.cpp"):
    """Unified interface for running Dev-C++ GCC diagnostics."""
    if isinstance(code_or_tokens, str):
        code_str = code_or_tokens
    else:
        lines = []
        cur_line = 1
        line_buf = []
        for t in code_or_tokens:
            while t.get("line", 1) > cur_line:
                lines.append(" ".join(line_buf))
                line_buf = []
                cur_line += 1
            line_buf.append(t.get("token_value", ""))
        if line_buf:
            lines.append(" ".join(line_buf))
        code_str = "\n".join(lines)

    diags = analyze_gcc_errors(code_str, filename=filename)
    return diags
