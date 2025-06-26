# core/pos_utils.py

from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from typing import Literal

# POS الرمزية المعتمدة من WordNet
WordNetPOS = Literal['n', 'v', 'a', 's', 'r']

# تهيئة الملمّز مرة واحدة على مستوى الملف
lemmatizer = WordNetLemmatizer()

def get_dominant_wordnet_pos(word: str) -> WordNetPOS:
    """
    استنتاج نوع الكلمة الأكثر شيوعًا (noun, verb, adjective, ...) بناءً على WordNet.
    
    Parameters:
        word (str): الكلمة المدخلة
        
    Returns:
        str: رمز POS الأكثر تكرارًا (n/v/a/r/s)
    """
    if not isinstance(word, str) or not word.strip():
        return 'n'  # fallback
    
    synsets = wn.synsets(word)
    pos_counts = {"n": 0, "v": 0, "a": 0, "s": 0, "r": 0}

    for syn in synsets:
        pos = syn.pos()
        if pos in pos_counts:
            pos_counts[pos] += 1

    # الأولوية المعرفية للأنواع
    priority = ['n', 'v', 'a', 'r', 's']
    if any(pos_counts.values()):
        return sorted(priority, key=lambda x: -pos_counts[x])[0]
    return 'n'

def extract_stem(word: str, pos: WordNetPOS = 'n') -> str:
    """
    استخراج جذر الكلمة باستخدام WordNet Lemmatizer بناءً على نوعها اللغوي.
    
    Parameters:
        word (str): الكلمة الأصلية
        pos (str): نوع الكلمة POS ('n', 'v', 'a', 's', 'r')
        
    Returns:
        str: الجذر المتوقع للكلمة
    """
    if not isinstance(word, str):
        return word
    
    if pos not in {'n', 'v', 'a', 's', 'r'}:
        pos = 'n'
    return lemmatizer.lemmatize(word, pos=pos)


# ✅ اختبار مباشر عند تشغيل الملف بشكل مستقل
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
