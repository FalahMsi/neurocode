# core/cleaner.py

import re
from typing import Optional

def clean_word(word: str) -> Optional[str]:
    """
    Cleans the word from symbols and non-alphabetic elements, preserving spaces.

    - Converts to lowercase
    - Replaces "_" and "-" with spaces
    - Removes numbers and symbols
    - Preserves spaces
    - Returns None if the word becomes empty
    """
    if not isinstance(word, str):
        return None

    word = word.replace("_", " ").replace("-", " ").lower()
    word = re.sub(r'[^a-z\s]', '', word)  # Remove numbers as well
    word = re.sub(r'\s+', ' ', word).strip()
    return word if word else None

# Direct test
if __name__ == "__main__":
    test_words = [
        "Cat", "  multiple   spaces ", "Café", "data-driven",
        "NAÏVE", "!!!", None, "this_is_clean", "12345", "   "
    ]
    print(f"{'Original':<20} → {'Cleaned'}")
    print("-" * 40)
    for w in test_words:
        cleaned = clean_word(w)
        print(f"{str(w):<20} → {str(cleaned)}")
