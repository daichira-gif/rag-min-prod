import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?:\+?\d{1,3}[- .]?)?\(?\d{3}\)?[- .]?\d{3}[- .]?\d{4}")
CARD = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

def scrub(text: str) -> str:
    text = EMAIL.sub("[EMAIL]", text)
    text = CARD.sub("[CARD]", text)
    text = PHONE.sub("[PHONE]", text)
    return text
