#!/usr/bin/env python3
"""验证动作主题完整链 V2 的确定性规则。"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("build_live_action_topic_task_groups_v2.py")


def load_module():
    spec = importlib.util.spec_from_file_location("action_topic_v2", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载脚本：{SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ActionTopicV2RulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_module()

    def test_generic_action_problem_is_not_explicit_question(self) -> None:
        self.assertFalse(self.module.is_explicit_question("动作相关问题"))
        self.assertFalse(self.module.is_explicit_question("动作/练习口播"))
        self.assertTrue(self.module.is_explicit_question("经期可以往上吸吗"))
        self.assertTrue(self.module.is_explicit_question("經期可以往上吸嗎"))

    def test_full_asr_lookup_keeps_related_segments_more_than_150_seconds_apart(self) -> None:
        segments = [
            {"start_seconds": 10.0, "end_seconds": 13.0, "text": "这个点穴主要用来配合呼吸放松"},
            {"start_seconds": 205.0, "end_seconds": 208.0, "text": "找到大包穴后轻轻点按"},
        ]
        hits = self.module.find_topic_segments(segments, ["点穴", "大包穴"])
        self.assertEqual([10.0, 205.0], [row["start_seconds"] for row in hits])

    def test_body_part_conflict_is_a_veto(self) -> None:
        result = self.module.deterministic_conflict_check(
            speech_body_part="胸部",
            visual_body_part="腹部",
            speech_action_name="大包穴点按",
            visual_action_name="腹部按压",
            topic_break_present="no",
        )
        self.assertEqual("no", result["body_part_match"])
        self.assertEqual("logic_mismatch", result["forced_status"])

    def test_action_topic_ids_are_stable_and_chronological(self) -> None:
        visual_rows = [
            {"visual_action_unit_id": "VA007", "action_start_time": "00:40:28.510"},
            {"visual_action_unit_id": "VA005", "action_start_time": "00:32:07.320"},
        ]
        topics = self.module.assign_action_topic_ids(visual_rows, "513")
        self.assertEqual("VA005", topics[0]["visual_action_unit_id"])
        self.assertEqual("AT513_001", topics[0]["action_topic_id"])
        self.assertEqual("AT513_002", topics[1]["action_topic_id"])

    def test_repeated_anchor_uses_occurrence_nearest_visual_action(self) -> None:
        segments = [
            {"start_seconds": 100.0, "end_seconds": 102.0, "text": "当我们在吸气的时候"},
            {"start_seconds": 103.0, "end_seconds": 105.0, "text": "向下呼"},
            {"start_seconds": 1900.0, "end_seconds": 1902.0, "text": "当我们在吸气的时候"},
            {"start_seconds": 1903.0, "end_seconds": 1905.0, "text": "向下呼"},
        ]
        spec = self.module.EvidenceSpec("method", ("当我们在吸气的时候",), ("向下呼",), "method.mp4")
        evidence = self.module.build_evidence(segments, spec, reference_seconds=1920.0)
        self.assertEqual(1900.0, evidence["start_seconds"])

    def test_visual_action_check_uses_body_or_tool_evidence_from_same_unit(self) -> None:
        row = {
            "observed_action_name": "手指轻触或按压胸前位置",
            "observed_body_part_or_tool": "中指（劳宫穴位置）、胸部（乳头区域）",
        }
        combined = self.module.compose_visual_action_evidence(row)
        self.assertIn("劳宫穴", combined)
        result = self.module.deterministic_conflict_check(
            speech_body_part="胸部/乳头",
            visual_body_part=row["observed_body_part_or_tool"],
            speech_action_name="劳宫穴对准乳头并配合吸管式呼吸",
            visual_action_name=combined,
            topic_break_present="no",
        )
        self.assertEqual("yes", result["action_name_match"])

    def test_incomplete_or_unclear_action_cycle_cannot_be_true_pair(self) -> None:
        common = {
            "forced_status": "",
            "purpose_present": True,
            "method_present": True,
            "visual_clear": True,
            "explicit_question": True,
        }
        self.assertEqual(
            "partial_action_task_group",
            self.module.derive_task_group_status(action_cycle_status="no", **common)[0],
        )
        self.assertEqual(
            "manual_review",
            self.module.derive_task_group_status(action_cycle_status="unclear", **common)[0],
        )
        self.assertEqual(
            "true_pair_pending_user_review",
            self.module.derive_task_group_status(action_cycle_status="yes", **common)[0],
        )


if __name__ == "__main__":
    unittest.main()
