#!/usr/bin/env python3
"""
DISCLAIMER: This script is for authorized security research and SDK
integration testing only. 本脚本仅供授权安全研究和 SDK 集成测试使用。

解密 HttpCanary 抓包文件

用法:
    python decrypt_httpcanary.py <prefix> --aes KEY

示例:
    python decrypt_httpcanary.py 1777340797811 --aes 416d44d033be6269
"""

import sys, os, json
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

import base64, gzip
from Crypto.Cipher import AES


def get_body_from_raw(raw_file: str) -> str:
    """从 _raw 文件中提取 HTTP body"""
    with open(raw_file, "r", encoding="utf-8") as f:
        content = f.read()
    # HTTP 头体分隔
    for sep in ["\r\n\r\n", "\n\n"]:
        if sep in content:
            return content.split(sep, 1)[-1].strip()
    return ""


def decrypt_aes_gzip_b64(encrypted_b64: str, aes_key: str) -> str:
    """Base64 → AES解密 → GZip解压 → 明文"""
    raw = base64.b64decode(encrypted_b64)
    cipher = AES.new(aes_key.encode("utf-8"), AES.MODE_ECB)
    decrypted = cipher.decrypt(raw)
    # 去 PKCS7 padding
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    return gzip.decompress(decrypted).decode("utf-8")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="解密 HttpCanary V3 加密请求")
    parser.add_argument("prefix", help="文件前缀 (例如 1777340797811)")
    parser.add_argument("--aes", required=True, help="AES 密钥 (16字节)")
    args = parser.parse_args()

    dir_path = os.path.dirname(__file__) or "."
    raw_file = os.path.join(dir_path, f"{args.prefix}_raw")
    header_file = os.path.join(dir_path, f"{args.prefix}_header")

    # 读 headers 判断是否加密
    headers = {}
    with open(header_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()

    is_encrypted = "encrypted" in headers.get("encrypted", "")

    # 从 raw 文件取 body
    body_b64 = get_body_from_raw(raw_file)

    print(f"请求: {headers.get('Eebbk-Sign', '')[:16]}...")
    print(f"URL: {headers.get('Host', '')}{headers.get('POST', '').split(' ')[0] if 'POST' in open(header_file).read()[:10] else ''}")

    if is_encrypted and body_b64:
        plain = decrypt_aes_gzip_b64(body_b64, args.aes)
        print(f"\n解密结果:")
        print("-" * 40)
        try:
            obj = json.loads(plain)
            print(json.dumps(obj, indent=2, ensure_ascii=False))
        except:
            print(plain)
        print("-" * 40)
    else:
        print(f"\n未加密或body为空:")
        print(body_b64)


if __name__ == "__main__":
    main()
