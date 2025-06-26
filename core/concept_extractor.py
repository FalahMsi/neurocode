import re
from typing import List

NON_CONCEPTS = {
    "a", "an", "the", "to", "of", "in", "on", "by", "at", "any", "one",
    "something", "thing", "type", "kind", "form", "way", "means",
    "process", "action", "aspect", "element", "area", "category", "manner"
}

PRIORITY_KEYWORDS = {
    "animal", "organism", "structure", "object", "movement",
    "tool", "device", "substance", "feature", "signal", "material", "system"
}

def extract_concept(definitions: List[str], compound: bool = True) -> str:
    """
    استخراج المفهوم (concept) من أول 3 تعريفات.
    يعطي الأولوية لكلمات قوية الدلالة.
    يدعم المفاهيم المركبة (compound) إذا كانت مفعّلة.
    """
    if not definitions:
        return "unknown"

    for definition in definitions[:3]:
        words = re.findall(r'\b\w+\b', definition.lower())
        filtered = [w for w in words if w not in NON_CONCEPTS]

        for word in filtered:
            if word in PRIORITY_KEYWORDS:
                return word

        if compound and len(filtered) >= 2:
            return f"{filtered[0]} {filtered[1]}"
        elif filtered:
            return filtered[0]

    return "unknown"

# ✅ اختبار مباشر
if __name__ == "__main__":
    test_definitions = [
        "a small creature with wings.",
        "the act of jumping from a plane.",
        "a process of converting energy.",
        "a type of animal known for loyalty.",
        "an electronic device that stores data.",
        "the movement of water in a river.",
        "an element of artistic expression.",
        "a feature of biological systems."
    ]

    print(f"{'Definition':<60} → Single Concept | Compound Concept")
    print("-" * 90)
    for definition in test_definitions:
        concept_single = extract_concept([definition], compound=False)
        concept_multi = extract_concept([definition], compound=True)
        print(f"{definition:<60} → {concept_single:<15} | {concept_multi}")
