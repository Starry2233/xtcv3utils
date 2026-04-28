"""MD5 签名（大写 Hex 输出）

对应 Android: com.xtc.utils.encode.h (MD5Util.java)
注意: 输出是大写 A-F (cArr = {'0'..'9', 'A'..'F'})
"""

import hashlib


def sign(data: bytes) -> str:
    """MD5 签名，返回大写 Hex 字符串"""
    return hashlib.md5(data).hexdigest().upper()


def sign_str(text: str) -> str:
    """字符串 MD5 签名，返回大写 Hex"""
    return sign(text.encode("utf-8"))
