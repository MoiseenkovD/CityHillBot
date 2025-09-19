import re
from typing import Optional

PHONE_RE = re.compile(r"\+?\d[\d\-\s\(\)]{8,}")


def extract_phone(text: str) -> Optional[str]:
    if not text:
        return None
    m = PHONE_RE.search(text)
    if not m:
        return None
    raw = m.group(0)
    has_plus = raw.strip().startswith("+")
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 9:
        return None
    return f"+{digits}" if has_plus else digits
