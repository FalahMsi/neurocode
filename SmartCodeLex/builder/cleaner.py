# builder/cleaner.py

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
    word = re.sub(r'[^a-z\s]', '', word)  # نحذف الأرقام والرموز
    word = re.sub(r'\s+', ' ', word).strip()
    return word if word else None

# اختبار داخلي
if __name__ == "__main__":
    samples = ["Python_Dev!", "123", None, "clean-word", "this_is_a_test"]
    for word in samples:
        print(f"'{word}' → '{clean_word(word)}'")
