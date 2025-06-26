# smartcodelex_prompt_exporter.py

import sqlite3
import os

DB_PATH = "smartcodelex.db"
OUTPUT_PATH = "prompts/prompts.txt"
MAX_EXAMPLES = 3

# ===============================
# Fetch data from the database
# ===============================
def fetch_units_with_examples():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, term, concept, definition, example_ids FROM core_units")
    core_units = c.fetchall()

    examples_map = {}
    c.execute("SELECT id, content FROM examples")
    for eid, content in c.fetchall():
        examples_map[eid] = content.strip()

    conn.close()
    return core_units, examples_map

# ===============================
# Generate prompt from unit
# ===============================
def generate_prompt(unit, examples_map):
    uid, term, concept, definition, example_ids_json = unit
    example_ids = []
    try:
        example_ids = json.loads(example_ids_json)
    except:
        pass

    examples = [examples_map.get(eid) for eid in example_ids if eid in examples_map][:MAX_EXAMPLES]

    prompt = f"[Concept] {concept}\n"
    if definition:
        prompt += f"[Definition] {definition.strip()}\n"
    if examples:
        prompt += f"[Examples]\n"
        for i, ex in enumerate(examples, 1):
            prompt += f"- E{i:03}: {ex}\n"
    prompt += "\n"
    return prompt

# ===============================
# Execute export
# ===============================
def export_prompts():
    if not os.path.exists("prompts"):
        os.makedirs("prompts")

    core_units, examples_map = fetch_units_with_examples()
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for unit in core_units:
            prompt = generate_prompt(unit, examples_map)
            f.write(prompt)

    print(f"✅ Prompts generated for {len(core_units)} concepts.")
    print(f"📁 Saved to: {OUTPUT_PATH}")

# ===============================
if __name__ == "__main__":
    import json
    export_prompts()