import os
import re
import sys
import random
import argparse
from collections import defaultdict
from itertools import cycle


VAR_NAMES = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "count", "total", "sum", "index", "value", "result", "output", "input",
    "data", "temp", "buffer", "flag", "status", "code", "num", "val",
    "score", "rate", "size", "len", "pos", "offset", "limit", "threshold",
    "counter", "tracker", "accumulator", "product", "quotient", "remainder",
    "minimum", "maximum", "average", "median", "variance", "difference",
    "x", "y", "z", "a", "b", "c", "d", "e", "f", "g", "h", "k",
    "n", "m", "p", "q", "r", "s", "t", "u", "v", "w",
    "number", "integer", "decimal", "fraction", "digit", "character",
    "weight", "height", "width", "depth", "distance", "speed", "time",
    "price", "cost", "profit", "loss", "balance", "amount", "quantity",
]

FUNC_NAMES = [
    "compute", "calculate", "process", "evaluate", "execute", "perform",
    "run", "start", "init", "setup", "configure", "update", "refresh",
    "display", "print", "show", "render", "draw", "paint",
    "read", "write", "load", "save", "store", "retrieve", "fetch",
    "check", "verify", "validate", "test", "scan", "search", "find",
    "sort", "filter", "map", "reduce", "transform", "convert",
    "add", "remove", "insert", "delete", "push", "pop", "enqueue", "dequeue",
    "open", "close", "connect", "disconnect", "send", "receive",
    "encode", "decode", "compress", "decompress", "encrypt", "decrypt",
    "reset", "clear", "flush", "drain", "fill", "copy", "move", "swap",
    "foo", "bar", "baz", "qux", "main", "helper", "util", "handler",
    "doTask", "runJob", "execStep", "applyRule", "buildResult",
]

TYPE_NAMES = ["int", "float", "double", "char", "long", "short", "bool"]

ARRAY_NAMES = [
    "arr", "list", "seq", "vec", "buf", "stack", "queue", "heap",
    "table", "grid", "matrix", "set", "bag", "pool", "cache",
    "items", "values", "numbers", "scores", "data", "records", "entries",
]

VAR_DECL_PATTERN = re.compile(
    r'\b(int|float|double|char|long|short|bool)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b'
)

FUNC_DEF_PATTERN = re.compile(
    r'\b(int|float|double|char|long|short|bool|void)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
)

ARRAY_DECL_PATTERN = re.compile(
    r'\b(int|float|double|char|long|short|bool)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\['
)


def extract_names(code):
    """Extract all variable and function names from code."""
    var_names = set()
    func_names = set()
    array_names = set()

    for match in VAR_DECL_PATTERN.finditer(code):
        var_names.add(match.group(2))

    for match in FUNC_DEF_PATTERN.finditer(code):
        func_names.add(match.group(2))

    for match in ARRAY_DECL_PATTERN.finditer(code):
        array_names.add(match.group(2))

    return var_names, func_names, array_names


def build_substitution_map(var_names, func_names, array_names, seed=42):
    """Build a random substitution map for all names."""
    random.seed(seed)
    sub_map = {}

   
    used = set()

    reserved = {
        "int", "float", "double", "char", "long", "short", "bool", "void",
        "if", "else", "while", "for", "return", "main", "include",
        "using", "namespace", "std", "cin", "cout", "endl",
        "#", "0", "1", "true", "false", "NULL", "nullptr",
    }

    def pick(pool):
        pool_copy = [p for p in pool if p not in used and p not in reserved]
        if not pool_copy:
            name = f"var_{random.randint(100,999)}"
            used.add(name)
            return name
        choice = random.choice(pool_copy)
        used.add(choice)
        return choice

    for name in array_names:
        if name not in reserved:
            sub_map[name] = pick(ARRAY_NAMES)

    for name in func_names:
        if name not in reserved:
            sub_map[name] = pick(FUNC_NAMES)

    for name in var_names:
        if name not in reserved and name not in sub_map:
            sub_map[name] = pick(VAR_NAMES)

    return sub_map


def apply_substitution(code, sub_map):
    """Apply name substitutions to code, replacing whole words only."""
    if not sub_map:
        return code

    sorted_keys = sorted(sub_map.keys(), key=len, reverse=True)

    for old_name in sorted_keys:
        new_name = sub_map[old_name]
        code = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, code)

    return code


def generate_variant(code, variant_index):
    """Generate one variant of code with different name substitutions."""
    var_names, func_names, array_names = extract_names(code)
    sub_map = build_substitution_map(
        var_names, func_names, array_names,
        seed=variant_index * 137 + 42 
    )
    return apply_substitution(code, sub_map)



def discover_files(input_folder):
    """Return dict: {CLASS_NAME: [filepath, ...]}"""
    class_files = defaultdict(list)

    for fname in os.listdir(input_folder):
        if not fname.endswith(".cpp"):
            continue
        fpath = os.path.join(input_folder, fname)

        
        parts = fname.replace(".cpp", "").split("_")

  
        label = None
        for i, part in enumerate(parts):
            if part.isdigit() or (i == 0 and not part.isdigit()):
                continue
            if not part.isdigit():

                label = "_".join(parts[i:])
                break


        if label is None or not label.isupper():
      
            for i, part in enumerate(parts):
                if part.isupper() or (len(part) > 2 and part[0].isupper()):
                    label = "_".join(parts[i:])
                    break

        if label:
            class_files[label].append(fpath)

    return class_files




def augment(input_folder, output_folder, target_total):
    os.makedirs(output_folder, exist_ok=True)

    print(f"Scanning: {input_folder}")
    class_files = discover_files(input_folder)

    if not class_files:
        print("ERROR: No .cpp files found or could not parse class labels.")
        print("Make sure files follow naming: aug_N_CLASSNAME.cpp")
        return

    num_classes = len(class_files)
    print(f"Found {num_classes} classes:")
    for cls, files in sorted(class_files.items()):
        print(f"  {cls}: {len(files)} files")

    total_existing = sum(len(v) for v in class_files.values())
    print(f"\nTotal existing files: {total_existing}")
    print(f"Target total: {target_total}")

    if target_total <= total_existing:
        print(f"Already have {total_existing} files. Nothing to do.")
        return


    target_per_class = target_total // num_classes
    print(f"Target per class: {target_per_class}")

    total_generated = 0

    for class_label, files in sorted(class_files.items()):
        current_count = len(files)
        needed = target_per_class - current_count

        if needed <= 0:
            print(f"  {class_label}: already has {current_count}, skipping")
            continue

        print(f"  {class_label}: generating {needed} more files...")

        source_cycle = cycle(files)
        generated_for_class = 0

        for i in range(needed):
            source_path = next(source_cycle)

            try:
                with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
                    original_code = f.read()
            except Exception as e:
                print(f"    Warning: could not read {source_path}: {e}")
                continue


            variant_code = generate_variant(original_code, variant_index=current_count + i + 1000)

       
            new_filename = f"var{i}_{current_count + i}_{class_label}.cpp"
            new_filepath = os.path.join(output_folder, new_filename)

            try:
                with open(new_filepath, "w", encoding="utf-8") as f:
                    f.write(variant_code)
                generated_for_class += 1
                total_generated += 1
            except Exception as e:
                print(f"    Warning: could not write {new_filepath}: {e}")

        print(f"    Done. {class_label} now has ~{current_count + generated_for_class} files")

    print(f"\n✅ Done! Generated {total_generated} new files.")
    print(f"   Output folder: {output_folder}")
    print(f"\nNext steps:")
    print(f"  1. Run your lexer on the new .cpp files to get new tokens")
    print(f"  2. Run ast_extractor.py on the combined tokens")
    print(f"  3. Re-run train.py")



def main():
    parser = argparse.ArgumentParser(description="Augment C++ error dataset via variable name substitution")
    parser.add_argument("input_folder", help="Folder containing existing .cpp files")
    parser.add_argument("output_folder", help="Folder to write new .cpp files into")
    parser.add_argument("--target", type=int, default=1000,
                        help="Target total number of files (default: 1000)")
    args = parser.parse_args()

    augment(args.input_folder, args.output_folder, args.target)


if __name__ == "__main__":
    main()