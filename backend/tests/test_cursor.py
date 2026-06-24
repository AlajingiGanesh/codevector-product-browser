from datetime import datetime

import pytest

from app.core.cursor import CursorDecodeError, decode_cursor, encode_cursor


def test_cursor_round_trip() -> None:
    updated_at = datetime(2026, 1, 2, 3, 4, 5, 123456)

    token = encode_cursor(updated_at=updated_at, product_id=123)
    cursor = decode_cursor(token)

    assert cursor.updated_at == updated_at
    assert cursor.id == 123


def test_invalid_cursor_raises_decode_error() -> None:
    with pytest.raises(CursorDecodeError):
        decode_cursor("not-a-valid-cursor")

