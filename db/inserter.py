# db/inserter.py

import json
from typing import Dict

def insert_unit(conn, unit: Dict[str, str | list], commit: bool = True):
    """
    يدخل اللبنة الذكية CoreUnit إلى جدول core_units.
    
    Parameters:
        conn (sqlite3.Connection): اتصال بقاعدة البيانات.
        unit (dict): تمثيل اللبنة.
        commit (bool): هل يتم حفظ التغييرات فورًا أم لا.
    """
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO core_units (
            id, stem, concept, pos, main_pos,
            definition_set, related, source, last_updated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        unit["id"],
        unit["stem"],
        unit["concept"],
        json.dumps(unit["pos"]),
        unit["main_pos"],
        json.dumps(unit["definition_set"]),
        json.dumps(unit["related"]),
        unit["source"],
        unit["last_updated"]
    ))

    if commit:
        conn.commit()
