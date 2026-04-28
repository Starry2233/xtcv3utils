"""
V3 加密客户端

封装完整的 V3 请求加密和响应解密逻辑。
对应 Android:
  - com.xtc.httplib.okhttp.HttpRequestInterceptor (请求加密)
  - com.xtc.httplib.okhttp.HttpHelper (工具方法)
  - com.xtc.httplib.bean.NetBaseRequestParam (基础参数)
"""

import json as json_lib
from datetime import datetime
from typing import Optional, Tuple

from .utils import aes_util, md5_util, gzip_util, uuid_util, base64_util


class V3Client:
    """XTC V3 加密客户端"""

    def __init__(
        self,
        aes_key: str,
        eebbk_key: str,
        key_id: str,
        watch_id: str,
        device_id: str,
        token: str,
        mac: str = "",
        app_id: str = "2",
        program: str = "watch",
        im_flag: str = "1",
        package_name: str = "com.xtc.moment",
        package_version: str = "1",
        model: str = "watch",
        regist_id: int = 0,
        default_rsa_public_key: Optional[str] = None,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S",
    ):
        """
        Args:
            aes_key: AES 密钥 (来自 AppInfo.setEncryptEebbkKey 解密后的 aesKey)
            eebbk_key: RSA 加密后的 Eebbk-Key (来自 AppInfo.encryptEebbkKey)
            key_id: 密钥 ID (来自 AppInfo.keyId)
            watch_id: 用户 accountId
            device_id: 设备号 / 绑定手机号
            token: 芯片 ID / IMEI
            mac: MAC 地址
            app_id: 应用 ID (默认 "2")
            program: 程序名 (默认 "watch")
            im_flag: IM 标志 (默认 "1")
            regist_id: 注册 ID
        """
        self.aes_key = aes_key
        self.eebbk_key = eebbk_key
        self.key_id = key_id
        self.watch_id = watch_id
        self.device_id = device_id
        self.token = token
        self.mac = mac
        self.app_id = app_id
        self.program = program
        self.im_flag = im_flag
        self.package_name = package_name
        self.package_version = package_version
        self.model = model
        self.regist_id = regist_id
        self.default_rsa_public_key = default_rsa_public_key
        self.timestamp_format = timestamp_format

    # ============================================================
    # 公开 API
    # ============================================================

    def build_base_param_json(self) -> str:
        """构造 NetBaseRequestParam JSON

        对应 Android HttpHelper.buildBaseRequestParamJson()
        """
        param = {
            "imFlag": self.im_flag,
            "appId": self.app_id,
            "program": self.program,
            "timestamp": datetime.now().strftime(self.timestamp_format),
            "deviceId": self.device_id,
            "token": self.token,
            "mac": self.mac,
            "accountId": self.watch_id,
            "registId": self.regist_id,
            "requestId": uuid_util.generate(),
        }
        # 过滤 None / 空值（与 Android 保持一致）
        return json_lib.dumps(param, separators=(",", ":"))

    def generate_sign(self, url: str, base_param_json: str, body: Optional[str]) -> str:
        """生成 Eebbk-Sign

        对应 Android HttpHelper.generateSign():
          MD5(url + baseParamJson + requestBody + aesKey)
        """
        data = url.encode("utf-8")
        data += base_param_json.encode("utf-8")
        if body:
            data += body.encode("utf-8")
        data += self.aes_key.encode("utf-8")
        return md5_util.sign(data)

    def encrypt_base_param(self, base_param_json: str) -> str:
        """加密 Base-Request-Param

        对应 Android generateEncryptRequestParam():
          Base64(AES_ECB(param_json, aesKey))
        """
        return aes_util.encrypt_to_base64(base_param_json, self.aes_key)

    def encrypt_body(self, body: str) -> str:
        """加密请求体: AES(GZip(body)) → Base64

        对应 Android generateEncryptBody():
          Base64(AES_ECB(GZip(body), aesKey))
        """
        return self._aes_encrypt_bytes(gzip_util.compress_str(body))

    def _aes_encrypt_bytes(self, data: bytes) -> str:
        """AES/ECB 加密字节数据 → Base64"""
        from Crypto.Cipher import AES

        cipher = AES.new(self.aes_key.encode("utf-8"), AES.MODE_ECB)
        pad_len = 16 - len(data) % 16
        padded = data + bytes([pad_len] * pad_len)
        encrypted = cipher.encrypt(padded)
        return base64_util.encode(encrypted)

    def encrypt_request(
        self,
        url: str,
        body: Optional[str] = None,
        extra_headers: Optional[dict] = None,
    ) -> Tuple[dict, Optional[str]]:
        """加密完整请求，返回 (headers, encrypted_body)

        Args:
            url: 完整请求 URL (sign 会自动去掉 query params)
            body: 原始请求体 JSON 字符串 (如 '{"content":"hello","type":3}')
            extra_headers: 额外需要添加的请求头

        Returns:
            (headers_dict, encrypted_body_or_None)
        """
        # 1. 构造基础参数
        base_param_json = self.build_base_param_json()

        # 2. 判断是否需要加密 body
        is_encrypt = body is not None and len(body) > 0

        # 3. 生成签名 (用不带 query param 的 URL)
        sign_url = url.split("?")[0]  # 去掉 ?uuid=xxx
        sign = self.generate_sign(sign_url, base_param_json, body)

        # 4. 加密基础参数
        encrypted_param = self.encrypt_base_param(base_param_json)

        # 5. 构造 headers
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Eebbk-Sign": sign,
            "Base-Request-Param": encrypted_param,
            "model": self.model,
            "imSdkVersion": "102",
            "packageVersion": self.package_version,
            "packageName": self.package_name,
        }

        # V3 特有的 key 相关 header
        if self.key_id:
            headers["Eebbk-Key-Id"] = self.key_id
        if self.eebbk_key and is_encrypt:
            headers["Eebbk-Key"] = self.eebbk_key
            headers["encrypted"] = "encrypted"
            headers["Content-Encoding"] = "gzip"

        # 6. 合并额外 headers
        if extra_headers:
            headers.update(extra_headers)

        # 7. 加密 body
        encrypted_body = None
        if is_encrypt and self.eebbk_key:
            encrypted_body = self.encrypt_body(body)
        elif body is not None:
            encrypted_body = body

        return headers, encrypted_body

    def decrypt_response(
        self,
        response_body: str,
        is_encrypted: bool = True,
    ) -> str:
        """解密服务端响应

        对应 Android HttpHelper.decodeHttpResponseBody():
          去掉引号 → AES 解密 → GZip 解压

        Args:
            response_body: 服务端返回的 body 字符串
            is_encrypted: 响应是否加密（检查 header 是否有 "encrypted"）

        Returns:
            解密后的明文字符串
        """
        if not is_encrypted or not response_body:
            return response_body

        # 去掉引号 (Android: str.replace("\"", ""))
        body = response_body.replace('"', "")

        try:
            # AES 解密
            decrypted = aes_util.decrypt_from_base64(body, self.aes_key)
            # GZip 解压
            return gzip_util.decompress_to_str(decrypted)
        except Exception:
            # 如果解密失败，返回原始内容
            return response_body


def create_client_from_decrypted_keys(
    decrypted_key_str: str,
    watch_id: str,
    device_id: str,
    token: str,
    mac: str = "",
    **kwargs,
) -> V3Client:
    """从解密后的密钥字符串创建客户端

    对应 Android AppInfo.setEncryptEebbkKey():
      格式: "keyId:aesKey:rsaEncryptedEebbkKey"

    Args:
        decrypted_key_str: "keyId:aesKey:eebbkKey" 格式
        watch_id: 用户 ID
        device_id: 设备号
        token: 芯片 ID
        mac: MAC 地址
    """
    parts = decrypted_key_str.split(":")
    if len(parts) < 3:
        raise ValueError(f"密钥格式错误，需要 'keyId:aesKey:eebbkKey'，实际: {decrypted_key_str}")
    return V3Client(
        aes_key=parts[1],
        eebbk_key=parts[2],
        key_id=parts[0],
        watch_id=watch_id,
        device_id=device_id,
        token=token,
        mac=mac,
        **kwargs,
    )
