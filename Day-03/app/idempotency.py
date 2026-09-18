"""Stable fingerprints for side effects. Hashing, used for exactly-once."""
import hashlib
import json
from datetime import date


def _normalise(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_normalise(v) for v in value]
    return value


def canonical_json(value) -> str:
    """Return a stable compact JSON representation for equivalent values."""
    return json.dumps(_normalise(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def idempotency_key(run_id: str, step_seq: int, tool_name: str, args: dict) -> str:
    """Stable SHA-256 key for one tool call at one step of one run."""
    payload = canonical_json([run_id, step_seq, tool_name, args]).encode()
    return hashlib.sha256(payload).hexdigest()


def notification_dedupe_key(roll_no: str, message: str, day: date) -> str:
    """Stable key for the same normalized message to one student on one day."""
    message = " ".join(message.split())
    payload = canonical_json([roll_no, message, day.isoformat()]).encode()
    return hashlib.sha256(payload).hexdigest()
