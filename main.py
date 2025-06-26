import json
import os
import argparse
from core.cleaner import clean_word
from core.core_builder import build_core_unit
from db.database import create_database, initialize_meta, update_meta
from db.inserter import insert_unit

SKIPPED_LOG = "logs/skipped.log"
PROCESSED_LOG = "logs/processed.json"
CORE_DIR = "brain/lexical_cores"

def load_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ فشل في تحميل {file_path}: {e}")
        return []

def log_skipped(skipped):
    with open(SKIPPED_LOG, 'w', encoding='utf-8') as f:
        for word in skipped:
            f.write(f"{word}\n")

def log_processed(units):
    with open(PROCESSED_LOG, 'w', encoding='utf-8') as f:
        json.dump(units, f, indent=2, ensure_ascii=False)

def process_letter(letter, conn, global_seen, all_processed, all_skipped):
    path = os.path.join(CORE_DIR, f"{letter}.json")
    words = load_words(path)
    print(f"\n🔤 معالجة {letter}.json — {len(words)} كلمة")

    for i, raw_word in enumerate(words):
        cleaned = clean_word(raw_word)
        if not cleaned:
            all_skipped.append(raw_word)
            continue

        unit = build_core_unit(raw_word, cleaned)
        if not unit or unit["id"] in global_seen:
            all_skipped.append(raw_word)
            continue

        insert_unit(conn, unit, commit=False)
        global_seen.add(unit["id"])
        all_processed.append(unit)

        if i % 500 == 0:
            print(f"🔁 {i}/{len(words)} | الإجمالي: {len(global_seen)} محفوظ")

    conn.commit()
    update_meta(conn, f"letter_{letter}_count", str(len(all_processed)))

def main():
    parser = argparse.ArgumentParser(description="تشغيل نظام اللبنات الذكية")
    parser.add_argument('--letter', type=str, help='حدد حرف واحد فقط لمعالجته (مثل a أو c)', default=None)
    parser.add_argument('--db-path', type=str, help='مسار قاعدة البيانات', default="storage/core_units.db")
    args = parser.parse_args()

    conn = create_database(db_path=args.db_path)
    initialize_meta(conn)

    seen_ids = set()
    processed_units = []
    skipped_words = []

    if args.letter:
        letter = args.letter.lower()
        if len(letter) != 1 or not letter.isalpha():
            print("❌ يرجى إدخال حرف واحد فقط مثل: --letter c")
            return
        process_letter(letter, conn, seen_ids, processed_units, skipped_words)
    else:
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            process_letter(letter, conn, seen_ids, processed_units, skipped_words)

    print(f"\n✅ تم حفظ {len(processed_units)} لبنة في القاعدة.")
    if skipped_words:
        print(f"⚠️ تم تجاهل {len(skipped_words)} كلمة – راجع {SKIPPED_LOG}")
        log_skipped(skipped_words)

    log_processed(processed_units)
    update_meta(conn, "core_count", str(len(processed_units)))
    conn.close()

if __name__ == "__main__":
    main()
