#!/usr/bin/env python3
"""Validate strict blind-test generic rules."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("run_single_live_strict_blind_test.py")


def load_module():
    spec = importlib.util.spec_from_file_location("single_live_blind", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载脚本：{SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SingleLiveStrictBlindRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()
        cls.script_text = SCRIPT_PATH.read_text(encoding="utf-8")

    def test_script_has_no_manual_topic_specs_or_old_visual_ids(self) -> None:
        forbidden = ["TOPIC_SPECS", "VA005", "VA007", "VA009"]
        for token in forbidden:
            self.assertNotIn(token, self.script_text)

    def test_script_has_no_source_specific_answers_or_anchors(self) -> None:
        forbidden = ["6.2", "私房话", "6月2日", "劳宫穴", "云门", "中府", "大包", "乳头"]
        for token in forbidden:
            self.assertNotIn(token, self.script_text)

    def test_generic_problem_is_not_explicit_question(self) -> None:
        self.assertFalse(self.module.is_explicit_question("动作相关问题"))
        self.assertFalse(self.module.is_explicit_question("动作主题"))
        self.assertTrue(self.module.is_explicit_question("这个动作可以做吗"))

    def test_body_or_action_identity_cannot_be_time_only(self) -> None:
        visual = self.module.VisualUnit(
            action_topic_id="ATX_001",
            start_seconds=100.0,
            end_seconds=120.0,
            motion_score=9.0,
            contact_sheet=Path("sheet.jpg"),
            frame_timecodes=[],
            visual_status="action_visible_or_unclear",
            model_name="qwen3-vl-plus",
            observed_action_name="手臂上举",
            observed_body_part_or_tool="手臂",
            action_cycle_complete="yes",
            presenter_visible="yes",
            topic_break_risk="no",
            reason="test",
        )
        segments = [self.module.SpeechSegment(1, 98.0, 103.0, "这个动作很好，大家跟着做")]
        status, hits = self.module.identity_match_status(segments, visual)
        self.assertEqual("no", status)
        self.assertEqual([], hits)

    def test_direct_ready_requires_identity_method_cycle_and_no_break(self) -> None:
        visual = self.module.VisualUnit(
            action_topic_id="ATX_002",
            start_seconds=100.0,
            end_seconds=130.0,
            motion_score=9.0,
            contact_sheet=Path("sheet.jpg"),
            frame_timecodes=[],
            visual_status="action_visible_or_unclear",
            model_name="qwen3-vl-plus",
            observed_action_name="手臂上举",
            observed_body_part_or_tool="手臂",
            action_cycle_complete="yes",
            presenter_visible="yes",
            topic_break_risk="no",
            reason="test",
        )
        segments = [
            self.module.SpeechSegment(1, 10.0, 15.0, "这个手臂上举动作可以帮助打开肩部"),
            self.module.SpeechSegment(2, 20.0, 25.0, "先把手臂慢慢抬起来然后放下"),
        ]
        evidence = self.module.evidence_segments_for_visual(segments, visual)
        plan = self.module.classify_plan(visual, segments, evidence, Path("/tmp/final"), 1)
        assert plan is not None
        self.assertEqual("editor_ready_direct", plan.editor_usability_status)

    def test_pure_action_goes_manual_review(self) -> None:
        visual = self.module.VisualUnit(
            action_topic_id="ATX_003",
            start_seconds=100.0,
            end_seconds=130.0,
            motion_score=9.0,
            contact_sheet=Path("sheet.jpg"),
            frame_timecodes=[],
            visual_status="action_visible_or_unclear",
            model_name="qwen3-vl-plus",
            observed_action_name="手臂上举",
            observed_body_part_or_tool="手臂",
            action_cycle_complete="yes",
            presenter_visible="yes",
            topic_break_risk="no",
            reason="test",
        )
        evidence = self.module.evidence_segments_for_visual([], visual)
        plan = self.module.classify_plan(visual, [], evidence, Path("/tmp/final"), 1)
        assert plan is not None
        self.assertEqual("pending_manual_review", plan.editor_usability_status)

    def test_manual_review_filename_is_not_direct_ready(self) -> None:
        visual = self.module.VisualUnit(
            action_topic_id="ATX_004",
            start_seconds=100.0,
            end_seconds=130.0,
            motion_score=9.0,
            contact_sheet=Path("sheet.jpg"),
            frame_timecodes=[],
            visual_status="failed",
            model_name="",
            observed_action_name="",
            observed_body_part_or_tool="",
            action_cycle_complete="unclear",
            presenter_visible="unclear",
            topic_break_risk="unclear",
            reason="api failed",
        )
        evidence = self.module.evidence_segments_for_visual([], visual)
        plan = self.module.classify_plan(visual, [], evidence, Path("/tmp/final"), 1)
        assert plan is not None
        self.assertIn("08_人工复核", str(plan.final_video_path))
        self.assertNotIn("剪辑师直接版", plan.final_video_path.name)


if __name__ == "__main__":
    unittest.main()
