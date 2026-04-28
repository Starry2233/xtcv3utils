"""RSA/ECB/PKCS1Padding 加密

对应 Android: com.xtc.utils.encode.j (RSAUtil.java)
算法: RSA/ECB/PKCS1Padding
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


def encrypt(plain_text: str, public_key_pem: str) -> str:
    """RSA/ECB/PKCS1Padding 加密 → Base64 输出"""
    key = RSA.import_key(public_key_pem)
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(plain_text.encode("utf-8"))
    import base64
    return base64.b64encode(encrypted).decode()


def get_default_public_key() -> str:
    """Android RSAUtil.a 中硬编码的默认 RSA 公钥"""
    key_base64 = (
        "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDfQz49r6aXpY49YPr3a9n1PHUy"
        "/bYzufv/Ag3Cdv1GLtugWy3qYBE6uj2CrRuBGgaWlmTtWpw9EmQtnen4xsKjxw8e"
        "qqNqud+pAUEG4k2YLEBe79MOuslld6R6vT+a9kvpY60rGO7/Pm+x8fVyCZvIQouz"
        "bf+T2b/GDTU0XNJR0wIDAQAB"
    )
    import base64
    der = base64.b64decode(key_base64)
    key = RSA.import_key(der)
    return key.export_key("PEM").decode()
