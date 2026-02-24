"""Input validation for variables and minterms text."""


def validate_variables(text: str) -> tuple[bool, str | None]:
    """Return (True, None) if valid comma-separated variables (letters only), else (False, error_message)."""
    text = text.strip()
    if not text:
        return True, None
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        return False, "At least one variable required."
    for p in parts:
        if not p.isalpha() or not all(c.isascii() and c.isalpha() for c in p):
            return False, "Use only English letters (a-z, A-Z), comma-separated."
    return True, None


def validate_minterms(text: str) -> tuple[bool, str | None]:
    """Return (True, None) if valid comma-separated minterm numbers, else (False, error_message)."""
    text = text.strip()
    if not text:
        return True, None
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        return False, "At least one minterm required."
    for p in parts:
        if not p.isdigit():
            return False, "Use only numbers (0, 1, 2, ...), comma-separated."
    return True, None
