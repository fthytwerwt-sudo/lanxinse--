#!/usr/bin/env python3
"""Batch local timecoded transcription for Lanxin sample videos.

This script writes full transcript JSON/TXT files to an ignored local folder and
keeps only a status CSV suitable for Git. It does not analyze content or make
editing decisions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from faster_whisper import WhisperModel


STATUS_FIELDS = [
    "pair_id",
    "source_id",
    "video_file_name",
    "video_path",
    "transcript_json_path",
    "transcript_txt_path",
    "status",
    "segment_count",
    "duration_seconds",
    "language",
    "model_used",
    "compute_type",
    "error_message",
    "needs_manual_review",
]


@dataclass
class VideoItem:
    pair_id: str
    source_id: str
    video_file_name: str
    video_path: Path
    detected_topic: str = ""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def safe_slug(name: str, max_len: int = 48) -> str:
    stem = Path(name).stem
    stem = re.sub(r"^\._", "", stem)
    stem = re.sub(r"[\\/:*?\"<>|\s]+", "_", stem).strip("._")
    if not stem:
        stem = "video"
    return stem[:max_len]


def output_stem(item: VideoItem) -> str:
    digest = hashlib.sha1(str(item.video_path).encode("utf-8")).hexdigest()[:8]
    return f"{item.source_id}_{item.pair_id}_{safe_slug(item.video_file_name)}_{digest}"


def run_command(args: List[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )


def ffprobe_duration(video_path: Path) -> float:
    proc = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        timeout=60,
    )
    if proc.returncode != 0:
        return 0.0
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return 0.0


def extract_audio(video_path: Path, audio_path: Path, force: bool) -> None:
    if audio_path.exists() and audio_path.stat().st_size > 0 and not force:
        return
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    proc = run_command(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(audio_path),
        ],
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "ffmpeg audio extraction failed").strip())


def format_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    millis = int(round(seconds * 1000))
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def load_inventory(root: Path) -> List[VideoItem]:
    inventory_path = root / "素材整理_asset_management/02_素材清单_manifest/素材总清单_asset_inventory.csv"
    items: List[VideoItem] = []
    if inventory_path.exists():
        with inventory_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                file_name = row.get("file_name", "")
                ext = row.get("file_ext", "").lower()
                if row.get("file_type") != "视频":
                    continue
                if ext not in {".mp4", ".mov", ".m4v"}:
                    continue
                if file_name.startswith("._"):
                    continue
                path = Path(row.get("file_path", ""))
                items.append(
                    VideoItem(
                        pair_id=row.get("pair_id", ""),
                        source_id=row.get("source_id", ""),
                        video_file_name=file_name,
                        video_path=path,
                        detected_topic=row.get("detected_topic", ""),
                    )
                )
    if items:
        return sorted(items, key=lambda item: item.source_id)

    material_dir = Path("/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据")
    for idx, path in enumerate(sorted(material_dir.rglob("*"))):
        if path.name.startswith("._"):
            continue
        if path.suffix.lower() not in {".mp4", ".mov", ".m4v"}:
            continue
        items.append(
            VideoItem(
                pair_id="",
                source_id=f"scan_video_{idx + 1:04d}",
                video_file_name=path.name,
                video_path=path,
                detected_topic=str(path.parent.name),
            )
        )
    return items


def load_existing_status(status_path: Path) -> Dict[str, Dict[str, str]]:
    if not status_path.exists():
        return {}
    with status_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return {row.get("source_id", ""): row for row in csv.DictReader(handle)}


def write_status(status_path: Path, rows: List[Dict[str, object]]) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=STATUS_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in STATUS_FIELDS})


def transcript_paths(item: VideoItem, transcript_dir: Path) -> tuple[Path, Path]:
    stem = output_stem(item)
    return transcript_dir / f"{stem}.json", transcript_dir / f"{stem}.txt"


def make_status_row(
    item: VideoItem,
    root: Path,
    json_path: Path,
    txt_path: Path,
    status: str,
    segment_count: int,
    duration_seconds: float,
    language: str,
    model_used: str,
    compute_type: str,
    error_message: str = "",
    needs_manual_review: str = "yes",
) -> Dict[str, object]:
    return {
        "pair_id": item.pair_id,
        "source_id": item.source_id,
        "video_file_name": item.video_file_name,
        "video_path": str(item.video_path),
        "transcript_json_path": rel(json_path, root),
        "transcript_txt_path": rel(txt_path, root),
        "status": status,
        "segment_count": segment_count,
        "duration_seconds": f"{duration_seconds:.3f}" if duration_seconds else "",
        "language": language,
        "model_used": model_used,
        "compute_type": compute_type,
        "error_message": error_message,
        "needs_manual_review": needs_manual_review,
    }


def write_transcripts(
    item: VideoItem,
    root: Path,
    json_path: Path,
    txt_path: Path,
    segments: List[Dict[str, object]],
    duration_seconds: float,
    language: str,
    language_probability: Optional[float],
    model_used: str,
    compute_type: str,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "pair_id": item.pair_id,
        "source_id": item.source_id,
        "video_file_name": item.video_file_name,
        "video_path": str(item.video_path),
        "detected_topic": item.detected_topic,
        "duration_seconds": duration_seconds,
        "language": language,
        "language_probability": language_probability,
        "model_used": model_used,
        "compute_type": compute_type,
        "quality_status": "pending_manual_review",
        "segments": segments,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# {item.video_file_name}",
        f"source_id: {item.source_id}",
        f"pair_id: {item.pair_id}",
        "quality_status: pending_manual_review",
        "",
    ]
    for segment in segments:
        start = segment["start_time"]
        end = segment["end_time"]
        text = str(segment["text"]).strip()
        lines.append(f"start_time: {start} | end_time: {end} | text: {text}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def transcribe_one(
    model: WhisperModel,
    item: VideoItem,
    root: Path,
    transcript_dir: Path,
    audio_dir: Path,
    model_used: str,
    compute_type: str,
    language_hint: str,
    force: bool,
) -> Dict[str, object]:
    json_path, txt_path = transcript_paths(item, transcript_dir)
    duration_seconds = ffprobe_duration(item.video_path)

    if not item.video_path.exists():
        return make_status_row(
            item,
            root,
            json_path,
            txt_path,
            "failed",
            0,
            duration_seconds,
            "",
            model_used,
            compute_type,
            "video_path_not_found",
        )

    if json_path.exists() and txt_path.exists() and not force:
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            segment_count = len(data.get("segments", []))
            return make_status_row(
                item,
                root,
                json_path,
                txt_path,
                "skipped",
                segment_count,
                duration_seconds,
                str(data.get("language", "")),
                model_used,
                compute_type,
                "existing_transcript_reused",
            )
        except Exception:
            pass

    audio_path = audio_dir / f"{output_stem(item)}.wav"
    extract_audio(item.video_path, audio_path, force=force)
    if not audio_path.exists() or audio_path.stat().st_size == 0:
        return make_status_row(
            item,
            root,
            json_path,
            txt_path,
            "failed",
            0,
            duration_seconds,
            "",
            model_used,
            compute_type,
            "empty_audio_after_ffmpeg_extract",
        )

    raw_segments, info = model.transcribe(
        str(audio_path),
        language=language_hint,
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    segments: List[Dict[str, object]] = []
    for idx, seg in enumerate(raw_segments, start=1):
        text = (seg.text or "").strip()
        if not text:
            continue
        segments.append(
            {
                "index": idx,
                "start_seconds": round(float(seg.start), 3),
                "end_seconds": round(float(seg.end), 3),
                "start_time": format_time(float(seg.start)),
                "end_time": format_time(float(seg.end)),
                "text": text,
            }
        )

    language = getattr(info, "language", "") or language_hint
    language_probability = getattr(info, "language_probability", None)
    if not segments:
        return make_status_row(
            item,
            root,
            json_path,
            txt_path,
            "failed",
            0,
            duration_seconds,
            language,
            model_used,
            compute_type,
            "no_segments_detected_or_empty_audio",
        )

    write_transcripts(
        item,
        root,
        json_path,
        txt_path,
        segments,
        duration_seconds,
        language,
        language_probability,
        model_used,
        compute_type,
    )
    return make_status_row(
        item,
        root,
        json_path,
        txt_path,
        "success",
        len(segments),
        duration_seconds,
        language,
        model_used,
        compute_type,
        "",
        "yes",
    )


def clean_apple_double(paths: Iterable[Path]) -> int:
    deleted = 0
    for base in paths:
        if not base.exists():
            continue
        for path in base.rglob("._*"):
            if path.is_file():
                path.unlink()
                deleted += 1
    return deleted


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch transcribe videos to local timecoded transcripts.")
    parser.add_argument("--model", default=os.environ.get("TIMECODE_MODEL", "small"))
    parser.add_argument("--device", default=os.environ.get("TIMECODE_DEVICE", "cpu"))
    parser.add_argument("--compute-type", default=os.environ.get("TIMECODE_COMPUTE_TYPE", "int8"))
    parser.add_argument("--language", default=os.environ.get("TIMECODE_LANGUAGE", "zh"))
    parser.add_argument("--force", action="store_true", help="re-run even if local transcript files exist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    timecode_dir = root / "素材整理_asset_management/04_时间码_timecode"
    transcript_dir = timecode_dir / "本地转写输出_local_transcripts"
    audio_dir = timecode_dir / "音频缓存_audio_cache"
    model_cache = timecode_dir / "model_cache"
    status_path = timecode_dir / "时间码全量转写状态_batch_timecode_status.csv"
    venv_dir = root / ".venv_timecode"

    for path in [transcript_dir, audio_dir, model_cache]:
        path.mkdir(parents=True, exist_ok=True)
    clean_apple_double([venv_dir, transcript_dir, audio_dir, model_cache])

    items = load_inventory(root)
    if not items:
        print("blocked: no videos found", file=sys.stderr)
        return 2

    existing = load_existing_status(status_path)
    rows: List[Dict[str, object]] = []
    model: Optional[WhisperModel] = None
    started = datetime.now().isoformat(timespec="seconds")
    print(f"batch_started={started}")
    print(f"video_count={len(items)}")
    print(f"model={args.model} device={args.device} compute_type={args.compute_type} language={args.language}")

    try:
        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
            download_root=str(model_cache),
        )
    except Exception as exc:
        message = f"blocked_model_download_failed_or_model_load_failed: {type(exc).__name__}: {exc}"
        for item in items:
            json_path, txt_path = transcript_paths(item, transcript_dir)
            rows.append(
                make_status_row(
                    item,
                    root,
                    json_path,
                    txt_path,
                    "failed",
                    0,
                    ffprobe_duration(item.video_path),
                    "",
                    args.model,
                    args.compute_type,
                    message,
                )
            )
        write_status(status_path, rows)
        print(message, file=sys.stderr)
        return 3

    for index, item in enumerate(items, start=1):
        prior = existing.get(item.source_id)
        print(f"[{index}/{len(items)}] {item.source_id} {item.video_file_name}", flush=True)
        started_item = time.time()
        try:
            row = transcribe_one(
                model,
                item,
                root,
                transcript_dir,
                audio_dir,
                args.model,
                args.compute_type,
                args.language,
                args.force,
            )
            if prior and row["status"] == "skipped":
                row["error_message"] = "existing_transcript_reused"
        except subprocess.TimeoutExpired as exc:
            json_path, txt_path = transcript_paths(item, transcript_dir)
            row = make_status_row(
                item,
                root,
                json_path,
                txt_path,
                "failed",
                0,
                ffprobe_duration(item.video_path),
                "",
                args.model,
                args.compute_type,
                f"failed_timeout: {exc}",
            )
        except Exception as exc:
            json_path, txt_path = transcript_paths(item, transcript_dir)
            row = make_status_row(
                item,
                root,
                json_path,
                txt_path,
                "failed",
                0,
                ffprobe_duration(item.video_path),
                "",
                args.model,
                args.compute_type,
                f"{type(exc).__name__}: {exc}",
            )
            traceback.print_exc()
        elapsed = time.time() - started_item
        print(
            f"status={row['status']} segments={row['segment_count']} duration={row['duration_seconds']} elapsed={elapsed:.1f}s",
            flush=True,
        )
        rows.append(row)
        write_status(status_path, rows)
        clean_apple_double([venv_dir, transcript_dir, audio_dir, model_cache])

    counts: Dict[str, int] = {}
    for row in rows:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    print("batch_finished=" + datetime.now().isoformat(timespec="seconds"))
    print("status_counts=" + json.dumps(counts, ensure_ascii=False, sort_keys=True))
    print(f"status_csv={rel(status_path, root)}")
    print(f"local_transcript_dir={rel(transcript_dir, root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
