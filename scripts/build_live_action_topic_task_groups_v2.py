#!/usr/bin/env python3
"""按视觉动作主题构建 5 月 13 日直播的完整口播动作任务组。"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Volumes/WD_BLACK/完整直播录屏/今年直播素材/5月13日直播素材.MP4")
DEFAULT_ASR = REPO_ROOT / "api_outputs/full_live_material_screening/asr_transcripts/rec_001_5月13日直播素材.json"
DEFAULT_VISUAL = REPO_ROOT / "素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/03_视觉动作单元表_visual_action_units.csv"
DEFAULT_OUTPUT = REPO_ROOT / "outputs/local_513_action_topic_task_groups_v2"

MASTER_CSV = REPO_ROOT / "项目事实_project_facts/直播素材重筛_live_rescreen/08_5月13日动作主题任务组总表_513_action_topic_task_group_master.csv"
MANIFEST_CSV = REPO_ROOT / "项目事实_project_facts/直播素材重筛_live_rescreen/09_5月13日视频任务包索引V2_513_video_task_package_manifest_v2.csv"
REVIEW_CSV = REPO_ROOT / "项目事实_project_facts/直播素材重筛_live_rescreen/11_5月13日代表样本用户复核表_513_representative_user_review.csv"

GENERIC_QUESTION_VALUES = {
    "",
    "动作相关问题",
    "胸部/乳房状态",
    "动作/练习口播",
    "动作/练习问题",
}
QUESTION_MARKERS = ("吗", "嗎", "呢", "为什么", "為什麼", "怎么", "怎麼", "要不要", "能不能", "可不可以", "是否", "有没有", "有沒有")
REPRESENTATIVE_VISUAL_IDS = ("VA005", "VA007", "VA009")


@dataclass(frozen=True)
class EvidenceSpec:
    role: str
    start_anchors: tuple[str, ...]
    end_anchors: tuple[str, ...]
    filename: str
    shared_with: str = ""


@dataclass(frozen=True)
class TopicSpec:
    visual_action_unit_id: str
    normalized_action_name: str
    speech_action_name: str
    speech_body_part: str
    topic_terms: tuple[str, ...]
    evidence_specs: tuple[EvidenceSpec, ...]
    expected_topic_break: str = "no"


TOPIC_SPECS = {
    "VA005": TopicSpec(
        visual_action_unit_id="VA005",
        normalized_action_name="劳宫穴对准乳头的吸管式呼吸连接",
        speech_action_name="劳宫穴对准乳头并配合吸管式呼吸",
        speech_body_part="胸部/乳头",
        topic_terms=("劳工穴", "劳宫穴", "乳头", "吸管"),
        evidence_specs=(
            EvidenceSpec("purpose", ("呼吸特别短的人",), ("慢慢的来去做练习的", "慢慢的來去做練習的"), "01_动作用途_purpose.mp4"),
            EvidenceSpec("problem", ("呼吸特别短的人",), ("所以呼吸就会比较浅",), "", "purpose"),
            EvidenceSpec("reason_or_boundary", ("就是因为我们的",), ("慢慢的来去做练习的", "慢慢的來去做練習的"), "", "purpose"),
            EvidenceSpec("method", ("接下来我们要将我们的手的劳工穴",), ("向下呼",), "04_操作方法_method.mp4"),
            EvidenceSpec("action_instruction", ("当我们在吸气的时候呢",), ("向下呼",), "", "method"),
        ),
    ),
    "VA007": TopicSpec(
        visual_action_unit_id="VA007",
        normalized_action_name="单侧托揉乳房配合吸管式呼吸",
        speech_action_name="单侧托揉乳房并配合呼吸",
        speech_body_part="胸部/乳房",
        topic_terms=("拖住乳房", "揉", "面团", "单侧"),
        evidence_specs=(
            EvidenceSpec("purpose", ("把里面的委屈",), ("让它消失",), "01_动作用途_purpose.mp4"),
            EvidenceSpec("question", ("可以往上吸嗎", "可以往上吸吗"), ("吸的是可以的",), "02_对应问题与解答_problem_answer.mp4"),
            EvidenceSpec("answer", ("我們只是做乳房療癒", "我们只是做乳房疗愈"), ("吸的是可以的",), "", "question"),
            EvidenceSpec("method", ("接下来我们要做单侧的",), ("就把呼吸帶到這個過程當中", "就把呼吸带到这个过程当中"), "04_操作方法_method.mp4"),
            EvidenceSpec("reason_or_boundary", ("我們在家裡做最好是不穿衣服", "我们在家里做最好是不穿衣服"), ("主要是感受你的手心的溫暖", "主要是感受你的手心的温暖"), "03_原因或方法边界_reason_boundary.mp4"),
            EvidenceSpec("action_instruction", ("手拖住它拖住乳房来吸气",), ("落下",), "", "action_execution"),
        ),
    ),
    "VA009": TopicSpec(
        visual_action_unit_id="VA009",
        normalized_action_name="云门中府大包等胸部穴位点按",
        speech_action_name="胸部穴位点按",
        speech_body_part="胸部/锁骨窝/腋下",
        topic_terms=("点穴", "云门", "中腹", "大宝穴", "大包穴"),
        evidence_specs=(
            EvidenceSpec("purpose", ("让那个情绪从你的血味",), ("好像就散掉了一样",), "01_动作用途_purpose.mp4"),
            EvidenceSpec("method", ("接下来我们要来去进行我们的点穴",), ("都可以轻轻的按压住它",), "04_操作方法_method.mp4"),
            EvidenceSpec("action_instruction", ("接下来我们点按我们的云门血和中腹血",), ("最後一次吸氣 呼氣", "最后一次吸气 呼气"), "", "action_execution"),
        ),
    ),
}


# CSV 字段用于把视觉主题、原始口播证据、冲突闸门和本地任务包放在同一行追溯。
MASTER_FIELDS = [
    "action_topic_id", "source_id", "source_file", "visual_action_unit_id", "legacy_candidate_id",
    "normalized_action_name", "visual_action_name", "visual_body_part", "speech_action_name", "speech_body_part",
    "action_start_time", "action_end_time", "action_cycle_status", "visual_evidence_status",
    "purpose_evidence", "problem_evidence", "question_text", "question_start_time", "answer_text", "answer_start_time",
    "reason_or_boundary_evidence", "method_evidence", "action_instruction_evidence",
    "body_part_match", "action_name_match", "problem_evidence_present", "purpose_evidence_present", "topic_break_present",
    "structure_type", "task_group_status", "deterministic_reason", "local_task_folder", "content_status", "notes",
]

MANIFEST_FIELDS = [
    "action_topic_id", "task_group_status", "task_folder", "task_card_path", "purpose_path", "problem_answer_path",
    "reason_boundary_path", "method_path", "action_execution_path", "full_logic_chain_path", "contact_sheet_path",
    "shared_source_segment", "missing_segments", "technical_probe_status", "content_status", "notes",
]


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def timecode_to_seconds(value: str) -> float:
    hours, minutes, seconds = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def seconds_to_timecode(value: float) -> str:
    total_ms = int(round(max(0.0, value) * 1000))
    milliseconds = total_ms % 1000
    total_seconds = total_ms // 1000
    seconds = total_seconds % 60
    minutes = (total_seconds // 60) % 60
    hours = total_seconds // 3600
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def is_explicit_question(text: str) -> bool:
    cleaned = re.sub(r"\s+", "", str(text or ""))
    if cleaned in GENERIC_QUESTION_VALUES or len(cleaned) < 4:
        return False
    return any(marker in cleaned for marker in QUESTION_MARKERS)


def find_topic_segments(segments: list[dict[str, Any]], topic_terms: list[str] | tuple[str, ...]) -> list[dict[str, Any]]:
    """扫描完整 ASR；时间距离不参与删除，命中同主题词的片段全部保留。"""
    return [segment for segment in segments if any(term in str(segment.get("text", "")) for term in topic_terms)]


def assign_action_topic_ids(visual_rows: list[dict[str, str]], source_id: str) -> list[dict[str, str]]:
    ordered = sorted(visual_rows, key=lambda row: (timecode_to_seconds(row["action_start_time"]), row["visual_action_unit_id"]))
    return [{**row, "action_topic_id": f"AT{source_id}_{index:03d}"} for index, row in enumerate(ordered, start=1)]


def body_tokens(value: str) -> set[str]:
    aliases = {
        "胸部": ("胸", "乳房", "乳头", "乳頭", "乳腺"),
        "锁骨窝": ("锁骨", "鎖骨"),
        "腋下": ("腋下", "夜下", "腋窝", "夜窩"),
        "腹部": ("腹部", "肚子"),
        "肩部": ("肩",),
        "盆底": ("盆底", "会阴", "會陰", "阴道", "音道"),
    }
    return {name for name, terms in aliases.items() if any(term in value for term in terms)}


def action_family(value: str) -> str:
    if any(term in value for term in ("穴", "点按", "點按", "云门", "中府", "大包")):
        return "acupoint_press"
    if any(term in value for term in ("揉", "托", "捧")):
        return "knead_support"
    if any(term in value for term in ("劳宫", "勞宮", "劳工", "乳头", "乳頭")):
        return "palm_nipple_breath"
    if "呼吸" in value:
        return "breathing"
    return "unknown"


def compose_visual_action_evidence(row: dict[str, str]) -> str:
    """合并同一视觉单元的动作描述和身体/工具字段，避免丢掉穴位等动作特征。"""
    return "；".join(
        value for value in (row.get("observed_action_name", ""), row.get("observed_body_part_or_tool", "")) if value
    )


def deterministic_conflict_check(
    speech_body_part: str,
    visual_body_part: str,
    speech_action_name: str,
    visual_action_name: str,
    topic_break_present: str,
) -> dict[str, str]:
    speech_parts = body_tokens(speech_body_part)
    visual_parts = body_tokens(visual_body_part)
    body_match = "yes" if speech_parts and visual_parts and speech_parts.intersection(visual_parts) else "no"
    speech_family = action_family(speech_action_name)
    visual_family = action_family(visual_action_name)
    action_match = "yes" if speech_family != "unknown" and speech_family == visual_family else "no"
    forced = "logic_mismatch" if "no" in (body_match, action_match) or topic_break_present == "yes" else ""
    return {"body_part_match": body_match, "action_name_match": action_match, "forced_status": forced}


def derive_task_group_status(
    forced_status: str,
    purpose_present: bool,
    method_present: bool,
    visual_clear: bool,
    action_cycle_status: str,
    explicit_question: bool,
) -> tuple[str, str]:
    if forced_status:
        return forced_status, "deterministic_veto:body_part_or_action_name_conflict"
    if not purpose_present or not method_present or not visual_clear:
        return "partial_action_task_group", "required_chain_component_missing"
    if action_cycle_status == "no":
        return "partial_action_task_group", "visual_action_cycle_incomplete"
    if action_cycle_status != "yes":
        return "manual_review", "visual_action_cycle_unclear"
    if explicit_question:
        return "true_pair_pending_user_review", "explicit_question_answer_and_complete_action_chain_present"
    return "action_teaching_group_pending_user_review", "teaching_chain_present_without_fabricated_question"


def find_anchor_index(segments: list[dict[str, Any]], anchors: tuple[str, ...], start_at: int = 0) -> int | None:
    for index in range(start_at, len(segments)):
        text = str(segments[index].get("text", ""))
        if any(anchor in text for anchor in anchors):
            return index
    return None


def build_evidence(
    segments: list[dict[str, Any]],
    spec: EvidenceSpec,
    reference_seconds: float,
) -> dict[str, Any] | None:
    candidates: list[tuple[float, int, int]] = []
    for start_index, segment in enumerate(segments):
        text = str(segment.get("text", ""))
        if not any(anchor in text for anchor in spec.start_anchors):
            continue
        end_index = find_anchor_index(segments, spec.end_anchors, start_index)
        if end_index is None:
            continue
        start_seconds = float(segments[start_index]["start_seconds"])
        end_seconds = float(segments[end_index]["end_seconds"])
        if end_seconds - start_seconds > 300:
            continue
        candidates.append((abs(start_seconds - reference_seconds), start_index, end_index))
    if not candidates:
        return None
    _, start_index, end_index = min(candidates, key=lambda item: (item[0], item[1]))
    selected = segments[start_index : end_index + 1]
    return {
        "role": spec.role,
        "start_seconds": float(selected[0]["start_seconds"]),
        "end_seconds": float(selected[-1]["end_seconds"]),
        "start_time": selected[0].get("start_time") or seconds_to_timecode(float(selected[0]["start_seconds"])),
        "end_time": selected[-1].get("end_time") or seconds_to_timecode(float(selected[-1]["end_seconds"])),
        "text": " ".join(str(row.get("text", "")).strip() for row in selected if str(row.get("text", "")).strip()),
        "filename": spec.filename,
        "shared_with": spec.shared_with,
    }


def export_clip(source: Path, start: float, end: float, output: Path) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    if probe_video(output) == "passed":
        return "reused_existing_verified"
    duration = max(0.2, end - start)
    hardware_cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}", "-i", str(source),
        "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "h264_videotoolbox",
        "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-allow_sw", "1",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output),
    ]
    proc = run(hardware_cmd, timeout=1200)
    if proc.returncode == 0 and output.exists() and output.stat().st_size > 0:
        return "h264_videotoolbox_8m_aac"
    encode_cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}", "-i", str(source),
        "-t", f"{duration:.3f}", "-map", "0:v:0", "-map", "0:a:0?", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "22", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(output),
    ]
    fallback = run(encode_cmd, timeout=1800)
    if fallback.returncode != 0 or not output.exists() or output.stat().st_size == 0:
        raise RuntimeError(f"clip_export_failed:{output.name}:{fallback.stderr[-500:]}")
    return "h264_aac_fallback"


def probe_video(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "failed_missing"
    proc = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-show_streams", "-of", "json", str(path)], timeout=120)
    if proc.returncode != 0:
        return "failed_ffprobe"
    data = json.loads(proc.stdout)
    streams = data.get("streams", [])
    has_video = any(stream.get("codec_type") == "video" for stream in streams)
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    return "passed" if has_video and has_audio else "failed_missing_stream"


def evidence_summary(evidence: dict[str, Any] | None) -> str:
    if not evidence:
        return ""
    return f"{evidence['start_time']}--{evidence['end_time']} | {evidence['text']}"


def create_contact_sheet(source_sheet: str, folder: Path) -> str:
    source = Path(source_sheet)
    if not source.exists():
        return ""
    destination = folder / "07_视觉证据_contact_sheet.jpg"
    shutil.copy2(source, destination)
    return str(destination)


def build_topic(
    topic_row: dict[str, str],
    spec: TopicSpec,
    segments: list[dict[str, Any]],
    source: Path,
    output_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    action_topic_id = topic_row["action_topic_id"]
    folder = output_root / f"{action_topic_id}_{spec.normalized_action_name}"
    folder.mkdir(parents=True, exist_ok=True)
    action_start = timecode_to_seconds(topic_row["action_start_time"])
    evidence = {
        evidence_spec.role: build_evidence(segments, evidence_spec, reference_seconds=action_start)
        for evidence_spec in spec.evidence_specs
    }
    topic_hits = find_topic_segments(segments, spec.topic_terms)

    checks = deterministic_conflict_check(
        speech_body_part=spec.speech_body_part,
        visual_body_part=topic_row.get("observed_body_part_or_tool", ""),
        speech_action_name=spec.speech_action_name,
        visual_action_name=compose_visual_action_evidence(topic_row),
        topic_break_present=spec.expected_topic_break,
    )
    question = evidence.get("question")
    answer = evidence.get("answer")
    explicit_question = bool(question and answer and is_explicit_question(question["text"]))
    purpose_present = bool(evidence.get("purpose"))
    method_present = bool(evidence.get("method"))
    visual_clear = topic_row.get("visual_api_status") == "success" and topic_row.get("presenter_visible") == "yes"

    status, reason = derive_task_group_status(
        forced_status=checks["forced_status"],
        purpose_present=purpose_present,
        method_present=method_present,
        visual_clear=visual_clear,
        action_cycle_status=topic_row.get("action_cycle_complete", "unclear"),
        explicit_question=explicit_question,
    )

    role_paths: dict[str, str] = {}
    shared_roles: list[str] = []
    export_methods: list[str] = []
    for role, item in evidence.items():
        if not item:
            continue
        if item["shared_with"]:
            shared_roles.append(f"{role}->{item['shared_with']}")
            continue
        if not item["filename"]:
            continue
        path = folder / item["filename"]
        export_methods.append(f"{role}:{export_clip(source, item['start_seconds'], item['end_seconds'], path)}")
        role_paths[role] = str(path)

    action_end = timecode_to_seconds(topic_row["action_end_time"])
    action_path = folder / "05_动作执行_action_execution.mp4"
    export_methods.append(f"action_execution:{export_clip(source, action_start, action_end, action_path)}")
    role_paths["action_execution"] = str(action_path)

    evidence_starts = [item["start_seconds"] for item in evidence.values() if item]
    evidence_ends = [item["end_seconds"] for item in evidence.values() if item]
    full_start = min(evidence_starts + [action_start])
    full_end = max(evidence_ends + [action_end])
    full_path = folder / "06_完整逻辑链_full_logic_chain.mp4"
    export_methods.append(f"full_logic_chain:{export_clip(source, full_start, full_end, full_path)}")
    contact_sheet_path = create_contact_sheet(topic_row.get("contact_sheet_path_local", ""), folder)

    missing = []
    if not purpose_present:
        missing.append("purpose")
    if not explicit_question:
        missing.append("explicit_question_answer")
    if not evidence.get("reason_or_boundary"):
        missing.append("reason_or_boundary")
    if not method_present:
        missing.append("method")

    card = f"""# {action_topic_id} 剪辑任务卡

状态：`{status}`
生成时间：{now_text()}

## 动作主题

- 归一动作：{spec.normalized_action_name}
- 视觉动作：{topic_row.get('observed_action_name', '')}
- 口播身体部位：{spec.speech_body_part}
- 视觉身体部位：{topic_row.get('observed_body_part_or_tool', '')}
- 旧候选：{topic_row.get('candidate_id', '')}

## 完整链证据

- 为什么做：{evidence_summary(evidence.get('purpose')) or 'missing'}
- 解决什么问题：{evidence_summary(evidence.get('problem')) or 'missing'}
- 明确问题：{evidence_summary(question) or 'missing；不得伪造问题问答'}
- 对应回答：{evidence_summary(answer) or 'missing'}
- 原因或边界：{evidence_summary(evidence.get('reason_or_boundary')) or 'missing'}
- 怎么做：{evidence_summary(evidence.get('method')) or 'missing'}
- 实际动作：{topic_row['action_start_time']}--{topic_row['action_end_time']}

## 确定性闸门

- body_part_match: `{checks['body_part_match']}`
- action_name_match: `{checks['action_name_match']}`
- topic_break_present: `{spec.expected_topic_break}`
- 结论原因：{reason}

本卡仅为剪辑候选证据，不代表动作专业性、健康效果、审美、业务或发布通过。
"""
    task_card = folder / "00_剪辑任务卡.md"
    write_text(task_card, card)

    all_video_paths = [Path(path) for path in role_paths.values()] + [full_path]
    technical = "passed" if all(probe_video(path) == "passed" for path in all_video_paths) else "failed"
    question_text = question["text"] if explicit_question else ""
    answer_text = answer["text"] if explicit_question else ""
    master = {
        "action_topic_id": action_topic_id,
        "source_id": "513",
        "source_file": str(source),
        "visual_action_unit_id": topic_row["visual_action_unit_id"],
        "legacy_candidate_id": topic_row.get("candidate_id", ""),
        "normalized_action_name": spec.normalized_action_name,
        "visual_action_name": topic_row.get("observed_action_name", ""),
        "visual_body_part": topic_row.get("observed_body_part_or_tool", ""),
        "speech_action_name": spec.speech_action_name,
        "speech_body_part": spec.speech_body_part,
        "action_start_time": topic_row["action_start_time"],
        "action_end_time": topic_row["action_end_time"],
        "action_cycle_status": topic_row.get("action_cycle_complete", ""),
        "visual_evidence_status": topic_row.get("visual_api_status", ""),
        "purpose_evidence": evidence_summary(evidence.get("purpose")),
        "problem_evidence": evidence_summary(evidence.get("problem")),
        "question_text": question_text,
        "question_start_time": question["start_time"] if explicit_question else "",
        "answer_text": answer_text,
        "answer_start_time": answer["start_time"] if explicit_question else "",
        "reason_or_boundary_evidence": evidence_summary(evidence.get("reason_or_boundary")),
        "method_evidence": evidence_summary(evidence.get("method")),
        "action_instruction_evidence": evidence_summary(evidence.get("action_instruction")),
        "body_part_match": checks["body_part_match"],
        "action_name_match": checks["action_name_match"],
        "problem_evidence_present": "yes" if evidence.get("problem") or explicit_question else "no",
        "purpose_evidence_present": "yes" if purpose_present else "no",
        "topic_break_present": spec.expected_topic_break,
        "structure_type": "question_answer_structure" if explicit_question else "action_teaching_structure",
        "task_group_status": status,
        "deterministic_reason": reason,
        "local_task_folder": str(folder),
        "content_status": "pending_user_review",
        "notes": f"full_asr_topic_hits={len(topic_hits)}; old_102_input=no; api_called=no",
    }
    manifest = {
        "action_topic_id": action_topic_id,
        "task_group_status": status,
        "task_folder": str(folder),
        "task_card_path": str(task_card),
        "purpose_path": role_paths.get("purpose", ""),
        "problem_answer_path": role_paths.get("question", ""),
        "reason_boundary_path": role_paths.get("reason_or_boundary", ""),
        "method_path": role_paths.get("method", ""),
        "action_execution_path": str(action_path),
        "full_logic_chain_path": str(full_path),
        "contact_sheet_path": contact_sheet_path,
        "shared_source_segment": ";".join(shared_roles),
        "missing_segments": ";".join(missing),
        "technical_probe_status": technical,
        "content_status": "pending_user_review",
        "notes": ";".join(export_methods) + "; ignored_not_committed",
    }
    return master, manifest


def ensure_inputs(source: Path, asr_path: Path, visual_path: Path, output_root: Path, reuse_existing_output: bool) -> None:
    for path in (source, asr_path, visual_path):
        if not path.is_file():
            raise RuntimeError(f"blocked_missing_input:{path}")
    if output_root.exists() and any(output_root.iterdir()) and not reuse_existing_output:
        raise RuntimeError(f"blocked_output_collision:{output_root}")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("blocked_ffmpeg_or_ffprobe_unavailable")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-video", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--asr-json", type=Path, default=DEFAULT_ASR)
    parser.add_argument("--visual-units-csv", type=Path, default=DEFAULT_VISUAL)
    parser.add_argument("--source-id", default="513")
    parser.add_argument("--max-action-topics", type=int, default=3)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reuse-existing-output", action="store_true", help="复用已经通过 ffprobe 的本地媒体，只重建索引和任务卡。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source_video.resolve()
    asr_path = args.asr_json.resolve()
    visual_path = args.visual_units_csv.resolve()
    output_root = args.output_root.resolve()
    ensure_inputs(source, asr_path, visual_path, output_root, args.reuse_existing_output)
    if args.source_id != "513":
        raise RuntimeError("blocked_only_source_513_allowed")
    if not 2 <= args.max_action_topics <= 5:
        raise RuntimeError("blocked_max_action_topics_must_be_2_to_5")

    asr_data = json.loads(asr_path.read_text(encoding="utf-8"))
    segments = asr_data.get("segments", [])
    visual_rows = read_csv(visual_path)
    selected_rows = [row for row in visual_rows if row.get("visual_action_unit_id") in REPRESENTATIVE_VISUAL_IDS]
    selected_rows = assign_action_topic_ids(selected_rows, args.source_id)[: args.max_action_topics]
    output_root.mkdir(parents=True, exist_ok=args.reuse_existing_output)

    master_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    for row in selected_rows:
        spec = TOPIC_SPECS[row["visual_action_unit_id"]]
        master, manifest = build_topic(row, spec, segments, source, output_root)
        master_rows.append(master)
        manifest_rows.append(manifest)
        print(f"built={master['action_topic_id']} status={master['task_group_status']}", flush=True)

    write_csv(MASTER_CSV, master_rows, MASTER_FIELDS)
    write_csv(MANIFEST_CSV, manifest_rows, MANIFEST_FIELDS)
    review_rows = [
        {
            "action_topic_id": row["action_topic_id"],
            "normalized_action_name": row["normalized_action_name"],
            "task_group_status": row["task_group_status"],
            "local_task_folder": row["local_task_folder"],
            "user_review_status": "pending_user_review",
            "逻辑链是否连贯": "",
            "问题与回答是否对应": "",
            "口播与动作是否同题": "",
            "用户备注": "",
        }
        for row in master_rows
    ]
    write_csv(
        REVIEW_CSV,
        review_rows,
        ["action_topic_id", "normalized_action_name", "task_group_status", "local_task_folder", "user_review_status", "逻辑链是否连贯", "问题与回答是否对应", "口播与动作是否同题", "用户备注"],
    )
    print(f"action_topics={len(master_rows)}")
    print(f"output_root={output_root}")
    print("api_called=no")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
