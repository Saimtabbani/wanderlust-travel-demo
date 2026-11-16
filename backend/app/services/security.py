import hmac
import hashlib
import os
import uuid
from typing import Tuple, Optional

# The deployment must supply this value. The fallback is only for local
# development so a real secret is never committed to the repository.
SESSION_SECRET = os.getenv(
    "WANDERLUST_SESSION_SECRET", "wanderlust-local-development-only-change-me"
).encode("utf-8")

def generate_secure_session_id(contributor_id: Optional[int] = None) -> str:
    """
    Generates a cryptographically signed session token:
    Format: wl_sec_<raw_id>_<signature>
    If contributor_id is present, encodes it: wl_sec_c<id>_<raw_id>_<signature>
    """
    prefix = f"c{contributor_id}_" if contributor_id is not None else ""
    raw_token = f"{prefix}{uuid.uuid4().hex}"
    sig = hmac.new(SESSION_SECRET, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()[:16]
    return f"wl_sec_{raw_token}_{sig}"

def verify_session_id(session_id: str) -> Tuple[bool, Optional[int]]:
    """
    Validates the session token authenticity.
    Returns (is_valid, extracted_contributor_id).
    Prevents clients from fabricating untrusted session IDs in automated loops.
    """
    if not session_id or not isinstance(session_id, str):
        return False, None

    if not session_id.startswith("wl_sec_"):
        return False, None

    parts = session_id[7:].rsplit("_", 1)
    if len(parts) != 2:
        return False, None

    raw_token, provided_sig = parts
    expected_sig = hmac.new(SESSION_SECRET, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()[:16]

    if not hmac.compare_digest(provided_sig, expected_sig):
        return False, None

    contributor_id = None
    if raw_token.startswith("c"):
        try:
            cid_part = raw_token[1:].split("_")[0]
            contributor_id = int(cid_part)
        except Exception:
            pass

    return True, contributor_id
