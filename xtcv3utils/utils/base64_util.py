"""Base64 编解码（兼容 Android Base64 URL-safe / no-wrap 模式）"""

import base64


def encode(data: bytes) -> str:
    """Base64 encode, NO_WRAP (不换行)"""
    return base64.b64encode(data).decode()


def decode(data: str) -> bytes:
    """Base64 decode"""
    return base64.b64decode(data)


def encode_urlsafe(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def decode_urlsafe(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)
