import base64
import json
from dataclasses import dataclass
from datetime import UTC, datetime


class CursorDecodeError(ValueError):
    """Raised when a pagination cursor cannot be trusted."""


@dataclass(frozen=True)
class ProductCursor:
    updated_at: datetime
    id: int


def encode_cursor(updated_at: datetime, product_id: int) -> str:
    payload = {
        "updated_at": updated_at.isoformat(timespec="microseconds"),
        "id": product_id,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> ProductCursor:
    try:
        padding = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode((cursor + padding).encode("ascii"))
        payload = json.loads(raw.decode("utf-8"))
        updated_at = datetime.fromisoformat(payload["updated_at"])
        product_id = int(payload["id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise CursorDecodeError("Invalid pagination cursor.") from exc

    if product_id <= 0:
        raise CursorDecodeError("Invalid pagination cursor.")

    if updated_at.tzinfo is not None:
        updated_at = updated_at.astimezone(UTC).replace(tzinfo=None)

    return ProductCursor(updated_at=updated_at, id=product_id)
