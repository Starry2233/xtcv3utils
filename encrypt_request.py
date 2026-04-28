#!/usr/bin/env python3
"""
DISCLAIMER: This script is for authorized security research and SDK
integration testing only. 本脚本仅供授权安全研究和 SDK 集成测试使用。

加密 V3 请求

用法:
    # 查看从抓包提取的信息
    python encrypt_request.py extract <prefix> --aes KEY

    # 加密自定义请求
    python encrypt_request.py encrypt <prefix> --aes KEY --json '{"content":"你好","type":3}'
"""

import sys, os, json, base64
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "xtcv3utils"))

from Crypto.Cipher import AES
from xtcv3utils import V3Client


def decode_base_param(base_param_b64: str, aes_key: str) -> dict:
    """解密 Base-Request-Param 得到设备信息"""
    raw = base64.b64decode(base_param_b64)
    cipher = AES.new(aes_key.encode("utf-8"), AES.MODE_ECB)
    decrypted = cipher.decrypt(raw)
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    return json.loads(decrypted.decode("utf-8"))


def extract_from_raw(raw_file: str) -> dict:
    """从 raw 文件提取 headers"""
    info = {}
    with open(raw_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip().lower()] = v.strip()
    return info


def main():
    import argparse
    parser = argparse.ArgumentParser(description="V3 请求加密工具")
    sub = parser.add_subparsers(dest="cmd")

    # extract 子命令
    ext = sub.add_parser("extract", help="从抓包提取设备信息")
    ext.add_argument("prefix", help="文件前缀")
    ext.add_argument("--aes", required=True, help="AES 密钥")

    # encrypt 子命令
    enc = sub.add_parser("encrypt", help="加密请求")
    enc.add_argument("prefix", help="文件前缀（用于提取 eebbk_key/key_id）")
    enc.add_argument("--aes", required=True, help="AES 密钥")
    enc.add_argument("--json", required=True, help="要发送的 JSON 字符串")
    enc.add_argument("--url", default="<paste your api url e.g. moment.watch.okii.com/moment/public>", help="请求 URL")

    args = parser.parse_args()
    dir_path = os.path.dirname(__file__) or "."

    if args.cmd == "extract":
        raw_file = os.path.join(dir_path, f"{args.prefix}_raw")
        if not os.path.exists(raw_file):
            print(f"找不到文件: {raw_file}")
            return

        info = extract_from_raw(raw_file)
        base_param_b64 = info.get("base-request-param", "")
        if not base_param_b64:
            print("没有找到 Base-Request-Param header")
            return

        params = decode_base_param(base_param_b64, args.aes)
        print("=== 设备信息 ===")
        print(f"watchId:     {params.get('accountId', '')}")
        print(f"deviceId:    {params.get('deviceId', '')}")
        print(f"token:       {params.get('token', '')}")
        print(f"mac:         {params.get('mac', '')}")
        print(f"requestId:   {params.get('requestId', '')}")
        print()
        print("=== 密钥信息 ===")
        print(f"aesKey:    {args.aes}")
        print(f"eebbkKey:  {info.get('eebbk-key', '')}")
        print(f"keyId:     {info.get('eebbk-key-id', '')}")
        print()
        print("=== 其他 ===")
        print(f"packageVersion: {info.get('packageversion', '')}")
        print(f"packageName:    {info.get('packagename', '')}")
        print(f"model:          {info.get('model', '')}")

    elif args.cmd == "encrypt":
        raw_file = os.path.join(dir_path, f"{args.prefix}_raw")
        if not os.path.exists(raw_file):
            print(f"找不到文件: {raw_file}")
            return

        info = extract_from_raw(raw_file)
        base_param_b64 = info.get("base-request-param", "")
        if not base_param_b64:
            print("没有找到 Base-Request-Param header")
            return

        params = decode_base_param(base_param_b64, args.aes)

        client = V3Client(
            aes_key=args.aes,
            eebbk_key=info.get("eebbk-key", ""),
            key_id=info.get("eebbk-key-id", ""),
            watch_id=params.get("accountId", ""),
            device_id=params.get("deviceId", ""),
            token=params.get("token", ""),
            mac=params.get("mac", ""),
            package_version=info.get("packageversion", ""),
            package_name=info.get("packagename", ""),
            model=info.get("model", "watch"),
        )

        # 生成新的 uuid
        import uuid as uuid_mod
        url_uuid = uuid_mod.uuid4().hex
        header_uuid = str(uuid_mod.uuid4())
        full_url = args.url + "?uuid=" + url_uuid

        headers, encrypted_body = client.encrypt_request(
            url=full_url,
            body=args.json,
        )
        headers["uuid"] = header_uuid
        # 原始请求中额外的 header
        headers["dataCenterCode"] = "CN_BJ"
        headers["Version"] = "W_1.9.0"
        headers["Grey"] = "0"
        headers["Accept-Language"] = "zh-CN"
        headers["Watch-Time-Zone"] = "GMT+08:00"

        print("=== 请求头 ===")
        for k, v in headers.items():
            print(f"{k}: {v}")

        print(f"\n=== 加密后的 Body ===")
        print(encrypted_body)

        # 生成 curl 命令
        print(f"\n=== curl 命令 (PowerShell) ===")
        print(f'# url_uuid: {url_uuid}')
        print(f'# header_uuid: {header_uuid}')
        cmd = f'curl.exe -X POST "{full_url}" `'
        for k, v in headers.items():
            cmd += f'\n  -H "{k}: {v}" `'
        cmd += f'\n  -d "{encrypted_body}"'
        print(cmd)


if __name__ == "__main__":
    main()
