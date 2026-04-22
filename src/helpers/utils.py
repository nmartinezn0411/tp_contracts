import re
def clean_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)  # Collapse all whitespace to single space
    text = re.sub(r"(\n\s*){2,}", "\n", text)  # Collapse multiple blank lines
    return text.strip()