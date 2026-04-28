"""UUID 生成器（去掉横线）

对应 Android: com.xtc.utils.encode.m (UUIDUtil.java)
格式: UUID.randomUUID().toString() 去掉所有 "-"
"""

import uuid


def generate() -> str:
    """生成 32 位无横线 UUID"""
    return uuid.uuid4().hex
