#!/usr/bin/env python3
"""阿里 API 配置与最小连接检查。

默认只做本地配置检查。只有 ALI_API_ENABLE_LIVE_TEST=true 时，才会发起
一次最小文本模型请求；不会上传视频，不会跑全量解析。
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
ENV_EXAMPLE_PATH = ROOT / ".env.example"

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        values[key] = value
    return values


def env_value(values: dict[str, str], key: str, default: str = "") -> str:
    return values.get(key) or os.environ.get(key, default)


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_int(value: str, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def mask_secret(value: str) -> str:
    if not value:
        return "未填写"
    if len(value) <= 8:
        return value[:2] + "*" * max(len(value) - 2, 0)
    return f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"


def is_placeholder_key(value: str) -> bool:
    normalized = value.strip()
    return normalized in PLACEHOLDER_VALUES


def print_local_config(values: dict[str, str]) -> None:
    print("配置检查结果：")
    print(f"- ALI_API_BASE_URL: {env_value(values, 'ALI_API_BASE_URL') or '未填写'}")
    print(f"- ALI_MODEL_TEXT_ANALYSIS: {env_value(values, 'ALI_MODEL_TEXT_ANALYSIS') or '未填写'}（状态：待验证）")
    print(f"- ALI_MODEL_VISION_ANALYSIS: {env_value(values, 'ALI_MODEL_VISION_ANALYSIS') or '未填写'}（状态：待验证）")
    print(f"- ALI_MODEL_VISION_HIGH: {env_value(values, 'ALI_MODEL_VISION_HIGH') or '未填写'}（状态：待验证）")
    print(f"- ALI_MODEL_OMNI_ANALYSIS: {env_value(values, 'ALI_MODEL_OMNI_ANALYSIS') or '未填写'}（状态：待验证）")
    print(f"- ALI_MODEL_STRUCTURED_OUTPUT: {env_value(values, 'ALI_MODEL_STRUCTURED_OUTPUT') or '未填写'}（状态：待验证）")
    print(f"- ALI_ALLOW_VIDEO_UPLOAD: {env_value(values, 'ALI_ALLOW_VIDEO_UPLOAD', 'false')}（本脚本不会上传视频）")


def run_live_text_probe(values: dict[str, str]) -> int:
    api_key = env_value(values, "ALI_API_KEY")
    base_url = env_value(values, "ALI_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = env_value(values, "ALI_MODEL_TEXT_ANALYSIS", "qwen-plus-latest")
    timeout = parse_int(env_value(values, "ALI_API_TIMEOUT_SECONDS", "60"), 60)

    endpoint = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "请只回复 pong，用于最小连通性检查。",
            }
        ],
        "max_tokens": 16,
        "temperature": 0,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    print("开始最小文本连接测试：")
    print(f"- API key: {mask_secret(api_key)}")
    print(f"- endpoint: {endpoint}")
    print(f"- model: {model}（状态：待验证）")
    print("- 本次不会上传视频，不会跑全量解析。")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"连接测试未通过：HTTP {exc.code}")
        print("请检查阿里控制台中的 API key、endpoint、模型名和账号权限。")
        if body:
            print(f"错误摘要：{body[:800]}")
        return 1
    except urllib.error.URLError as exc:
        print(f"连接测试未通过：{exc.reason}")
        print("请检查网络、endpoint 和阿里控制台服务开通状态。")
        return 1
    except TimeoutError:
        print(f"连接测试超时：{timeout} 秒")
        return 1

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        print("连接测试返回了非 JSON 响应，请检查 endpoint 是否正确。")
        print(f"响应摘要：{body[:500]}")
        return 1

    content = ""
    choices = parsed.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        if isinstance(message, dict):
            content = str(message.get("content", "")).strip()

    print("连接测试已返回响应。")
    print(f"- response_preview: {content[:120] if content else '未解析到文本内容'}")
    print("- 状态：只证明本次最小文本请求有响应，不代表视频理解、成本、额度、稳定性已确认。")
    return 0


def main() -> int:
    print("阿里 API 配置检查脚本")

    if not ENV_PATH.exists():
        print("未发现本地 .env。")
        print("请先执行：")
        print("cp .env.example .env")
        print("然后只在 .env 中填写 ALI_API_KEY。")
        return 0

    values = load_dotenv(ENV_PATH)
    if ENV_EXAMPLE_PATH.exists():
        print(f"已确认环境变量示例文件存在：{ENV_EXAMPLE_PATH.relative_to(ROOT)}")

    api_key = env_value(values, "ALI_API_KEY")
    if is_placeholder_key(api_key):
        print("ALI_API_KEY 尚未填写。")
        print("请打开 .env 并填写：")
        print("ALI_API_KEY=你的真实阿里 API key")
        return 0

    print(f"API key 已读取：{mask_secret(api_key)}")
    print_local_config(values)

    live_test = parse_bool(env_value(values, "ALI_API_ENABLE_LIVE_TEST", "false"))
    if not live_test:
        print("ALI_API_ENABLE_LIVE_TEST=false：本次只做本地配置检查，不真实调用 API。")
        return 0

    return run_live_text_probe(values)


if __name__ == "__main__":
    sys.exit(main())
