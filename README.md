# xtcv3utils

XTC V3 API 加密/解密工具

V3 API encryption/decryption utilities (protocol implementation for XTC services).

## 安装 / Install

```bash
pip install xtcv3utils
```

需要依赖 `pycryptodome`。

## 快速开始 / Quick Start

```python
from xtcv3utils import V3Client

client = V3Client(
    aes_key="your-aes-key",
    eebbk_key="rsa-encrypted-eebbk-key",
    key_id="your-key-id",
    watch_id="your-watch-id",
    device_id="bind-number",
    token="chip-id",
    mac="mac-address",
)

# 加密请求
headers, encrypted_body = client.encrypt_request(
    url="https://api.example.com/moment/public",
    body='{"watchId":"your-watch-id","content":"hello","type":3}',
)

# 解密响应
plain_text = client.decrypt_response(
    response_body=response_text,
    is_encrypted=True,
)
```

## API

### `V3Client`

| 方法 | 说明 |
|------|------|
| `encrypt_request(url, body, extra_headers)` | 加密完整请求，返回 `(headers, encrypted_body)` |
| `decrypt_response(response_body, is_encrypted)` | 解密服务器响应 |
| `build_base_param_json()` | 构建基础参数 JSON（deviceId, token, timestamp 等） |
| `generate_sign(url, base_param_json, body)` | 计算 Eebbk-Sign |

### `create_client_from_decrypted_keys(key_str, ...)`

从 `"keyId:aesKey:eebbkKey"` 格式的密钥字符串直接创建客户端。

## V3 加密原理

| 步骤 | 算法 | 用途 |
|------|------|------|
| 密钥传输 | RSA/ECB/PKCS1Padding | 安全分发 AES 密钥 |
| 参数加密 | AES/ECB/PKCS5Padding | 加密设备信息 (`Base-Request-Param`) |
| Body 加密 | GZip → AES/ECB/PKCS5Padding → Base64 | 压缩并加密请求体 |
| 签名 | `MD5(url + baseParam + body + aesKey)` | 请求完整性校验 |
| 响应解密 | AES 解密 → GZip 解压 | 读取加密响应 |

签名使用的 URL **不包含** `?uuid=xxx` 参数（uuid 在签名完成后才追加）。

## 相关项目

- [Frida hook 脚本](dump_key.js) — 运行时提取 AES 密钥
- [加密请求脚本](encrypt_request.py) — 命令行加密并生成 curl 命令
- [HttpCanary 解密脚本](decrypt_httpcanary.py) — 解密抓包文件

## License

MIT
