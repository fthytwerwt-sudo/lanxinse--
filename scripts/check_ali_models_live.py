#!/usr/bin/env python3
"""逐个检查阿里模型角色的最小 live 连接状态。

本脚本只执行小请求：
- 文本 / 结构化 / Omni 使用极短文本 prompt。
- 视觉使用内置 1x1 PNG data URL，不读取或上传真实素材。
- 音频转写不上传音频；Paraformer 需要专用 SDK / 文件 URL 路线，本轮只标记待验证。

输出：
- 本地 JSON：api_outputs/ali_model_live_test_results.json（不提交）
- 可提交报告：执行日志_codex_log/104_阿里模型接入验证报告_ali_model_live_connection_report.md
- 更新配置：config/ali_model_config.yaml
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
CONFIG_PATH = ROOT / "config" / "ali_model_config.yaml"
REPORT_PATH = ROOT / "执行日志_codex_log" / "104_阿里模型接入验证报告_ali_model_live_connection_report.md"
OUTPUT_PATH = ROOT / "api_outputs" / "ali_model_live_test_results.json"

DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
TINY_PNG_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}


@dataclass(frozen=True)
class RoleSpec:
    role: str
    purpose: str
    primary_candidates: tuple[str, ...]
    kind: str
    env_key: str | None = None
    fallback_route: str | None = None


ROLE_SPECS = [
    RoleSpec(
        role="text_analysis",
        purpose="文本分析、结构总结、候选解释",
        primary_candidates=("qwen-plus-latest", "qwen-max-latest"),
        kind="text",
        env_key="ALI_MODEL_TEXT_ANALYSIS",
    ),
    RoleSpec(
        role="structured_output",
        purpose="JSON 输出、字段归一、供料包清洗",
        primary_candidates=("qwen-plus-latest", "qwen-max-latest"),
        kind="structured",
        env_key="ALI_MODEL_STRUCTURED_OUTPUT",
    ),
    RoleSpec(
        role="vision_analysis",
        purpose="关键帧理解、画面摘要、人物动作识别",
        primary_candidates=("qwen3-vl-plus", "qwen-vl-plus", "qwen-vl-plus-latest"),
        kind="vision",
        env_key="ALI_MODEL_VISION_ANALYSIS",
    ),
    RoleSpec(
        role="vision_high",
        purpose="复杂画面和高价值候选片段视觉复核",
        primary_candidates=("qwen3-vl-max", "qwen-vl-max", "qwen-vl-max-latest"),
        kind="vision",
        env_key="ALI_MODEL_VISION_HIGH",
    ),
    RoleSpec(
        role="omni_analysis",
        purpose="音视频综合观察，语气、动作、画面联合理解",
        primary_candidates=("qwen-omni-turbo-latest",),
        kind="omni_text",
        env_key="ALI_MODEL_OMNI_ANALYSIS",
    ),
    RoleSpec(
        role="audio_transcription",
        purpose="直播口播转写和时间码文本供料，可由本地 Whisper fallback",
        primary_candidates=("paraformer-v2",),
        kind="audio_manual",
        env_key="ALI_MODEL_AUDIO_TRANSCRIPTION",
        fallback_route="local_faster_whisper",
    ),
    RoleSpec(
        role="fallback_text",
        purpose="文本模型备用",
        primary_candidates=("qwen-turbo-latest", "qwen-plus-latest"),
        kind="text",
        env_key="ALI_MODEL_FALLBACK_TEXT",
    ),
    RoleSpec(
        role="fallback_vision",
        purpose="视觉模型备用",
        primary_candidates=("qwen-vl-plus-latest",),
        kind="vision",
        env_key="ALI_MODEL_FALLBACK_VISION",
    ),
]


def load_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env_value(values: dict[str, str], key: str, default: str = "") -> str:
    return values.get(key) or os.environ.get(key, default)


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
    return value.strip() in PLACEHOLDER_VALUES


def sanitize_text(text: str, api_key: str) -> str:
    sanitized = text.replace(api_key, "<redacted_api_key>") if api_key else text
    sanitized = re.sub(r"(?i)bearer\s+[A-Za-z0-9_./+=-]{12,}", "Bearer <redacted>", sanitized)
    sanitized = re.sub(r"\bsk-[A-Za-z0-9_-]{10,}\b", "<redacted_secret>", sanitized)
    sanitized = sanitized.replace("\n", " ").replace("\r", " ")
    return sanitized[:500]


def choose_model(spec: RoleSpec, values: dict[str, str]) -> str:
    if spec.env_key:
        configured = env_value(values, spec.env_key)
        if configured:
            return configured
    return spec.primary_candidates[0]


def build_payload(spec: RoleSpec, model: str) -> dict[str, Any]:
    if spec.kind == "structured":
        return {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": '请只输出 JSON：{"status":"ok"}',
                }
            ],
            "max_tokens": 32,
            "temperature": 0,
        }
    if spec.kind == "vision":
        return {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这是一张测试图。请只回复：ok"},
                        {"type": "image_url", "image_url": {"url": TINY_PNG_DATA_URL}},
                    ],
                }
            ],
            "max_tokens": 16,
            "temperature": 0,
        }
    if spec.kind == "omni_text":
        return {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "请回复：ok",
                }
            ],
            "max_tokens": 16,
            "temperature": 0,
        }
    return {
        "model": model,
        "messages": [{"role": "user", "content": "请回复：ok"}],
        "max_tokens": 16,
        "temperature": 0,
    }


def classify_http_error(status_code: int, body: str) -> tuple[str, str]:
    error_type = f"http_{status_code}"
    summary = body
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {}
    error = parsed.get("error") if isinstance(parsed, dict) else None
    if isinstance(error, dict):
        code = str(error.get("code") or "")
        message = str(error.get("message") or "")
        err_type = str(error.get("type") or "")
        summary = " | ".join(part for part in [code, err_type, message] if part)
        lowered = f"{code} {err_type} {message}".lower()
        if "invalid_api_key" in lowered or "incorrect api key" in lowered or status_code == 401:
            error_type = "authentication_failed"
        elif status_code == 403 or "access" in lowered or "permission" in lowered:
            error_type = "permission_or_account_required"
        elif status_code == 404 or "not found" in lowered or "model" in lowered and "not" in lowered:
            error_type = "model_not_available"
        elif status_code == 429 or "quota" in lowered or "rate" in lowered:
            error_type = "quota_or_rate_limit"
    elif status_code == 401:
        error_type = "authentication_failed"
    elif status_code == 403:
        error_type = "permission_or_account_required"
    elif status_code == 404:
        error_type = "model_not_available"
    elif status_code == 429:
        error_type = "quota_or_rate_limit"
    return error_type, summary


def response_preview(body: str) -> str:
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body[:160]
    choices = parsed.get("choices") if isinstance(parsed, dict) else None
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, str):
                    return content.strip()[:160]
    return json.dumps(parsed, ensure_ascii=False)[:160]


def test_chat_role(spec: RoleSpec, model: str, values: dict[str, str], api_key: str) -> dict[str, Any]:
    base_url = env_value(values, "ALI_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    timeout = parse_int(env_value(values, "ALI_API_TIMEOUT_SECONDS", "60"), 60)
    endpoint = f"{base_url}/chat/completions"
    payload = build_payload(spec, model)
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
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            latency_ms = round((time.perf_counter() - started) * 1000)
    except urllib.error.HTTPError as exc:
        latency_ms = round((time.perf_counter() - started) * 1000)
        body = exc.read().decode("utf-8", errors="replace")
        error_type, summary = classify_http_error(exc.code, body)
        return {
            "role": spec.role,
            "model_name": model,
            "status": "failed",
            "latency_ms": latency_ms,
            "error_type": error_type,
            "error_summary": sanitize_text(summary, api_key),
            "response_preview": None,
        }
    except TimeoutError:
        latency_ms = round((time.perf_counter() - started) * 1000)
        return {
            "role": spec.role,
            "model_name": model,
            "status": "failed",
            "latency_ms": latency_ms,
            "error_type": "endpoint_timeout",
            "error_summary": f"请求超过 {timeout} 秒未返回",
            "response_preview": None,
        }
    except urllib.error.URLError as exc:
        latency_ms = round((time.perf_counter() - started) * 1000)
        return {
            "role": spec.role,
            "model_name": model,
            "status": "failed",
            "latency_ms": latency_ms,
            "error_type": "endpoint_failed",
            "error_summary": sanitize_text(str(exc.reason), api_key),
            "response_preview": None,
        }

    return {
        "role": spec.role,
        "model_name": model,
        "status": "connected",
        "latency_ms": latency_ms,
        "error_type": None,
        "error_summary": None,
        "response_preview": sanitize_text(response_preview(body), api_key),
    }


def test_role(spec: RoleSpec, values: dict[str, str], api_key: str) -> dict[str, Any]:
    model = choose_model(spec, values)
    if spec.kind == "audio_manual":
        return {
            "role": spec.role,
            "model_name": model,
            "status": "pending_validation",
            "latency_ms": None,
            "error_type": "pending_manual_route_or_local_whisper",
            "error_summary": (
                "paraformer-v2 需要 DashScope 音频转写 SDK 或文件 URL 任务路线；"
                "本轮不上传音频，保留 local_faster_whisper fallback。"
            ),
            "response_preview": None,
        }
    return test_chat_role(spec, model, values, api_key)


def yaml_quote(value: str | None) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def render_yaml(results: list[dict[str, Any]], tested_at: str) -> str:
    by_role = {result["role"]: result for result in results}
    connected_count = sum(1 for result in results if result["status"] == "connected")
    failed_count = sum(1 for result in results if result["status"] == "failed")
    pending_count = sum(1 for result in results if result["status"] == "pending_validation")
    final_status = "partial_connected_with_failed_models" if failed_count else "ali_models_connected_partial_or_completed_pending_probe"

    lines = [
        "# 阿里云百炼 / DashScope 模型配置",
        "# 状态说明：本文件记录模型角色和最小 live test 结果；连接成功不代表解析效果、成本或稳定性已确认。",
        "",
        "provider:",
        '  name: "aliyun_bailian_dashscope"',
        '  display_name: "阿里云百炼 / DashScope"',
        f"  status: {yaml_quote(final_status)}",
        '  api_key_env: "ALI_API_KEY"',
        '  base_url_env: "ALI_API_BASE_URL"',
        "",
        "models:",
        "  text_analysis:",
        '    env_key: "ALI_MODEL_TEXT_ANALYSIS"',
        '    default_model: "qwen-plus-latest"',
        '    status: "待验证"',
        '    purpose: "文本分析、结构总结、规则归纳、候选解释"',
        '    notes: "以 model_roles.text_analysis 的 live test 状态为准"',
        "",
        "  vision_analysis:",
        '    env_key: "ALI_MODEL_VISION_ANALYSIS"',
        '    default_model: "qwen-vl-plus-latest"',
        '    status: "待验证"',
        '    purpose: "关键帧、画面、人物动作、字幕画面理解"',
        '    notes: "以 model_roles.vision_analysis 的 live test 状态为准"',
        "",
        "  vision_high:",
        '    env_key: "ALI_MODEL_VISION_HIGH"',
        '    default_model: "qwen-vl-max-latest"',
        '    status: "待验证"',
        '    purpose: "复杂画面、高价值候选片段复核"',
        '    notes: "成本可能更高，默认不用于全量"',
        "",
        "  audio_analysis:",
        '    env_key: "ALI_MODEL_OMNI_ANALYSIS"',
        '    default_model: "qwen-omni-turbo-latest"',
        '    status: "待验证"',
        '    purpose: "音频解析、口播内容理解、声音线索提取"',
        '    notes: "音频转写以 model_roles.audio_transcription 的后续专用路线为准"',
        "",
        "  video_analysis:",
        '    env_key: "ALI_MODEL_OMNI_ANALYSIS"',
        '    default_model: "qwen-omni-turbo-latest"',
        '    status: "待验证"',
        '    purpose: "视频片段理解、画面和声音的综合观察"',
        '    notes: "本轮不上传视频；后续小样本 probe 通过前不得全量解析"',
        "",
        "  omni_analysis:",
        '    env_key: "ALI_MODEL_OMNI_ANALYSIS"',
        '    default_model: "qwen-omni-turbo-latest"',
        '    status: "待验证"',
        '    purpose: "音频 + 视频综合理解，适合直播片段多模态观察"',
        '    notes: "以 model_roles.omni_analysis 的 live test 状态为准"',
        "",
        "  structured_output:",
        '    env_key: "ALI_MODEL_STRUCTURED_OUTPUT"',
        '    default_model: "qwen-plus-latest"',
        '    status: "待验证"',
        '    purpose: "JSON 字段归一、解析结果修正、供料包清洗"',
        '    notes: "用于把模型输出整理成 Codex 可读结构"',
        "",
        "model_roles:",
    ]
    for spec in ROLE_SPECS:
        result = by_role[spec.role]
        selected_model = result["model_name"] if result["status"] == "connected" else None
        lines.extend(
            [
                f"  {spec.role}:",
                f"    purpose: {yaml_quote(spec.purpose)}",
                "    primary_candidates:",
            ]
        )
        for candidate in spec.primary_candidates:
            lines.append(f"      - {yaml_quote(candidate)}")
        if spec.fallback_route:
            lines.append(f"    fallback_route: {yaml_quote(spec.fallback_route)}")
        lines.extend(
            [
                f"    selected_model: {yaml_quote(selected_model)}",
                f"    tested_model: {yaml_quote(result['model_name'])}",
                f"    status: {yaml_quote(result['status'])}",
                f"    last_tested_at: {yaml_quote(tested_at)}",
                f"    last_latency_ms: {result['latency_ms'] if result['latency_ms'] is not None else 'null'}",
                f"    last_error_type: {yaml_quote(result['error_type'])}",
                f"    last_error_summary: {yaml_quote(result['error_summary'])}",
                "",
            ]
        )
    lines.extend(
        [
            "run_limits:",
            '  max_videos_per_run_env: "ALI_MAX_VIDEOS_PER_RUN"',
            '  max_frames_per_video_env: "ALI_MAX_FRAMES_PER_VIDEO"',
            '  timeout_seconds_env: "ALI_API_TIMEOUT_SECONDS"',
            '  live_test_enabled_env: "ALI_API_ENABLE_LIVE_TEST"',
            '  allow_video_upload_env: "ALI_ALLOW_VIDEO_UPLOAD"',
            "",
            "cost_control:",
            '  status: "待验证"',
            "  default_live_test: false",
            "  default_allow_video_upload: false",
            "  full_batch_parse_allowed: false",
            '  notes: "本轮只做最小连接测试；真实素材 probe 和全量解析必须另行确认"',
            "",
            "probe_policy:",
            '  current_round: "model_live_connection_only"',
            "  live_api_call_this_round: true",
            "  video_upload_this_round: false",
            '  next_step_after_connected_models: "run_1_to_3_short_material_probe"',
            "",
            "live_test_summary:",
            f"  last_tested_at: {yaml_quote(tested_at)}",
            f"  total_roles: {len(results)}",
            f"  connected_count: {connected_count}",
            f"  failed_count: {failed_count}",
            f"  pending_count: {pending_count}",
            f"  final_status: {yaml_quote(final_status)}",
            '  output_json: "api_outputs/ali_model_live_test_results.json"',
            '  report: "执行日志_codex_log/104_阿里模型接入验证报告_ali_model_live_connection_report.md"',
            "",
            "decision_boundary:",
            '  ali_role: "只做解析供料，不做最终剪辑决策"',
            '  codex_role: "读取阿里供料包后做候选池、结构公式、初剪决策"',
            '  human_role: "剪映深加工、审美、人感、业务事实和最终发布判断"',
            "",
        ]
    )
    return "\n".join(lines)


def next_action(result: dict[str, Any]) -> str:
    role = result["role"]
    status = result["status"]
    error_type = result.get("error_type")
    if status == "connected":
        if role in {"text_analysis", "structured_output", "fallback_text"}:
            return "可进入文本 / 时间码供料小样本 probe"
        if role in {"vision_analysis", "vision_high", "fallback_vision"}:
            return "可进入抽帧 + 视觉小样本 probe"
        if role == "omni_analysis":
            return "可进入 1 条短视频素材 probe，但不得直接全量"
    if error_type == "model_not_available":
        return "检查模型名或替换候选模型"
    if error_type == "permission_or_account_required":
        return "到阿里控制台检查权限 / 服务开通"
    if error_type == "authentication_failed":
        return "检查 .env 中 API key 是否正确"
    if error_type == "quota_or_rate_limit":
        return "先处理额度 / 频控，不跑全量"
    if error_type == "pending_manual_route_or_local_whisper":
        return "后续走 DashScope 音频转写专用路线或本地 faster-whisper"
    return "保留错误摘要，先不进入该模型路线"


def table_cell(value: Any) -> str:
    text = str(value)
    return text.replace("|", "/").replace("\n", " ").replace("\r", " ")


def render_report(results: list[dict[str, Any]], tested_at: str, values: dict[str, str], api_key: str) -> str:
    connected_count = sum(1 for result in results if result["status"] == "connected")
    failed_count = sum(1 for result in results if result["status"] == "failed")
    pending_count = sum(1 for result in results if result["status"] == "pending_validation")
    final_status = "partial_connected_with_failed_models" if failed_count else "ali_models_connected_partial_or_completed_pending_probe"
    model_rows = []
    for result in results:
        status_note = {
            "connected": "最小连接成功；不代表真实素材解析效果已确认",
            "failed": result.get("error_summary") or "最小连接失败",
            "pending_validation": result.get("error_summary") or "本轮未做 live 调用",
        }.get(result["status"], "待验证")
        model_rows.append(
            "| {role} | `{model}` | `{status}` | {latency} | `{error_type}` | {note} | {next_action} |".format(
                role=table_cell(result["role"]),
                model=table_cell(result["model_name"]),
                status=table_cell(result["status"]),
                latency=result["latency_ms"] if result["latency_ms"] is not None else "-",
                error_type=table_cell(result["error_type"] or "-"),
                note=table_cell(status_note),
                next_action=table_cell(next_action(result)),
            )
        )
    return "\n".join(
        [
            "# 阿里模型接入验证报告",
            "",
            f"状态：`{final_status}`",
            f"生成时间：{tested_at}",
            "任务类型：`ali_api_model_live_connection_setup`",
            "",
            "## 1. 执行结果",
            "",
            "| 项目 | 结果 |",
            "|---|---|",
            "| 当前仓库 | `fthytwerwt-sudo/lanxinse--` |",
            "| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |",
            "| 当前分支 | `main` |",
            "| 当前 remote | `https://github.com/fthytwerwt-sudo/lanxinse--.git` |",
            "| `.env` 是否存在 | 是 |",
            "| API key 是否读取 | yes，只记录掩码，不写完整 key |",
            f"| API key 掩码 | `{mask_secret(api_key)}` |",
            f"| API base URL | `{env_value(values, 'ALI_API_BASE_URL', DEFAULT_BASE_URL)}` |",
            f"| 测试模型角色数 | {len(results)} |",
            f"| connected 数 | {connected_count} |",
            f"| failed 数 | {failed_count} |",
            f"| pending 数 | {pending_count} |",
            "| 是否上传真实素材 | 否 |",
            "| 是否跑全量解析 | 否 |",
            "| 是否提交 `.env` | 否 |",
            "| 本地 JSON 输出 | `api_outputs/ali_model_live_test_results.json`，不提交 GitHub |",
            f"| 最终状态 | `{final_status}` |",
            "",
            "## 2. 模型接入结果表",
            "",
            "| role | model_name | status | latency_ms | error_type | 中文说明 | 下一步动作 |",
            "|---|---|---|---:|---|---|---|",
            *model_rows,
            "",
            "## 3. 边界确认",
            "",
            "| 边界 | 结果 |",
            "|---|---|",
            "| 是否打印完整 key | 否 |",
            "| 是否提交 `.env` | 否 |",
            "| 是否提交 API key | 否 |",
            "| 是否上传真实素材 | 否 |",
            "| 是否提交 `api_outputs/` | 否 |",
            "| 是否跑全量解析 | 否 |",
            "| 是否产生媒体文件 | 否 |",
            "| 是否确认模型效果好 | 否 |",
            "| 是否确认成本可接受 | 否 |",
            "| 是否确认全量稳定 | 否 |",
            "",
            "## 4. 下一步建议",
            "",
            "- 如果文本、视觉、Omni 至少各有一个 `connected`，下一步可以做 1 条短视频素材解析 probe。",
            "- 如果只有文本模型 `connected`，先做文本 / 时间码路线。",
            "- 如果视觉模型失败，先修视觉模型名或账号权限。",
            "- 如果 Omni 失败，不阻断抽帧 + 视觉模型路线。",
            "- 不直接进入全量解析；全量前必须先完成小样本素材 probe。",
            "",
            "## 5. 当前限制",
            "",
            "本报告只证明最小 API 请求的连通性，不证明真实直播素材解析质量、长视频支持、费用、限额、速度或稳定性。",
            "",
        ]
    )


def main() -> int:
    if not ENV_PATH.exists():
        print("blocked_missing_env：未发现 .env，请先 cp .env.example .env 并填写 ALI_API_KEY。")
        return 2

    values = load_dotenv(ENV_PATH)
    api_key = env_value(values, "ALI_API_KEY")
    if is_placeholder_key(api_key):
        print("blocked_missing_api_key：.env 中 ALI_API_KEY 为空或仍是占位符。")
        return 2

    tested_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    print("阿里模型最小 live test")
    print(f"- API key: {mask_secret(api_key)}")
    print(f"- base_url: {env_value(values, 'ALI_API_BASE_URL', DEFAULT_BASE_URL)}")
    print("- 不上传真实素材；视觉仅使用内置 1x1 测试 PNG；音频转写不上传音频。")

    results = []
    for spec in ROLE_SPECS:
        result = test_role(spec, values, api_key)
        results.append(result)
        status = result["status"]
        latency = result["latency_ms"] if result["latency_ms"] is not None else "-"
        error_type = result["error_type"] or "-"
        print(f"- {spec.role}: {result['model_name']} -> {status}, latency_ms={latency}, error_type={error_type}")

    connected_count = sum(1 for result in results if result["status"] == "connected")
    failed_count = sum(1 for result in results if result["status"] == "failed")
    all_live_failed = connected_count == 0 and failed_count > 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "tested_at": tested_at,
        "api_base_url": env_value(values, "ALI_API_BASE_URL", DEFAULT_BASE_URL),
        "api_key_masked": mask_secret(api_key),
        "real_material_uploaded": False,
        "full_batch_parse_run": False,
        "results": results,
        "summary": {
            "total_roles": len(results),
            "connected_count": connected_count,
            "failed_count": failed_count,
            "pending_count": sum(1 for result in results if result["status"] == "pending_validation"),
            "final_status": (
                "partial_connected_with_failed_models"
                if failed_count
                else "ali_models_connected_partial_or_completed_pending_probe"
            ),
        },
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CONFIG_PATH.write_text(render_yaml(results, tested_at), encoding="utf-8")
    REPORT_PATH.write_text(render_report(results, tested_at, values, api_key), encoding="utf-8")

    print(f"已写入本地 JSON：{OUTPUT_PATH.relative_to(ROOT)}")
    print(f"已更新配置：{CONFIG_PATH.relative_to(ROOT)}")
    print(f"已生成报告：{REPORT_PATH.relative_to(ROOT)}")
    if all_live_failed:
        print("blocked_all_models_failed_or_key_invalid：所有 live API 模型均失败，请检查 key、endpoint 或账号权限。")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
