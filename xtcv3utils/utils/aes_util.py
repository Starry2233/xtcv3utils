"""AES/ECB/PKCS5Padding 加解密

对应 Android: com.xtc.utils.encode.a (AESUtil.java)
算法: AES/ECB/PKCS5Padding
"""

from Crypto.Cipher import AES


def encrypt(plain_text: str, key: str) -> bytes:
    """AES/ECB/PKCS5Padding 加密，返回原始字节"""
    cipher = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    padded = _pkcs5_pad(plain_text.encode("utf-8"), AES.block_size)
    return cipher.encrypt(padded)


def decrypt(cipher_data: bytes, key: str) -> bytes:
    """AES/ECB/PKCS5Padding 解密，返回原始字节"""
    cipher = AES.new(key.encode("utf-8"), AES.MODE_ECB)
    decrypted = cipher.decrypt(cipher_data)
    return _pkcs5_unpad(decrypted)


def encrypt_to_base64(plain_text: str, key: str) -> str:
    """AES 加密 → Base64 输出"""
    import base64
    raw = encrypt(plain_text, key)
    return base64.b64encode(raw).decode()


def decrypt_from_base64(cipher_base64: str, key: str) -> bytes:
    """Base64 输入 → AES 解密 → 原始字节"""
    import base64
    raw = base64.b64decode(cipher_base64)
    return decrypt(raw, key)


def _pkcs5_pad(data: bytes, block_size: int) -> bytes:
    pad_len = block_size - len(data) % block_size
    return data + bytes([pad_len] * pad_len)


def _pkcs5_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]
