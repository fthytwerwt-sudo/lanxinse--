#!/usr/bin/env python3
"""检查阿里 API 配置骨架是否混入真实 key 或危险提交。"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FILES_TO_SCAN = [
    ROOT / ".env.example",
    ROOT / "config" / "ali_model_config.yaml",
    ROOT / "config" / "ali_model_config_readme.md",
    ROOT / "执行日志_codex_log" / "103_阿里API配置骨架创建报告_ali_api_config_scaffold_report.md",
    ROOT / "执行日志_codex_log" / "104_阿里模型接入验证报告_ali_model_live_connection_report.md",
    ROOT / "执行日志_codex_log" / "105_阿里视觉模型迁移验证报告_ali_vision_model_migration_report.md",
    ROOT / "执行日志_codex_log" / "106_阿里模型重连验证报告_ali_model_reconnect_after_env_update_report.md",
    ROOT / "api_outputs" / "ali_model_live_test_results.json",
    ROOT / "api_outputs" / "ali_vision_model_migration_results.json",
]

PLACEHOLDER_VALUES = {
    "",
    "your_api_key_here",
    "your-ali-api-key",
    "你的真实阿里 API key",
    "这里填你的真实阿里 API key",
    "请在本地填写，不要提交真实 key",
}

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"(?i)\b(access[_-]?key|secret[_-]?key|api[_-]?key|token)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{20,}"),
    re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9_./+=-]{20,}"),
]


def fail(message: str) -> None:
    print(f"安全检查失败：{message}")
    sys.exit(1)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def check_api_key_assignment(path: Path, text: str) -> None:
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith("ALI_API_KEY="):
            continue
        value = line.split("=", 1)[1].strip().strip('"').strip("'")
        if value not in PLACEHOLDER_VALUES:
            fail(f"{path.relative_to(ROOT)}:{line_no} 疑似把真实 ALI_API_KEY 写入可提交文件")


def check_secret_like_text(path: Path, text: str) -> None:
    for pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0)
            if "ALI_API_KEY" in snippet or "api_key_env" in snippet:
                continue
            fail(f"{path.relative_to(ROOT)} 疑似包含真实 secret：{snippet[:12]}***")


def check_scan_files() -> None:
    for path in FILES_TO_SCAN:
        text = read_text(path)
        if not text:
            print(f"跳过不存在或为空的文件：{path.relative_to(ROOT)}")
            continue
        check_api_key_assignment(path, text)
        check_secret_like_text(path, text)
        print(f"已检查：{path.relative_to(ROOT)}")


def check_gitignore() -> None:
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        fail(".gitignore 不存在")

    lines = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    required = {".env", ".env.*", "!.env.example", "api_outputs/"}
    missing = sorted(required - lines)
    if missing:
        fail(f".gitignore 缺少规则：{', '.join(missing)}")
    print("已确认 .gitignore 包含 .env 防误提交规则。")


def check_ignored_paths() -> None:
    paths = [
        ".env",
        "api_outputs/ali_model_live_test_results.json",
        "api_outputs/ali_vision_model_migration_results.json",
    ]
    for path in paths:
        result = subprocess.run(
            ["git", "check-ignore", "-q", path],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{path} 未被 .gitignore 忽略")
    print("已确认 .env 和 api_outputs 本地结果文件被 Git 忽略。")


def staged_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"无法读取 staged files：{result.stderr.strip()}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_staged_env_files() -> None:
    risky = []
    for path in staged_files():
        name = Path(path).name
        if name.startswith(".env") and name != ".env.example":
            risky.append(path)
        if path.startswith("api_outputs/"):
            risky.append(path)
    if risky:
        fail(f"staged files 中包含禁止提交的本地文件：{', '.join(risky)}")
    print("已确认 staged files 不包含真实 .env 或 api_outputs。")


def main() -> int:
    print("阿里 API 配置安全检查")
    check_scan_files()
    check_gitignore()
    check_ignored_paths()
    check_staged_env_files()
    print("安全检查通过：未发现真实 key、.env staged 或缺失忽略规则。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
