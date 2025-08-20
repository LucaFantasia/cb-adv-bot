import uuid


def idempotency_key() -> str:
    return str(uuid.uuid4())
