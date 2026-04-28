"""
CLI for xtcv3utils — python -m xtcv3utils

Usage:
    python -m xtcv3utils encrypt --aes KEY --eebbk-key KEY --key-id ID --watch-id ID --device-id ID --token TOKEN --url URL --json '{"content":"hello"}'
    python -m xtcv3utils decrypt --aes KEY --body "encrypted_body"
    python -m xtcv3utils param --aes KEY --watch-id ID --device-id ID --token TOKEN
    python -m xtcv3utils sign --aes KEY --url URL --param-json '{"...":""}' --body '{"...":""}'
"""

import argparse
import json
import sys

from . import V3Client


def cmd_encrypt(args):
    client = V3Client(
        aes_key=args.aes,
        eebbk_key=args.eebbk_key,
        key_id=args.key_id,
        watch_id=args.watch_id,
        device_id=args.device_id,
        token=args.token,
        mac=args.mac,
        package_version=args.package_version,
        package_name=args.package_name,
        model=args.model,
    )
    headers, body = client.encrypt_request(args.url, args.json)
    print("=== Headers ===")
    for k, v in headers.items():
        print(f"{k}: {v}")
    if body:
        print(f"\n=== Encrypted Body ===")
        print(body)


def cmd_decrypt(args):
    from .v3_client import V3Client as VC
    client = VC(aes_key=args.aes, eebbk_key="", key_id="",
                watch_id="", device_id="", token="")
    plain = client.decrypt_response(args.body, is_encrypted=True)
    try:
        obj = json.loads(plain)
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    except Exception:
        print(plain)


def cmd_param(args):
    client = V3Client(
        aes_key=args.aes,
        eebbk_key="", key_id="",
        watch_id=args.watch_id,
        device_id=args.device_id,
        token=args.token,
        mac=args.mac,
    )
    raw = client.build_base_param_json()
    encrypted = client.encrypt_base_param(raw)
    print(f"Raw:      {raw}")
    print(f"Encrypted: {encrypted}")


def cmd_sign(args):
    client = V3Client(
        aes_key=args.aes,
        eebbk_key="", key_id="",
        watch_id="", device_id="", token="",
    )
    sign = client.generate_sign(args.url, args.param_json, args.body)
    print(f"Eebbk-Sign: {sign}")


def main():
    parser = argparse.ArgumentParser(
        description="xtcv3utils — XTC V3 API encryption/decryption CLI"
    )
    sub = parser.add_subparsers(dest="cmd")

    # encrypt
    enc = sub.add_parser("encrypt", help="Encrypt a request")
    enc.add_argument("--aes", required=True)
    enc.add_argument("--eebbk-key", required=True)
    enc.add_argument("--key-id", required=True)
    enc.add_argument("--watch-id", required=True)
    enc.add_argument("--device-id", required=True)
    enc.add_argument("--token", required=True)
    enc.add_argument("--mac", default="")
    enc.add_argument("--url", required=True, help="Full request URL")
    enc.add_argument("--json", required=True, help="Request body JSON")
    enc.add_argument("--package-version", default="1")
    enc.add_argument("--package-name", default="com.xtc.moment")
    enc.add_argument("--model", default="watch")

    # decrypt
    dec = sub.add_parser("decrypt", help="Decrypt an encrypted response")
    dec.add_argument("--aes", required=True)
    dec.add_argument("--body", required=True, help="Encrypted response body")

    # param
    param = sub.add_parser("param", help="Build and encrypt base-request-param")
    param.add_argument("--aes", required=True)
    param.add_argument("--watch-id", required=True)
    param.add_argument("--device-id", required=True)
    param.add_argument("--token", required=True)
    param.add_argument("--mac", default="")

    # sign
    sign = sub.add_parser("sign", help="Generate Eebbk-Sign")
    sign.add_argument("--aes", required=True)
    sign.add_argument("--url", required=True)
    sign.add_argument("--param-json", required=True)
    sign.add_argument("--body", default=None)

    args = parser.parse_args()

    if args.cmd == "encrypt":
        cmd_encrypt(args)
    elif args.cmd == "decrypt":
        cmd_decrypt(args)
    elif args.cmd == "param":
        cmd_param(args)
    elif args.cmd == "sign":
        cmd_sign(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
