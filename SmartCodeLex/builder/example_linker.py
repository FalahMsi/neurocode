# builder/example_linker.py (نسخة مطورة نهائيًا)

import json, os, argparse
from typing import Dict, Any
from tqdm import tqdm

INPUT_PATH = "knowledge/example_bank.json"
OUTPUT_PATH = "knowledge/example_bank_advanced.json"
SKIPPED_LOG = "logs/skipped_examples.txt"

def extract_metadata(example_json: Dict[str, Any], include_raw: bool = True) -> Dict[str, Any]:
    calls, vars_, keywords = set(), set(), set()
    doc = ""
    param_count = 0
    return_type = ""
    max_depth = 0
    total_children = 0

    def recurse(node, depth=1):
        nonlocal doc, param_count, return_type, max_depth, total_children
        if depth > max_depth:
            max_depth = depth

        if isinstance(node, dict):
            total_children += 1
            node_type = node.get("type")

            # تحليل الاستدعاءات
            if node_type == "Call":
                for child in node.get("children", []):
                    if isinstance(child, dict) and child.get("type") in {"NameLoad", "AttributeLoad"}:
                        val = child.get("value")
                        if isinstance(val, str):
                            calls.add(val)

            elif node_type in {"NameLoad", "NameStore", "arg"}:
                val = node.get("value")
                if isinstance(val, str):
                    vars_.add(val)

            elif node_type == "keyword":
                val = node.get("value")
                if isinstance(val, str):
                    keywords.add(val)

            elif node_type == "arguments":
                args = node.get("children", [])
                param_count += sum(1 for arg in args if isinstance(arg, dict) and arg.get("type") == "arg")

            elif node_type == "Return":
                for child in node.get("children", []):
                    if isinstance(child, dict):
                        return_type = child.get("type", "")

            elif node_type == "Expr" and "children" in node:
                for gc in node["children"]:
                    if isinstance(gc, dict) and gc.get("type") == "Str":
                        doc_candidate = gc.get("value")
                        if isinstance(doc_candidate, str) and len(doc_candidate.strip()) > 10:
                            doc = doc_candidate.strip()

            for child in node.values():
                if isinstance(child, (dict, list)):
                    recurse(child, depth + 1)

        elif isinstance(node, list):
            for item in node:
                recurse(item, depth)

    recurse(example_json)

    metadata = {
        "type": example_json.get("type", "Unknown"),
        "value": example_json.get("value", ""),
        "doc": doc,
        "calls": sorted(calls),
        "vars": sorted(vars_),
        "keywords": sorted(keywords),
        "param_count": param_count,
        "return_type": return_type,
        "depth": max_depth,
        "child_count": total_children,
        "complexity_score": len(calls) + len(vars_) + len(keywords) + param_count + max_depth  # محسوب بذكاء
    }

    if include_raw:
        metadata["raw"] = example_json
    return metadata

def process_examples(input_path: str, output_path: str, include_raw: bool):
    if not os.path.exists(input_path):
        print(f"❌ الملف غير موجود: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        raw_bank = json.load(f)

    advanced_bank = {}
    skipped = []

    for eid, raw_str in tqdm(raw_bank.items(), desc="🔍 تحليل الأمثلة"):
        try:
            parsed = json.loads(raw_str)
            advanced_bank[eid] = extract_metadata(parsed, include_raw)
        except Exception as e:
            skipped.append((eid, str(e)))
            continue

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(advanced_bank, f, indent=2, ensure_ascii=False)

    if skipped:
        os.makedirs(os.path.dirname(SKIPPED_LOG), exist_ok=True)
        with open(SKIPPED_LOG, 'w', encoding='utf-8') as log:
            for eid, err in skipped:
                log.write(f"{eid}: {err}\n")
        print(f"⚠️ تم تخطي {len(skipped)} مثالًا. انظر {SKIPPED_LOG}")

    print(f"✅ تم حفظ {len(advanced_bank)} مثالًا محسنًا في: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="تحليل أمثلة AST وتحسين بياناتها")
    parser.add_argument('--input', type=str, default=INPUT_PATH, help="مسار ملف example_bank.json")
    parser.add_argument('--output', type=str, default=OUTPUT_PATH, help="مسار إخراج الملف المحسن")
    parser.add_argument('--no-raw', action='store_true', help="عدم حفظ الشكل الكامل لكل مثال (raw)")

    args = parser.parse_args()
    process_examples(args.input, args.output, include_raw=not args.no_raw)
