# core/cleaner.py

import re
from typing import Optional

def clean_word(word: str) -> Optional[str]:
    """
    ينظف الكلمة من الرموز والعناصر غير الأبجدية، ويحافظ على المسافات.

    - يحوّل إلى lowercase
    - يستبدل "_" و "-" بمسافات
    - يحذف الأرقام والرموز
    - يطبع المسافات
    - يرجع None إذا أصبحت الكلمة فارغة
    """
    if not isinstance(word, str):
        return None

    word = word.replace("_", " ").replace("-", " ").lower()
    word = re.sub(r'[^a-z\s]', '', word)  # نحذف الأرقام أيضًا
    word = re.sub(r'\s+', ' ', word).strip()
    return word if word else None

# ✅ اختبار مباشر
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
