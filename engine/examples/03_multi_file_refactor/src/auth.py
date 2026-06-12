def normalize_email(addr: str) -> str:
    # Duplicate of the helper in users.py — refactor candidate.
    return addr.strip().lower()


def login(addr: str, password: str) -> bool:
    email = normalize_email(addr)
    return bool(email) and bool(password)
