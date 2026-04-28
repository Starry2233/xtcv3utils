#!/usr/bin/env python3
"""XTC V3 加密解密演示"""

import os, sys
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

from xtcv3utils import V3Client

def main():
    client = V3Client(
        aes_key="0123456789abcdef",
        eebbk_key="fake_rsa_encrypted_key",
        key_id="v3_key_001",
        watch_id="watch_12345",
        device_id="13800138000",
        token="chip_id_abc123",
        mac="AA:BB:CC:DD:EE:FF",
    )

    url = "https://api.xtc.com/moment/public"
    request_body = '{"watchId":"watch_12345","content":"Hello World!","type":3,"emotionId":0}'

    print("=" * 60)
    print("[请求加密演示]")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Body: {request_body}")

    headers, encrypted_body = client.encrypt_request(url, request_body)

    print("\nHeaders:")
    for k, v in headers.items():
        val = v[:60] + "..." if len(v) > 60 else v
        print(f"  {k}: {val}")

    if encrypted_body:
        eb = encrypted_body[:80] + "..." if len(encrypted_body) > 80 else encrypted_body
        print(f"\nEncrypted Body: {eb}")

    print(f"\nSign: {headers.get('Eebbk-Sign')}")

    print("\n" + "=" * 60)
    print("[基础参数 JSON]")
    print("=" * 60)
    print(client.build_base_param_json())

    print("\n" + "=" * 60)
    print("[签名计算过程]")
    print("=" * 60)
    sign = client.generate_sign(url, client.build_base_param_json(), request_body)
    print(f"Eebbk-Sign = MD5(url + param + body + aesKey)")
    print(f"           = {sign}")


if __name__ == "__main__":
    main()
