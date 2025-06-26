# core/core_builder.py

import datetime
from nltk.corpus import wordnet as wn
from typing import Optional

from core.cleaner import clean_word
from core.pos_utils import extract_stem, get_dominant_wordnet_pos
from core.concept_extractor import extract_concept

POS_MAP = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "s": "adjective satellite",
    "r": "adverb"
}

def build_core_unit(raw_word: str, cleaned_word: str, timestamp: Optional[str] = None) -> Optional[dict]:
    """
    Converts the word into a smart CoreUnit containing:
    - The stem of the word
    - The main concept
    - Part-of-speech types (POS)
    - Brief definitions
    - Semantically related words

    Returns None if insufficient information is extracted.
    """
    synsets = wn.synsets(cleaned_word)
    if not synsets:
        return None

    definition_set = []
    pos_tags = []
    related_words = set()

    for syn in synsets:
        defn = syn.definition()
        exs = syn.examples()
        pos = POS_MAP.get(syn.pos(), syn.pos())
        pos_tags.append(pos)
        definition_set.append({
            "definition": defn,
            "example": exs[0] if exs else "",
            "source": "wordnet"
        })

        for lemma in syn.lemmas():
            lemma_clean = clean_word(lemma.name())
            if lemma_clean:
                stemmed = extract_stem(lemma_clean)
                if stemmed:
                    related_words.add(stemmed)

    if not definition_set or all(d["definition"].strip() == "" for d in definition_set):
        return None

    concept = extract_concept([d["definition"] for d in definition_set])
    best_pos = get_dominant_wordnet_pos(cleaned_word)
    stem = extract_stem(cleaned_word, best_pos)
    pos_code = best_pos.upper()
    unit_id = f"{stem.upper()}_{pos_code}_CORE"

    return {
        "id": unit_id,
        "stem": stem,
        "concept": concept,
        "pos": sorted(set(pos_tags)),
        "main_pos": POS_MAP.get(best_pos, best_pos),
        "definition_set": definition_set[:3],
        "related": sorted(list(related_words))[:5],
        "source": "wordnet",
        "last_updated": timestamp or datetime.datetime.utcnow().isoformat()
    }
