# builder/smartcodelex_extractor.py (نسخة نهائية موحدة شاملة ذكية)

import json, os, argparse, sqlite3, re
from typing import Set, Any, List, Dict, Tuple
from collections import Counter
from tqdm import tqdm
from difflib import SequenceMatcher
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

# =================== المسارات ===================
AST_INPUT = "languages/python/python100k_train.json"
EXAMPLE_BANK_PATH = "knowledge/example_bank.json"
EXAMPLE_ADVANCED_PATH = "knowledge/example_bank_advanced.json"
CORE_UNITS_PATH = "core_units/core_units_python.json"
DB_PATH = "smartcodelex.db"

# =================== أدوات مساعدة ===================
def clean_word(word: str) -> str | None:
    if not isinstance(word, str): return None
    word = word.replace("_", " ").replace("-", " ").lower()
    word = re.sub(r'[^a-z\s]', '', word)
    return re.sub(r'\s+', ' ', word).strip() or None

def is_garbage_like(term: str, threshold: float = 0.6) -> bool:
    if not term or len(term) < 5: return False
    freq = Counter(term)
    return sum(c for _, c in freq.most_common(3)) / len(term) >= threshold

def suggest_concept_code(index: int) -> str:
    return f"C{str(index).zfill(4)}"

# =================== استخراج من AST ===================
def extract_terms_examples_docstrings(node: Any, terms: Set[str], examples: Dict[str, str], docstrings: Dict[str, str]):
    if isinstance(node, dict):
        val = node.get("value")
        node_type = node.get("type")
        if isinstance(val, str):
            word = clean_word(val)
            if word: terms.add(word)

        if node_type in {"Call", "FunctionDef"}:
            eid = f"E{len(examples)+1:05}"
            examples[eid] = json.dumps(node, ensure_ascii=False)

        if node_type == "FunctionDef":
            for child in node.get("children", []):
                if isinstance(child, dict) and child.get("type") == "Expr":
                    for gc in child.get("children", []):
                        if isinstance(gc, dict) and gc.get("type") == "Str":
                            doc = gc.get("value")
                            if isinstance(doc, str) and len(doc.strip()) > 10:
                                docstrings[val] = doc.strip()

        for v in node.values():
            if isinstance(v, (list, dict)):
                extract_terms_examples_docstrings(v, terms, examples, docstrings)
    elif isinstance(node, list):
        for item in node:
            extract_terms_examples_docstrings(item, terms, examples, docstrings)

# =================== تحليل الأمثلة ===================
def extract_metadata(example_json: Dict[str, Any]) -> Dict[str, Any]:
    calls, vars_, keywords = set(), set(), set()
    doc, param_count, return_type, max_depth, total_children = "", 0, "", 0, 0

    def recurse(node, depth=1):
        nonlocal doc, param_count, return_type, max_depth, total_children
        max_depth = max(max_depth, depth)
        if isinstance(node, dict):
            total_children += 1
            typ = node.get("type")
            if typ == "Call":
                for c in node.get("children", []):
                    if isinstance(c, dict) and c.get("type") in {"NameLoad", "AttributeLoad"}:
                        if isinstance(c.get("value"), str):
                            calls.add(c["value"])
            elif typ in {"NameStore", "NameLoad", "arg"}:
                if isinstance(node.get("value"), str):
                    vars_.add(node["value"])
            elif typ == "keyword":
                if isinstance(node.get("value"), str):
                    keywords.add(node["value"])
            elif typ == "arguments":
                param_count += sum(1 for arg in node.get("children", []) if isinstance(arg, dict) and arg.get("type") == "arg")
            elif typ == "Return":
                for c in node.get("children", []):
                    if isinstance(c, dict):
                        return_type = c.get("type", "")
            elif typ == "Expr":
                for gc in node.get("children", []):
                    if isinstance(gc, dict) and gc.get("type") == "Str":
                        val = gc.get("value")
                        if isinstance(val, str) and len(val.strip()) > 10:
                            doc = val.strip()
            for child in node.values():
                if isinstance(child, (list, dict)):
                    recurse(child, depth + 1)
        elif isinstance(node, list):
            for item in node:
                recurse(item, depth)

    recurse(example_json)
    return {
        "type": example_json.get("type", ""),
        "value": example_json.get("value", ""),
        "doc": doc,
        "calls": sorted(calls),
        "vars": sorted(vars_),
        "keywords": sorted(keywords),
        "param_count": param_count,
        "return_type": return_type,
        "depth": max_depth,
        "child_count": total_children,
        "complexity_score": len(calls) + len(vars_) + len(keywords) + param_count + max_depth,
        "raw": example_json
    }

# =================== تصنيف وربط ===================
def classify_term(term: str, index: int, cache: Dict[str, Dict]) -> Dict:
    if term in cache: return cache[term]
    analysis = {"term": term, "type": "unknown", "score": 0, "notes": "", "suggested_code": None}
    if len(term) <= 2: analysis.update({"type": "irrelevant", "notes": "قصير"})
    elif term in {"this", "that", "from", "your", "none"}: analysis.update({"type": "irrelevant", "notes": "كلمة عامة"})
    elif is_garbage_like(term): analysis.update({"type": "nonsense", "score": -2, "notes": "رمز مكرر"})
    elif term.istitle(): analysis.update({"type": "class", "score": 3, "notes": "CamelCase", "suggested_code": suggest_concept_code(index)})
    elif "_" in term: analysis.update({"type": "function", "score": 4, "notes": "دالة أو معالج", "suggested_code": suggest_concept_code(index)})
    else: analysis.update({"type": "concept", "score": 5, "notes": "مرشح مفهوم", "suggested_code": suggest_concept_code(index)})
    cache[term] = analysis
    return analysis

def match_examples(term: str, bank: Dict[str, Dict]) -> List[str]:
    matches, t = [], term.lower()
    for eid, meta in bank.items():
        if t in meta["value"].lower() or t in " ".join(meta["calls"]).lower() or t in " ".join(meta["vars"]).lower():
            matches.append(eid)
        elif SequenceMatcher(None, t, meta["value"].lower()).ratio() > 0.7:
            matches.append(eid)
        if len(matches) >= 3: break
    return matches

def gpt_definition(term: str, gpt_key: str | None) -> str:
    if not gpt_key or not openai: return ""
    try:
        openai.api_key = gpt_key
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "اشرح هذا المصطلح البرمجي بإيجاز ووضوح."},
                {"role": "user", "content": term}
            ],
            temperature=0.2,
            max_tokens=60
        )
        return res.choices[0].message.content.strip()
    except: return ""

# =================== التنفيذ ===================
def run_pipeline(ast_file: str, gpt_key: str | None):
    print(f"📥 تحميل AST من {ast_file}...")
    terms, examples_raw, docstrings = set(), {}, {}
    with open(ast_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="🧠 تحليل JSONL"):
            try:
                obj = json.loads(line.strip())
                extract_terms_examples_docstrings(obj, terms, examples_raw, docstrings)
            except: continue

    if not os.path.exists(EXAMPLE_ADVANCED_PATH):
        print("🔬 تحليل الأمثلة...")
        example_advanced = {
            eid: extract_metadata(json.loads(raw)) for eid, raw in tqdm(examples_raw.items())
        }
        with open(EXAMPLE_ADVANCED_PATH, 'w', encoding='utf-8') as f:
            json.dump(example_advanced, f, indent=2, ensure_ascii=False)
    else:
        print("✅ تم العثور على example_bank_advanced.json – سيتم استخدامه مباشرة")
        with open(EXAMPLE_ADVANCED_PATH, 'r', encoding='utf-8') as f:
            example_advanced = json.load(f)

    print("🔗 بناء اللبنات...")
    concepts, cache, idx = [], {}, 1
    for term in tqdm(sorted(terms)):
        analysis = classify_term(term, idx, cache)
        if analysis["suggested_code"]:
            desc = docstrings.get(term, "") or gpt_definition(term, gpt_key)
            unit = {
                "id": analysis["suggested_code"],
                "term": term,
                "concept": term,
                "definition": desc,
                "example_ids": match_examples(term, example_advanced),
                "language": "python",
                "source": "py150"
            }
            concepts.append(unit)
            idx += 1

    os.makedirs(os.path.dirname(CORE_UNITS_PATH), exist_ok=True)
    with open(CORE_UNITS_PATH, 'w', encoding='utf-8') as f:
        json.dump(concepts, f, indent=2, ensure_ascii=False)
    print(f"✅ تم حفظ {len(concepts)} لبنة في {CORE_UNITS_PATH}")

# =================== Main ===================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default=AST_INPUT)
    parser.add_argument('--openai-key', type=str, help="مفتاح OpenAI لتوليد الشروحات الذكية")
    args = parser.parse_args()
    run_pipeline(args.input, args.openai_key)
