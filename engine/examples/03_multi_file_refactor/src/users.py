def normalize_email(addr: str) -> str:
    return addr.strip().lower()


def create_user(addr: str) -> dict:
    return {"email": normalize_email(addr)}
