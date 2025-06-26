# db/inserter.py

import json
from typing import Dict

def insert_unit(conn, unit: Dict[str, str | list], commit: bool = True):
    """
    Inserts the smart unit CoreUnit into the core_units table.
    
    Parameters:
        conn (sqlite3.Connection): Database connection.
        unit (dict): Unit representation.
        commit (bool): Whether to commit changes immediately.
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
