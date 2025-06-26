# builder/cleaner.py

import re
from typing import Optional

def clean_word(word: str) -> Optional[str]:
    """
    Cleans the word from symbols and non-alphabetic elements, preserving spaces.

    - Converts to lowercase
    - Replaces "_" and "-" with spaces
    - Removes numbers and symbols
    - Keeps spaces
    - Returns None if the word becomes empty
    """
    if not isinstance(word, str):
        return None

    word = word.replace("_", " ").replace("-", " ").lower()
    word = re.sub(r'[^a-z\s]', '', word)  # Remove numbers and symbols
    word = re.sub(r'\s+', ' ', word).strip()
    return word if word else None

# Internal test
if __name__ == "__main__":
    samples = ["Python_Dev!", "123", None, "clean-word", "this_is_a_test"]
    for word in samples:
        print(f"'{word}' → '{clean_word(word)}'")
