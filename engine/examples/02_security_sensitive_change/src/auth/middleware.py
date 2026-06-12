"""Auth middleware — verifies request tokens against the expected secret."""

import os


def verify_token(provided: str) -> bool:
    expected = os.environ.get("API_TOKEN", "")
    # NOTE: not timing-safe.
    return provided == expected
