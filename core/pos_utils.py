# core/pos_utils.py

from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from typing import Literal

# WordNet POS tags
WordNetPOS = Literal['n', 'v', 'a', 's', 'r']

# Initialize the lemmatizer once at the file level
lemmatizer = WordNetLemmatizer()

def get_dominant_wordnet_pos(word: str) -> WordNetPOS:
    """
    Infer the most common part of speech (noun, verb, adjective, ...) based on WordNet.
    
    Parameters:
        word (str): The input word
        
    Returns:
        str: The most frequent POS tag (n/v/a/r/s)
    """
    if not isinstance(word, str) or not word.strip():
        return 'n'  # fallback
    
    synsets = wn.synsets(word)
    pos_counts = {"n": 0, "v": 0, "a": 0, "s": 0, "r": 0}

    for syn in synsets:
        pos = syn.pos()
        if pos in pos_counts:
            pos_counts[pos] += 1

    # Priority order for POS types
    priority = ['n', 'v', 'a', 'r', 's']
    if any(pos_counts.values()):
        return sorted(priority, key=lambda x: -pos_counts[x])[0]
    return 'n'

def extract_stem(word: str, pos: WordNetPOS = 'n') -> str:
    """
    Extract the stem of the word using WordNet Lemmatizer based on its POS.
    
    Parameters:
        word (str): The original word
        pos (str): POS tag ('n', 'v', 'a', 's', 'r')
        
    Returns:
        str: The expected stem of the word
    """
    if not isinstance(word, str):
        return word
    
    if pos not in {'n', 'v', 'a', 's', 'r'}:
        pos = 'n'
    return lemmatizer.lemmatize(word, pos=pos)


# Direct test when running the file independently
if __name__ == "__main__":
    try:
        wn.synsets("test")
    except LookupError:
        import nltk
        nltk.download("wordnet")

    test_words = ["running", "flies", "better", "apples", "thinking", "unavailable", ""]

    print(f"{'Word':<15} {'POS':<5} {'Stem'}")
    print("-" * 35)
    for word in test_words:
        pos = get_dominant_wordnet_pos(word)
        stem = extract_stem(word, pos)
        print(f"{word:<15} {pos:<5} {stem}")
