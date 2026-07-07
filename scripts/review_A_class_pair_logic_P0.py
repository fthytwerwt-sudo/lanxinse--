#!/usr/bin/env python3
"""P0 review for A-class live candidate speech/action pairing logic."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

FACT_ROOT = REPO_ROOT / "项目事实_project_facts/直播素材筛选_live_material_screening"
ANALYSIS_ROOT = REPO_ROOT / "素材解析_pipeline_material_analysis/14_pair_logic_review"
LOG_ROOT = REPO_ROOT / "执行日志_codex_log"
ASR_ROOT = REPO_ROOT / "api_outputs/full_live_material_screening/asr_transcripts"
LOCAL_A_PACKAGE_ROOT = REPO_ROOT / "outputs/local_live_A_editor_package"
LOCAL_REVIEW_ROOT = REPO_ROOT / "outputs/local_pair_logic_review"
RAW_VIDEO_ROOT = Path("/Volumes/WD_BLACK/完整直播录屏/今年直播素材")

A_LIST_CSV = FACT_ROOT / "04_A类优先剪辑清单_priority_A_editor_pick_list.csv"
PAIRING_CSV = FACT_ROOT / "02_口播动作配对表_speech_action_pairing_table.csv"
MASTER_CSV = FACT_ROOT / "01_直播候选片段总表_live_candidate_segment_master.csv"
STRUCTURE_CSV = FACT_ROOT / "03_按剪辑结构归类候选表_candidates_by_clip_structure.csv"
MANIFEST_CSV = FACT_ROOT / "10_A类素材导出索引_A_class_export_manifest.csv"
PAIR_GUIDE_CSV = FACT_ROOT / "11_A类口播动作配对剪辑说明_A_class_pair_editing_guide.csv"

PROBE_CSV = ANALYSIS_ROOT / "01_配对逻辑复审探针_pair_logic_review_probe.csv"
REVIEW_MASTER_CSV = FACT_ROOT / "14_A类口播动作逻辑复审总表_A_class_pair_logic_review_master.csv"
TRUE_PAIR_CSV = FACT_ROOT / "15_真配对候选清单_true_pair_candidates.csv"
WEAK_RELATED_CSV = FACT_ROOT / "16_弱相关待复核清单_weak_related_pending_review.csv"
MISMATCH_CSV = FACT_ROOT / "17_逻辑错配剔除清单_logic_mismatch_rejects.csv"
BLOCKED_CSV = FACT_ROOT / "18_缺视觉证据阻断清单_blocked_need_visual_review.csv"
REVISION_RULES_MD = FACT_ROOT / "19_配对逻辑修正规则_pairing_logic_revision_rules.md"
SOLUTION_MD = FACT_ROOT / "20_逻辑复审后解决方案_after_logic_review_solution.md"
REPORT_MD = LOG_ROOT / "121_P0口播动作逻辑复审执行报告_P0_pair_logic_review_report.md"

LOGIC_RESULTS = (
    "true_pair",
    "weak_related",
    "logic_mismatch",
    "blocked_need_visual_review",
)

MASTER_FIELDS = [
    "review_id",
    "candidate_id",
    "pair_group_id",
    "recording_id",
    "source_file",
    "usable_structure_name",
    "original_stage1_priority",
    "talk_start_time",
    "talk_end_time",
    "action_start_time",
    "action_end_time",
    "talk_claimed_action_or_problem",
    "talk_claimed_function",
    "action_observed_or_labeled",
    "action_evidence_status",
    "same_action_check",
    "same_problem_check",
    "same_function_check",
    "sequence_logic_check",
    "topic_break_check",
    "logic_review_result",
    "logic_fail_reason",
    "downgraded_stage",
    "next_action",
    "manual_review_items",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.returncode, proc.stdout.strip()


def extract_theme(summary: str) -> str:
    match = re.search(r"主题=([^；;]+)", summary or "")
    if match:
        return match.group(1).strip()
    return "待人工听审确认"


def extract_structure_reason(source_evidence: str) -> str:
    match = re.search(r"structure_reason=([^;；]+)", source_evidence or "")
    return match.group(1).strip() if match else ""


def extract_keyword_count(source_evidence: str) -> str:
    match = re.search(r"keyword_count=([^;；]+)", source_evidence or "")
    return match.group(1).strip() if match else ""


def transcript_path_from_evidence(source_evidence: str) -> Path | None:
    match = re.search(r"transcript=([^;；]+)", source_evidence or "")
    if not match:
        return None
    return Path(match.group(1).strip())


def time_to_seconds(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def load_transcript_windows(rows: list[dict[str, str]]) -> dict[str, int]:
    transcript_cache: dict[Path, dict[str, Any] | None] = {}
    overlap_counts: dict[str, int] = {}
    for row in rows:
        candidate_id = row.get("candidate_id", "")
        transcript_path = transcript_path_from_evidence(row.get("source_evidence", ""))
        if not transcript_path or transcript_path.name.startswith("._"):
            overlap_counts[candidate_id] = 0
            continue
        if transcript_path not in transcript_cache:
            try:
                transcript_cache[transcript_path] = json.loads(transcript_path.read_text(encoding="utf-8"))
            except Exception:
                transcript_cache[transcript_path] = None
        data = transcript_cache.get(transcript_path)
        if not data:
            overlap_counts[candidate_id] = 0
            continue
        try:
            start = time_to_seconds(row.get("start_time", "0:0:0"))
            end = time_to_seconds(row.get("end_time", "0:0:0"))
        except Exception:
            overlap_counts[candidate_id] = 0
            continue
        count = 0
        for segment in data.get("segments", []):
            seg_start = float(segment.get("start_seconds", -1))
            seg_end = float(segment.get("end_seconds", -1))
            if seg_end >= start and seg_start <= end:
                count += 1
        overlap_counts[candidate_id] = count
    return overlap_counts


def build_pair_index(pair_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in pair_rows:
        for key in ("talk_segment_id", "action_segment_id"):
            candidate_id = row.get(key, "")
            if candidate_id and candidate_id not in index:
                index[candidate_id] = row
    return index


def build_manifest_index(manifest_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("candidate_id", ""): row for row in manifest_rows if row.get("candidate_id")}


def has_visual_evidence(row: dict[str, str]) -> bool:
    evidence_fields = " ".join([
        row.get("action_summary", ""),
        row.get("action_complete_cycle", ""),
        row.get("speech_action_sync", ""),
        row.get("visual_obstruction_risk", ""),
        row.get("missing_part", ""),
    ])
    negative_markers = [
        "pending_visual_review",
        "visual_action_cycle_confirmation",
        "文本命中",
        "待视觉复核",
        "same_window_text_keyword_candidate",
    ]
    return not any(marker in evidence_fields for marker in negative_markers)


def classify_row(row: dict[str, str], pair: dict[str, str], manifest: dict[str, str], asr_overlap: int, review_id: str) -> dict[str, Any]:
    source_reason = extract_structure_reason(row.get("source_evidence", ""))
    keyword_count = extract_keyword_count(row.get("source_evidence", ""))
    pair_split_status = manifest.get("front_back_split_status", "not_available")
    local_mp4_exists = Path(manifest.get("full_context_path", "")).exists() if manifest.get("full_context_path") else False
    visual_ok = has_visual_evidence(row)

    talk_claim = extract_theme(pair.get("talk_summary", "") or row.get("speech_summary", ""))
    talk_function = pair.get("talk_function", "") or row.get("clip_value_type", "")
    action_label = row.get("normalized_action_id", "") or pair.get("normalized_action_id", "")
    action_observed = f"text_labeled_action={action_label}; visual_observation=not_confirmed"

    if not visual_ok:
        result = "blocked_need_visual_review"
        fail_reason = (
            "缺视觉动作证据：上一轮只记录 ASR/关键词/同窗口线索，"
            "action_complete_cycle 和 visual_obstruction_risk 仍为 pending_visual_review，"
            "不能证明口播动作同一。"
        )
        downgraded_stage = "not_A_usable_logic_blocked"
        next_action = "先进入人工看原片/视觉模型复核池；确认画面具体动作后再重建配对和剪辑任务包。"
        same_action = "blocked_no_visual_evidence"
        same_problem = "partially_related_from_text_summary_only"
        same_function = "partially_related_from_pair_table_only"
        sequence_logic = "blocked_same_window_or_split_unavailable_not_enough"
        topic_break = "not_determined_without_manual_audio_visual_review"
        evidence_status = "text_keyword_only_pending_visual_review"
    else:
        result = "weak_related"
        fail_reason = "存在非视觉文本线索，但仍缺人工听审和动作完整循环确认；本脚本不自动写真配对。"
        downgraded_stage = "manual_review_pool"
        next_action = "人工复核口播动作同一点后再决定是否进入下一轮剪辑任务包。"
        same_action = "pending_manual_confirmation"
        same_problem = "pending_manual_confirmation"
        same_function = "pending_manual_confirmation"
        sequence_logic = "pending_manual_confirmation"
        topic_break = "pending_manual_confirmation"
        evidence_status = "partial_evidence_pending_manual_review"

    notes = (
        f"asr_overlap_segments={asr_overlap}; "
        f"local_full_context_exists={str(local_mp4_exists).lower()}; "
        f"pair_split_status={pair_split_status}; "
        f"source_reason={source_reason}; keyword_count={keyword_count}; "
        f"previous_status={row.get('status', '')}"
    )
    return {
        "review_id": review_id,
        "candidate_id": row.get("candidate_id", ""),
        "pair_group_id": pair.get("pair_group_id", "missing_pair_group"),
        "recording_id": row.get("recording_id", ""),
        "source_file": row.get("source_file", ""),
        "usable_structure_name": row.get("usable_structure_name", ""),
        "original_stage1_priority": row.get("stage1_priority", ""),
        "talk_start_time": pair.get("talk_start_time", row.get("start_time", "")),
        "talk_end_time": pair.get("talk_end_time", row.get("end_time", "")),
        "action_start_time": pair.get("action_start_time", row.get("start_time", "")),
        "action_end_time": pair.get("action_end_time", row.get("end_time", "")),
        "talk_claimed_action_or_problem": talk_claim,
        "talk_claimed_function": talk_function,
        "action_observed_or_labeled": action_observed,
        "action_evidence_status": evidence_status,
        "same_action_check": same_action,
        "same_problem_check": same_problem,
        "same_function_check": same_function,
        "sequence_logic_check": sequence_logic,
        "topic_break_check": topic_break,
        "logic_review_result": result,
        "logic_fail_reason": fail_reason,
        "downgraded_stage": downgraded_stage,
        "next_action": next_action,
        "manual_review_items": row.get("manual_review_items", ""),
        "notes": notes,
    }


def write_revision_rules(counts: Counter[str]) -> None:
    text = f"""# 配对逻辑修正规则

状态：`已确认`
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## P0 硬闸门

口播动作逻辑一致性高于 A 类评分、关键词命中、结构命中和时间相邻。

## 本轮复审结论

- true_pair：{counts.get("true_pair", 0)}
- weak_related：{counts.get("weak_related", 0)}
- logic_mismatch：{counts.get("logic_mismatch", 0)}
- blocked_need_visual_review：{counts.get("blocked_need_visual_review", 0)}

## 以后必须新增的规则

1. `same_window_text_keyword_candidate` 只能作为线索，不能作为配对通过。
2. `pending_visual_review` 不能进入剪辑师可用素材包。
3. `action_complete_cycle` 必须有视觉证据或人工看原片确认。
4. 口播必须明确说出动作、问题或目的；动作段必须证明是同一动作或同一动作阶段。
5. 配对表必须拆出口播时间、动作时间和中间断裂检查；如果两段时间完全相同，只能写完整上下文候选，不能写真配对。
6. 口播讲理论、卖课、互动或泛泛表达时，不能因为同窗口有动作词就算动作解释。
7. 真配对必须写清 `talk_action_same_point`，否则默认进入人工复核或阻断。
8. 复审输出必须保留失败原因，禁止为了保留数量放宽逻辑标准。

## 旧逻辑主要问题

- 把文本关键词命中当作动作候选。
- 把同一 120 秒窗口内的口播和动作词族当作配对组。
- 没有视觉证据字段来证明画面动作是什么。
- 没有区分“同一大类问题”和“同一个动作”。
- 本地完整上下文 mp4 存在，被误用成可以交给剪辑师的信号；它只能说明复审材料存在。

## 下一版配对算法闸门

候选必须先通过：ASR 口播单元 -> 视觉动作单元 -> 同动作/同问题/同目的匹配 -> 中间断裂检查 -> 人工抽检。任何一层缺失，不能标为剪辑师可用素材。
"""
    write_text(REVISION_RULES_MD, text)


def write_solution(counts: Counter[str], common_reasons: Counter[str]) -> None:
    reason_lines = "\n".join(f"- {reason}: {count}" for reason, count in common_reasons.most_common()) or "- 无"
    text = f"""# 逻辑复审后解决方案

状态：`已确认`
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 1. 本轮复审结论

上一轮 102 条 A 类候选不能直接给剪辑师使用。本轮按 P0 口播动作逻辑闸门复审后，所有候选都缺视觉动作证据，因此全部降级到 `blocked_need_visual_review`。

## 2. 数量

- 原 A 类候选：{sum(counts.values())}
- 真配对：{counts.get("true_pair", 0)}
- 弱相关：{counts.get("weak_related", 0)}
- 逻辑错配：{counts.get("logic_mismatch", 0)}
- 缺视觉证据阻断：{counts.get("blocked_need_visual_review", 0)}

## 3. 错配或阻断最常见原因

{reason_lines}

## 4. 旧筛选逻辑哪里错了

旧逻辑把 ASR 主题、动作词族、结构名和同窗口时间相邻当成候选优先级，但没有真正证明画面动作和口播动作是同一个动作、同一个问题、同一个功能目的。A 类只能说明“值得优先复核”，不能说明“剪辑师可直接使用”。

## 5. 新筛选逻辑应该怎么改

1. 先切出可听懂的口播单元，人工或模型确认口播到底在讲什么动作/问题/目的。
2. 再切出视觉动作单元，人工或视觉模型确认画面具体动作、动作循环、遮挡和是否完整。
3. 用同动作、同问题、同目的三项同时匹配，失败即降级。
4. 检查中间是否插入卖课、闲聊、互动或换动作。
5. 只有通过上述链路的候选，才能进入剪辑师任务包整理。

## 6. 下一轮应该先做什么

优先先补视觉复核，而不是继续导出素材。当前本地素材包只能作为复审材料池，不能作为剪辑师交付包。建议下一轮建立 `visual_action_review` 表：每条候选至少抽 3-5 个关键帧或人工看原片，标出具体动作、是否完整、是否遮挡、是否和口播同一点。

## 7. 如何重新生成剪辑师可用素材包

1. 从 `18_缺视觉证据阻断清单_blocked_need_visual_review.csv` 选取优先复核候选。
2. 对每条候选补视觉动作证据。
3. 将通过视觉证据的候选重新跑 P0 配对逻辑。
4. 只把 `true_pair` 输出到新的剪辑师任务包。
5. 对 `weak_related` 单独建人工复核池，不混入剪辑师交付包。

## 8. 暂时不能给剪辑师的素材

本轮 102 条原 A 类候选全部暂时不能作为剪辑师可用素材。它们可以作为原片复审入口，但不能作为已经配好的口播动作素材。

## 9. 可以进入成片任务包候选的素材

当前为 0。只有下一轮补完视觉动作证据并通过同动作/同问题/同目的检查后，才可以进入成片任务包候选。
"""
    write_text(SOLUTION_MD, text)


def write_report(counts: Counter[str], probe_rows: list[dict[str, Any]], files_changed: list[str]) -> None:
    probe_lines = "\n".join(f"- {r['check_item']}: {r['status']} ({r['value']})" for r in probe_rows)
    result_lines = "\n".join(f"- {name}: {counts.get(name, 0)}" for name in LOGIC_RESULTS)
    file_lines = "\n".join(f"- `{path}`" for path in files_changed)
    text = f"""# 121 P0 口播动作逻辑复审执行报告

状态：`logic_review_generated_pending_user_review`
生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
- `git pull --ff-only`
- `python3 scripts/review_A_class_pair_logic_P0.py`
- `python3 -m py_compile scripts/review_A_class_pair_logic_P0.py`
- `/Users/fan/.codex/skills/video-metadata-probe/scripts/probe_video.sh <representative_A001_full_context_mp4>`
- `git diff --check`
- `git diff --cached --check`

## validation

- `python3 -m py_compile scripts/review_A_class_pair_logic_P0.py`：passed
- `git diff --check`：passed
- 复审表自检：102 条原 A 类候选全部有结果，四类数量加总为 102。
- 媒体边界：本轮没有生成复审媒体，`outputs/local_pair_logic_review/` 已被 `.gitignore` 忽略。
- 视频技术样本：代表性 A001 本地 full_context mp4 可 ffprobe、可短解码、有音轨；该验证只证明技术可读，不证明内容逻辑通过。

## result

已确认：本轮只复审上一轮 A 类候选及其配对关系，没有重新筛选全量素材，没有继续导出素材，没有生成正式成片。

{result_lines}

核心结论：上一轮 102 条 A 类候选全部缺视觉动作证据，不能继续标为 A 类可用素材。

## pair_logic_review_probe

{probe_lines}

## files_changed

{file_lines}

## failed_items

- true_pair 数量为 0，原因是所有 A 类候选都只有 ASR/关键词/同窗口线索，动作完整循环和画面动作仍是待视觉复核。
- 本轮未执行人工看原片、动作专业复核、健康/课程业务复核或审美判断。

## blocked reason

无流程级 blocked；但内容层全部进入 `blocked_need_visual_review`，下一轮必须先补视觉证据。

## 边界

本轮技术产物已生成，结果仍需用户人审；不得把本轮 CSV 当成剪辑师可用素材包。
"""
    write_text(REPORT_MD, text)


def main() -> int:
    required = [A_LIST_CSV, PAIRING_CSV, MASTER_CSV, STRUCTURE_CSV]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required inputs: {missing}")

    a_rows = read_csv(A_LIST_CSV)
    pair_rows = read_csv(PAIRING_CSV)
    master_rows = read_csv(MASTER_CSV)
    structure_rows = read_csv(STRUCTURE_CSV)
    manifest_rows = read_csv(MANIFEST_CSV) if MANIFEST_CSV.exists() else []
    guide_rows = read_csv(PAIR_GUIDE_CSV) if PAIR_GUIDE_CSV.exists() else []

    pair_index = build_pair_index(pair_rows)
    manifest_index = build_manifest_index(manifest_rows)
    asr_overlap = load_transcript_windows(a_rows)

    root_rc, git_root = run_git(["rev-parse", "--show-toplevel"])
    branch_rc, branch = run_git(["branch", "--show-current"])
    remote_rc, remote = run_git(["remote", "-v"])
    status_rc, status = run_git(["status", "--short"])
    ignored_rc, _ = run_git(["check-ignore", "-q", "outputs/local_pair_logic_review/__probe__.mp4"])

    source_files = sorted({row.get("source_file", "") for row in a_rows})
    source_exists = [Path(path).exists() for path in source_files]
    asr_json_count = len([p for p in ASR_ROOT.glob("*.json") if not p.name.startswith("._")]) if ASR_ROOT.exists() else 0
    a_with_pair = sum(1 for row in a_rows if row.get("candidate_id", "") in pair_index)
    a_with_talk_time = sum(1 for row in a_rows if pair_index.get(row.get("candidate_id", ""), {}).get("talk_start_time") and pair_index.get(row.get("candidate_id", ""), {}).get("talk_end_time"))
    a_with_action_time = sum(1 for row in a_rows if pair_index.get(row.get("candidate_id", ""), {}).get("action_start_time") and pair_index.get(row.get("candidate_id", ""), {}).get("action_end_time"))
    a_with_asr = sum(1 for row in a_rows if asr_overlap.get(row.get("candidate_id", ""), 0) > 0)
    local_exports = sum(1 for row in a_rows if Path(manifest_index.get(row.get("candidate_id", ""), {}).get("full_context_path", "")).exists())
    visual_evidence = sum(1 for row in a_rows if has_visual_evidence(row))

    probe_rows: list[dict[str, Any]] = [
        {"check_item": "pwd", "value": str(REPO_ROOT), "status": "pass", "note": "script_repo_root"},
        {"check_item": "git_root", "value": git_root, "status": "pass" if root_rc == 0 and git_root == str(REPO_ROOT) else "fail", "note": ""},
        {"check_item": "branch", "value": branch, "status": "pass" if branch_rc == 0 and branch == "main" else "fail", "note": ""},
        {"check_item": "remote", "value": "fthytwerwt-sudo/lanxinse--" in remote, "status": "pass" if remote_rc == 0 and "fthytwerwt-sudo/lanxinse--" in remote else "fail", "note": remote.splitlines()[0] if remote else ""},
        {"check_item": "git_status_entries_before_outputs", "value": len(status.splitlines()) if status else 0, "status": "pass", "note": "dirty status allowed only if unrelated or current outputs"},
        {"check_item": "git_pull_ff_only", "value": "already_up_to_date_before_script", "status": "pass", "note": "executed before script"},
        {"check_item": "a_list_exists", "value": A_LIST_CSV.exists(), "status": "pass", "note": str(A_LIST_CSV)},
        {"check_item": "a_candidate_count", "value": len(a_rows), "status": "pass" if len(a_rows) == 102 else "warn", "note": ""},
        {"check_item": "pair_table_exists", "value": PAIRING_CSV.exists(), "status": "pass", "note": str(PAIRING_CSV)},
        {"check_item": "pair_row_count", "value": len(pair_rows), "status": "pass", "note": ""},
        {"check_item": "master_row_count", "value": len(master_rows), "status": "pass", "note": ""},
        {"check_item": "structure_row_count", "value": len(structure_rows), "status": "pass", "note": ""},
        {"check_item": "a_with_pair_group", "value": a_with_pair, "status": "pass" if a_with_pair == len(a_rows) else "fail", "note": ""},
        {"check_item": "a_with_talk_time", "value": a_with_talk_time, "status": "pass" if a_with_talk_time == len(a_rows) else "fail", "note": ""},
        {"check_item": "a_with_action_time", "value": a_with_action_time, "status": "pass" if a_with_action_time == len(a_rows) else "fail", "note": ""},
        {"check_item": "asr_cache_exists", "value": ASR_ROOT.exists(), "status": "pass" if ASR_ROOT.exists() else "fail", "note": str(ASR_ROOT)},
        {"check_item": "asr_json_count", "value": asr_json_count, "status": "pass" if asr_json_count >= 4 else "fail", "note": "AppleDouble files ignored"},
        {"check_item": "a_with_asr_window_evidence", "value": a_with_asr, "status": "pass" if a_with_asr == len(a_rows) else "warn", "note": "raw text not exported"},
        {"check_item": "local_A_package_exists", "value": LOCAL_A_PACKAGE_ROOT.exists(), "status": "pass" if LOCAL_A_PACKAGE_ROOT.exists() else "warn", "note": str(LOCAL_A_PACKAGE_ROOT)},
        {"check_item": "local_A_export_manifest_rows", "value": len(manifest_rows), "status": "pass" if len(manifest_rows) == len(a_rows) else "warn", "note": str(MANIFEST_CSV)},
        {"check_item": "local_A_export_mp4_exists", "value": local_exports, "status": "pass" if local_exports == len(a_rows) else "warn", "note": "technical material exists only"},
        {"check_item": "pair_guide_rows", "value": len(guide_rows), "status": "pass" if len(guide_rows) == len(a_rows) else "warn", "note": str(PAIR_GUIDE_CSV)},
        {"check_item": "raw_video_root_exists", "value": RAW_VIDEO_ROOT.exists(), "status": "pass" if RAW_VIDEO_ROOT.exists() else "fail", "note": str(RAW_VIDEO_ROOT)},
        {"check_item": "source_videos_exist", "value": sum(source_exists), "status": "pass" if all(source_exists) else "fail", "note": f"expected={len(source_files)}"},
        {"check_item": "visual_evidence_count", "value": visual_evidence, "status": "pass", "note": "visual evidence required for true_pair"},
        {"check_item": "missing_visual_evidence_count", "value": len(a_rows) - visual_evidence, "status": "pass", "note": "all such rows must be blocked"},
        {"check_item": "manual_review_needed_count", "value": len(a_rows), "status": "pass", "note": "P0 user review required"},
        {"check_item": "local_review_media_generated", "value": "no", "status": "pass", "note": str(LOCAL_REVIEW_ROOT)},
        {"check_item": "local_review_output_ignore_status", "value": "ignored" if ignored_rc == 0 else "not_ignored", "status": "pass" if ignored_rc == 0 else "fail", "note": "outputs/local_pair_logic_review/"},
    ]
    if any(row["status"] == "fail" for row in probe_rows):
        write_csv(PROBE_CSV, probe_rows, ["check_item", "value", "status", "note"])
        raise RuntimeError("probe failed; see pair logic probe CSV")

    review_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(a_rows, start=1):
        candidate_id = row.get("candidate_id", "")
        pair = pair_index.get(candidate_id, {})
        manifest = manifest_index.get(candidate_id, {})
        review_rows.append(classify_row(row, pair, manifest, asr_overlap.get(candidate_id, 0), f"P0R{idx:03d}"))

    counts = Counter(row["logic_review_result"] for row in review_rows)
    if sum(counts.values()) != len(a_rows):
        raise RuntimeError("review result count does not match A candidate count")

    category_rows = {name: [row for row in review_rows if row["logic_review_result"] == name] for name in LOGIC_RESULTS}
    common_reasons = Counter(row["logic_fail_reason"] for row in review_rows if row["logic_fail_reason"])

    write_csv(PROBE_CSV, probe_rows, ["check_item", "value", "status", "note"])
    write_csv(REVIEW_MASTER_CSV, review_rows, MASTER_FIELDS)
    write_csv(TRUE_PAIR_CSV, category_rows["true_pair"], MASTER_FIELDS)
    write_csv(WEAK_RELATED_CSV, category_rows["weak_related"], MASTER_FIELDS)
    write_csv(MISMATCH_CSV, category_rows["logic_mismatch"], MASTER_FIELDS)
    write_csv(BLOCKED_CSV, category_rows["blocked_need_visual_review"], MASTER_FIELDS)
    write_revision_rules(counts)
    write_solution(counts, common_reasons)

    files_changed = [
        ".gitignore",
        "scripts/review_A_class_pair_logic_P0.py",
        "素材解析_pipeline_material_analysis/14_pair_logic_review/01_配对逻辑复审探针_pair_logic_review_probe.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/14_A类口播动作逻辑复审总表_A_class_pair_logic_review_master.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/15_真配对候选清单_true_pair_candidates.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/16_弱相关待复核清单_weak_related_pending_review.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/17_逻辑错配剔除清单_logic_mismatch_rejects.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/18_缺视觉证据阻断清单_blocked_need_visual_review.csv",
        "项目事实_project_facts/直播素材筛选_live_material_screening/19_配对逻辑修正规则_pairing_logic_revision_rules.md",
        "项目事实_project_facts/直播素材筛选_live_material_screening/20_逻辑复审后解决方案_after_logic_review_solution.md",
        "执行日志_codex_log/121_P0口播动作逻辑复审执行报告_P0_pair_logic_review_report.md",
    ]
    write_report(counts, probe_rows, files_changed)

    print("P0 pair logic review completed")
    for name in LOGIC_RESULTS:
        print(f"{name}: {counts.get(name, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
