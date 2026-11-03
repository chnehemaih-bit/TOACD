import os
import re
import csv
import sys
from collections import defaultdict


CPP_KEYWORDS = {
    "int", "float", "double", "char", "bool", "void", "long", "short",
    "unsigned", "signed", "const", "static", "extern", "register", "volatile",
    "if", "else", "while", "for", "do", "switch", "case", "default",
    "break", "continue", "return", "goto",
    "class", "struct", "union", "enum", "typedef", "namespace", "using",
    "public", "private", "protected", "virtual", "override", "final",
    "new", "delete", "this", "nullptr", "NULL", "true", "false",
    "include", "define", "ifdef", "ifndef", "endif", "pragma",
    "template", "typename", "operator", "sizeof", "typeof",
    "try", "catch", "throw",
    "auto", "inline", "explicit", "friend", "mutable",
}


TOKEN_SPEC = [
    ("COMMENT",       r"//[^\n]*|/\*[\s\S]*?\*/"),
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

MASTER_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)


def extract_label(filename):
    """
    Extract class label from filename.
    Handles formats:
        aug_3_INVALID_ASSIGNMENT.cpp   → INVALID_ASSIGNMENT
        var0_51_MISSING_SEMICOLON.cpp  → MISSING_SEMICOLON
        INVALID_ASSIGNMENT_001.cpp     → INVALID_ASSIGNMENT
    """
    name = filename.replace(".cpp", "")
    parts = name.split("_")

   
    label_parts = []
    found = False
    for part in parts:
        if found:
            label_parts.append(part)
        elif part.isupper() and not part.isdigit():
            label_parts.append(part)
            found = True

    if label_parts:
        return "_".join(label_parts)

  
    return name.upper()


def tokenize_file(filepath):
    """
    Tokenize a single .cpp file.
    Returns list of dicts with keys:
        token_index, token_type, token_value, line, column
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception as e:
        print(f"  Warning: could not read {filepath}: {e}")
        return []

    tokens = []
    token_index = 0
    line = 1
    line_start = 0

    for mo in MASTER_REGEX.finditer(code):
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

        tokens.append({
            "token_index": token_index,
            "token_type": kind,
            "token_value": value,
            "line": line,
            "column": col,
        })
        token_index += 1

    return tokens


def strip_comments(code):
    """Remove // and /* */ comments before tokenizing."""

    code = re.sub(r"//[^\n]*", "", code)

    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    return code


def tokenize_file_clean(filepath):
    """Tokenize with comment stripping."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception as e:
        print(f"  Warning: could not read {filepath}: {e}")
        return []

    code = strip_comments(code)

    tokens = []
    token_index = 0
    line = 1
    line_start = 0

    for mo in MASTER_REGEX.finditer(code):
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

        tokens.append({
            "token_index": token_index,
            "token_type": kind,
            "token_value": value,
            "line": line,
            "column": col,
        })
        token_index += 1

    return tokens


def run_lexer(cpp_folder, output_csv):
    """Process all .cpp files in folder and write tokens.csv."""


    cpp_files = sorted([
        f for f in os.listdir(cpp_folder)
        if f.endswith(".cpp")
    ])

    if not cpp_files:
        print(f"ERROR: No .cpp files found in {cpp_folder}")
        sys.exit(1)

    print(f"Found {len(cpp_files)} .cpp files in '{cpp_folder}'")
    print(f"Output: {output_csv}")
    print("Tokenizing...")


    class_counts = defaultdict(int)
    for fname in cpp_files:
        label = extract_label(fname)
        class_counts[label] += 1

    print(f"\nClass distribution:")
    for cls, count in sorted(class_counts.items()):
        print(f"  {cls}: {count} files")
    print()

    total_tokens = 0
    files_processed = 0
    files_failed = 0

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "file_name", "label",
            "token_index", "token_type", "token_value",
            "line", "column"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for fname in cpp_files:
            filepath = os.path.join(cpp_folder, fname)
            label = extract_label(fname)

            tokens = tokenize_file_clean(filepath)

            if not tokens:
                print(f"  Warning: no tokens from {fname}")
                files_failed += 1
                continue

            for tok in tokens:
                writer.writerow({
                    "file_name":    fname,
                    "label":        label,
                    "token_index":  tok["token_index"],
                    "token_type":   tok["token_type"],
                    "token_value":  tok["token_value"],
                    "line":         tok["line"],
                    "column":       tok["column"],
                })

            total_tokens += len(tokens)
            files_processed += 1

            if files_processed % 100 == 0:
                print(f"  Processed {files_processed}/{len(cpp_files)} files...")

    print(f"\n✅ Done!")
    print(f"   Files processed : {files_processed}")
    print(f"   Files failed    : {files_failed}")
    print(f"   Total tokens    : {total_tokens}")
    print(f"   Avg tokens/file : {total_tokens // max(files_processed, 1)}")
    print(f"   Output written  : {output_csv}")
    print(f"\nNext step:")
    print(f"   python3 ast_extractor.py {output_csv} features.csv")



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 lexer.py <cpp_folder> <output_csv>")
        print("Example: python3 lexer.py ./cpp_files tokens.csv")
        sys.exit(1)

    cpp_folder = sys.argv[1]
    output_csv = sys.argv[2]

    if not os.path.isdir(cpp_folder):
        print(f"ERROR: '{cpp_folder}' is not a valid folder")
        sys.exit(1)

    run_lexer(cpp_folder, output_csv)