#!/usr/bin/env python3
"""
syntax_error_augmentor.py

1) Dataset augmentation (correct + injected syntax errors) for C++ source files.
2) Syntax error diagnosis and error-class mapping from arbitrary code.

Usage:
    # augment a folder of C++ source files into an error-labeled dataset
    python3 syntax_error_augmentor.py augment --input ./cpp_src --output ./augmented --variants 5

    # diagnose a file
    python3 syntax_error_augmentor.py diagnose --file ./test1.cpp

    # diagnose inline code snippet
    python3 syntax_error_augmentor.py diagnose --code "int main() { return 0 }"

Output:
    - augmented files in output folder with names <origname>__<class>__<idx>.cpp
    - metadata CSV for the produced examples
"""

import argparse
import csv
import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ERROR_CLASSES = [
    'missing_semicolon',
    'unmatched_braces',
    'missing_parentheses',
    'invalid_keyword',
    'missing_return_statement',
    'type_mismatch',
    'extra_token',
    'unknown_identifier',
]

CPP_KEYWORDS = {
    'alignas','alignof','and','and_eq','asm','auto','bitand','bitor','bool','break','case','catch','char',
    'char16_t','char32_t','class','compl','const','constexpr','const_cast','continue','decltype','default',
    'delete','do','double','dynamic_cast','else','enum','explicit','export','extern','false','float','for',
    'friend','goto','if','inline','int','long','mutable','namespace','new','noexcept','not','not_eq','nullptr',
    'operator','or','or_eq','private','protected','public','register','reinterpret_cast','return','short',
    'signed','sizeof','static','static_assert','static_cast','struct','switch','template','this','thread_local',
    'throw','true','try','typedef','typeid','typename','union','unsigned','using','virtual','void','volatile',
    'wchar_t','while','xor','xor_eq',
}

RARITY = 0.2


def _remove_random_semicolon(code):
    lines = code.splitlines()
    idxs = [i for i, line in enumerate(lines) if line.strip().endswith(';')]
    if not idxs:
        return code, False
    i = random.choice(idxs)
    lines[i] = lines[i].rstrip()[:-1]
    return '\n'.join(lines), True


def _delete_closing_brace(code):
    # remove one '}' from the end region
    close_idxs = [m.start() for m in re.finditer(r'\}', code)]
    if not close_idxs:
        return code, False
    i = random.choice(close_idxs)
    return code[:i] + code[i+1:], True


def _delete_opening_parenthesis(code):
    # remove one '(' from first function or if/for/while
    op_idxs = [m.start() for m in re.finditer(r'\(', code)]
    if not op_idxs:
        return code, False
    i = random.choice(op_idxs)
    return code[:i] + code[i+1:], True


def _replace_keyword(code):
    bad = {'if': 'iff', 'else': 'elsel', 'for': 'forr', 'while': 'whle', 'return': 'ret'}
    pat = re.compile(r"\b(" + '|'.join(re.escape(k) for k in bad.keys()) + r")\b")
    if not pat.search(code):
        return code, False
    return pat.sub(lambda m: bad[m.group(1)], code, count=1), True


def _remove_return(code):
    # remove first non-void return statement inside main/func
    m = re.search(r'\breturn\b[^;]*;', code)
    if not m:
        return code, False
    start, end = m.span()
    return code[:start] + code[end:], True


def _make_type_mismatch(code):
    # replace one int variable initialization with string literal or vice versa
    m = re.search(r'\b(int|float|double|char|long|short|bool)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;]+);', code)
    if not m:
        return code, False
    t, name, expr = m.groups()
    if '"' in expr or "'" in expr:
        rep = 'int {} = 3;'.format(name)
    else:
        rep = '{} {} = "bad";'.format(t, name)
    return code[:m.start()] + rep + code[m.end():], True


def _add_extra_token(code):
    # insert a random symbol in a random location
    insert_chars = ['$$', '??', '@', '##']
    # avoid adding inside string literal by simple approach
    pos = random.randrange(len(code) + 1)
    return code[:pos] + random.choice(insert_chars) + code[pos:], True


def _unknown_identifier(code):
    # replace a known identifier with unknown var
    names = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)
    names = [n for n in names if n not in CPP_KEYWORDS and len(n) > 1]
    if not names:
        return code, False
    name = random.choice(names)
    return re.sub(r'\b' + re.escape(name) + r'\b', name + 'z1', code, count=1), True


MUTATORS = {
    'missing_semicolon': _remove_random_semicolon,
    'unmatched_braces': _delete_closing_brace,
    'missing_parentheses': _delete_opening_parenthesis,
    'invalid_keyword': _replace_keyword,
    'missing_return_statement': _remove_return,
    'type_mismatch': _make_type_mismatch,
    'extra_token': _add_extra_token,
    'unknown_identifier': _unknown_identifier,
}


def generate_syntax_error_variants(code, max_variants=5, seed=42):
    random.seed(seed)
    variants = []
    tried = set()

    for err_cls, mut in MUTATORS.items():
        if len(variants) >= max_variants:
            break
        mutated, ok = mut(code)
        if not ok or mutated in tried:
            continue
        tried.add(mutated)
        variants.append((mutated, err_cls, f"Injected {err_cls}"))

    # if we still need more, apply random mutators with longer list
    while len(variants) < max_variants:
        err_cls = random.choice(list(MUTATORS.keys()))
        mutated, ok = MUTATORS[err_cls](code)
        if not ok or mutated in tried:
            continue
        tried.add(mutated)
        variants.append((mutated, err_cls, f"Injected {err_cls}"))

    return variants


def label_from_filename(filename):
    # take existing label from a name pattern, fallback to unknown
    base = Path(filename).stem
    parts = base.split('_')
    for p in reversed(parts):
        if p.isupper() and len(p) > 1:
            return p
    return 'unknown'


def augment_dataset(input_folder, output_folder, variants_each=3):
    os.makedirs(output_folder, exist_ok=True)
    metadata_rows = []

    for root, _, files in os.walk(input_folder):
        for fname in files:
            if not fname.endswith('.cpp'):
                continue
            src_path = Path(root) / fname
            try:
                code = src_path.read_text(encoding='utf-8', errors='ignore')
            except Exception as e:
                print('skip', src_path, 'error', e)
                continue

            base_label = label_from_filename(fname)
            # keep original as clean example
            out_name = f"{src_path.stem}__correct__0.cpp"
            out_path = Path(output_folder) / out_name
            out_path.write_text(code, encoding='utf-8')
            metadata_rows.append({'file': str(out_path), 'class': 'correct', 'orig': fname,
                                  'error_text': '', 'description': 'original source'})

            for idx, (wrong_code, err_cls, desc) in enumerate(generate_syntax_error_variants(code, variants_each, seed=hash(fname) & 0xffffffff)):
                out_name = f"{src_path.stem}__{err_cls}__{idx+1}.cpp"
                out_path = Path(output_folder) / out_name
                out_path.write_text(wrong_code, encoding='utf-8')
                metadata_rows.append({'file': str(out_path), 'class': err_cls, 'orig': fname,
                                      'error_text': desc, 'description': 'injected syntax error'})

    meta_path = Path(output_folder) / 'metadata.csv'
    with meta_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['file', 'class', 'orig', 'error_text', 'description'])
        writer.writeheader()
        for row in metadata_rows:
            writer.writerow(row)

    print(f"Augmented {len(metadata_rows)} examples to {output_folder} and metadata at {meta_path}")


SYNTAX_TO_CLASS = [
    (r"expected ';'|expected unqualified-id|expected declaration", 'missing_semicolon'),
    (r"expected '\)'|expected '('", 'missing_parentheses'),
    (r"expected '\}'|expected '}'", 'unmatched_braces'),
    (r"'if' was not declared in this scope|'for' was not declared", 'invalid_keyword'),
    (r"'return' was not declared in this scope|cannot return a value from function with void return type", 'missing_return_statement'),
    (r"cannot convert.*to.*|no matching function for call", 'type_mismatch'),
    (r"was not declared in this scope", 'unknown_identifier'),
    (r"expected primary-expression", 'extra_token'),
]


def parse_gcc_error_message(message):
    text = message.lower().replace('\n', ' ')
    for pat, cls in SYNTAX_TO_CLASS:
        if re.search(pat, text):
            return cls
    return 'unknown_syntax_error'


def diagnose_code(code):
    # try to use g++ if available
    with tempfile.TemporaryDirectory() as td:
        temp_file = os.path.join(td, 'tmp.cpp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        cmd = ['g++', '-std=c++17', '-fsyntax-only', temp_file]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        except FileNotFoundError:
            res = None

    if res is None:
        return {'status': 'no_compiler', 'error_class': 'unknown', 'message': 'g++ not found on system'}

    if res.returncode == 0:
        return {'status': 'ok', 'error_class': 'none', 'message': 'No syntax error detected (g++)'}

    stderr = res.stderr.strip()
    err_cls = parse_gcc_error_message(stderr)
    suggestion = suggest_fix(code, err_cls, stderr)
    return {'status': 'error', 'error_class': err_cls, 'message': stderr, 'suggestion': suggestion}


def suggest_fix(code, error_class, raw_message=''):
    hints = {
        'missing_semicolon': 'Add a semicolon at the end of the failing statement. Look at the line indicated by the compiler message.',
        'unmatched_braces': 'Check matching braces { and }. Add a missing } or remove extra bracket.',
        'missing_parentheses': 'Add missing parentheses near control structures or function calls.',
        'invalid_keyword': 'Replace invalid keyword with the correct C++ keyword (e.g., "if", "for", "while").',
        'missing_return_statement': 'Add a return statement in non-void functions or adjust function return type.',
        'type_mismatch': 'Fix type conversion errors, ensure assignments and calls use compatible types.',
        'unknown_identifier': 'Declare the variable/function or correct its name.',
        'extra_token': 'Remove stray characters or operators from the source.',
        'unknown_syntax_error': 'Inspect compiler message for details and check punctuation around reported location.',
    }
    return hints.get(error_class, 'No automated suggestion available. Please inspect compiler output.')


def main():
    parser = argparse.ArgumentParser(description='Augment C++ dataset and diagnose syntax errors')
    subparsers = parser.add_subparsers(dest='command', required=True)

    p_aug = subparsers.add_parser('augment', help='Generate augmentation dataset with syntax errors')
    p_aug.add_argument('--input', '-i', required=True, help='Input folder with C++ files')
    p_aug.add_argument('--output', '-o', required=True, help='Output folder for augmented files')
    p_aug.add_argument('--variants', '-v', type=int, default=4, help='Number of error variants per file')

    p_diag = subparsers.add_parser('diagnose', help='Diagnose syntax errors in a C++ snippet or file')
    group = p_diag.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='C++ source file to diagnose')
    group.add_argument('--code', '-c', help='Inline C++ source code string to diagnose')

    args = parser.parse_args()

    if args.command == 'augment':
        augment_dataset(args.input, args.output, variants_each=args.variants)
        return

    if args.command == 'diagnose':
        if args.file:
            source = Path(args.file).read_text(encoding='utf-8', errors='ignore')
        else:
            source = args.code
        # first sanitize windows line endings
        source = source.replace('\r\n', '\n')
        result = diagnose_code(source)
        print('status:', result.get('status'))
        print('error_class:', result.get('error_class'))
        print('message:')
        print(result.get('message'))
        if 'suggestion' in result:
            print('suggestion:', result['suggestion'])
        return


if __name__ == '__main__':
    main()
