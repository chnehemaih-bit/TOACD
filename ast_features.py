import pandas as pd
import sys
from cpp_parser import ASTNode, Parser, build_ast



def walk(node, callback, depth=0):
    """DFS walk — calls callback(node, depth) for every node."""
    callback(node, depth)
    for child in node.children:
        walk(child, callback, depth + 1)


def collect_nodes(root):
    """Return flat list of (node, depth) for the whole tree."""
    result = []
    walk(root, lambda n, d: result.append((n, d)))
    return result




def extract_features(root, parse_errors):
    nodes = collect_nodes(root)

    def count(ntype):
        return sum(1 for n, _ in nodes if n.node_type == ntype)

    def count_error(val):
        return sum(1 for n, _ in nodes
                   if n.node_type == "ErrorNode" and n.value == val)

    num_function_decls  = count("FunctionDeclNode")
    num_var_decls       = count("VarDeclNode")
    num_assign_exprs    = count("AssignExprNode")
    num_array_decls     = count("ArrayDeclNode")
    num_if_stmts        = count("IfStmtNode")
    num_else_stmts      = count("ElseStmtNode")
    num_while_stmts     = count("WhileStmtNode")
    num_for_stmts       = count("ForStmtNode")
    num_return_stmts    = count("ReturnStmtNode")
    num_compound_stmts  = count("CompoundStmtNode")
    num_expr_stmts      = count("ExprStmtNode")
    total_nodes         = len(nodes)

    depths    = [d for _, d in nodes]
    max_depth = max(depths) if depths else 0
    avg_depth = round(sum(depths) / len(depths), 4) if depths else 0
    num_leaf_nodes = sum(1 for n, _ in nodes if len(n.children) == 0)

    error_invalid_assignment  = count_error("INVALID_ASSIGNMENT")
    error_unmatched_brace     = count_error("UNMATCHED_BRACE")
    error_unmatched_paren     = count_error("UNMATCHED_PARANTHESES")
    error_missing_semicolon   = count_error("MISSING_SEMICOLON")
    error_invalid_conditional = count_error("INVALID_CONDITIONAL")
    error_invalid_loop        = count_error("INVALID_LOOP")
    error_invalid_type        = count_error("INVALID_TYPE")
    error_invalid_array       = count_error("INVALID_ARRAY_DECL")
    error_invalid_func_decl   = count_error("INVALID_FUNCTION_DECL")
    total_error_nodes         = sum(1 for n, _ in nodes if n.node_type == "ErrorNode")

    scope_depth_max = 0
    compound_depths = [d for n, d in nodes if n.node_type == "CompoundStmtNode"]
    if compound_depths:
        scope_depth_max = max(compound_depths)

    has_orphan_else = 0
    def find_parent_types(root_node):
        """Build child→parent_type map."""
        mapping = {}
        def _walk(node):
            for child in node.children:
                mapping[id(child)] = node.node_type
                _walk(child)
        _walk(root_node)
        return mapping

    parent_map = find_parent_types(root)
    for n, _ in nodes:
        if n.node_type == "ElseStmtNode":
            parent_type = parent_map.get(id(n), "")
            if parent_type not in ("IfStmtNode", "CompoundStmtNode"):
                has_orphan_else = 1
                break

    func_missing_return = 0
    for n, _ in nodes:
        if n.node_type == "FunctionDeclNode":
            sub = collect_nodes(n)
            has_return = any(s.node_type == "ReturnStmtNode" for s, _ in sub)
            if not has_return:
                func_missing_return = 1
                break

    assign_in_condition = 0
    for n, _ in nodes:
        if n.node_type == "ConditionNode":
            sub = collect_nodes(n)
            if any(s.node_type == "AssignExprNode" for s, _ in sub):
                assign_in_condition = 1
                break

    nested_func_decl = 0
    for n, _ in nodes:
        if n.node_type == "FunctionDeclNode":
            sub = collect_nodes(n)
            if any(s.node_type == "FunctionDeclNode" for s, _ in sub[1:]):
                nested_func_decl = 1
                break

    return {
        "num_function_decls"       : num_function_decls,
        "num_var_decls"            : num_var_decls,
        "num_assign_exprs"         : num_assign_exprs,
        "num_array_decls"          : num_array_decls,
        "num_if_stmts"             : num_if_stmts,
        "num_else_stmts"           : num_else_stmts,
        "num_while_stmts"          : num_while_stmts,
        "num_for_stmts"            : num_for_stmts,
        "num_return_stmts"         : num_return_stmts,
        "num_compound_stmts"       : num_compound_stmts,
        "num_expr_stmts"           : num_expr_stmts,
        "total_nodes"              : total_nodes,
        "max_depth"                : max_depth,
        "avg_depth"                : avg_depth,
        "num_leaf_nodes"           : num_leaf_nodes,
        "error_invalid_assignment" : error_invalid_assignment,
        "error_unmatched_brace"    : error_unmatched_brace,
        "error_unmatched_paren"    : error_unmatched_paren,
        "error_missing_semicolon"  : error_missing_semicolon,
        "error_invalid_conditional": error_invalid_conditional,
        "error_invalid_loop"       : error_invalid_loop,
        "error_invalid_type"       : error_invalid_type,
        "error_invalid_array"      : error_invalid_array,
        "error_invalid_func_decl"  : error_invalid_func_decl,
        "total_error_nodes"        : total_error_nodes,
        "scope_depth_max"          : scope_depth_max,
        "has_orphan_else"          : has_orphan_else,
        "func_missing_return"      : func_missing_return,
        "assign_in_condition"      : assign_in_condition,
        "nested_func_decl"         : nested_func_decl,
    }



def main():
    input_csv  = sys.argv[1] if len(sys.argv) > 1 else "tokens.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "features.csv"

    print("=" * 60)
    print("  AST FEATURE EXTRACTOR")
    print("=" * 60)
    print(f"[INFO] Input  : {input_csv}")
    print(f"[INFO] Output : {output_csv}\n")

    df    = pd.read_csv(input_csv)
    files = df["file_name"].unique()
    print(f"[INFO] Files to process : {len(files)}\n")

    rows = []
    for i, fname in enumerate(files, 1):
        file_tokens = df[df["file_name"] == fname].to_dict("records")
        label       = file_tokens[0]["label"]

        ast_root, parse_errors = build_ast(file_tokens)

        feats = extract_features(ast_root, parse_errors)
        feats["file_name"] = fname
        feats["label"]     = label
        rows.append(feats)

        if i % 50 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] processed {fname}")

    out_df = pd.DataFrame(rows)
    cols   = ["file_name", "label"] + [c for c in out_df.columns
                                        if c not in ("file_name","label")]
    out_df = out_df[cols]
    out_df.to_csv(output_csv, index=False)

    print(f"\n[INFO] Features shape : {out_df.shape}")
    print(f"[INFO] Feature columns ({len(cols)-2}):")
    for c in cols[2:]:
        print(f"        - {c}")
    print(f"\n[INFO] Saved to {output_csv}")
    print("\n" + "=" * 60)
    print("  FEATURE EXTRACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()















