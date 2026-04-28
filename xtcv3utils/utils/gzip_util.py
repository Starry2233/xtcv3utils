"""GZip 压缩/解压

对应 Android: com.xtc.utils.encode.e (GzipUtil.java)
"""

import gzip
import io


def compress(data: bytes) -> bytes:
    """GZip 压缩"""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as f:
        f.write(data)
    return buf.getvalue()


def decompress(data: bytes) -> bytes:
    """GZip 解压"""
    buf = io.BytesIO(data)
    with gzip.GzipFile(fileobj=buf, mode="rb") as f:
        return f.read()


def compress_str(text: str, encoding: str = "utf-8") -> bytes:
    """字符串 GZip 压缩"""
    return compress(text.encode(encoding))


def decompress_to_str(data: bytes, encoding: str = "utf-8") -> str:
    """GZip 解压为字符串"""
    return decompress(data).decode(encoding)
