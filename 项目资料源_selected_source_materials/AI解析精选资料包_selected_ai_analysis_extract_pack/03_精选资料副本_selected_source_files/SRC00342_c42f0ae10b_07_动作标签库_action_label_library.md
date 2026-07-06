# 动作标签库

本标签库用于解释 `06_讲师动作时间轴_presenter_action_timeline.csv`、`09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv` 和 `data/presenter_actions.jsonl` 中的动作字段。

## 逐字稿动作标签

- `breathing_inhale`：逐字稿原句包含吸气、吸一口气等动作词。
- `breathing_exhale`：逐字稿原句包含呼气、吐气等动作词。
- `relax_release`：逐字稿原句包含放松、松开、释放等动作词。
- `tighten_contract`：逐字稿原句包含收紧、夹紧、用力、提肛等动作词。
- `lift_raise`：逐字稿原句包含抬起、抬高、上提等动作词。
- `lower_down`：逐字稿原句包含放下、下沉、往下等动作词。
- `rotate_circle`：逐字稿原句包含旋转、转圈、绕圈等动作词。
- `swing_sway`：逐字稿原句包含摆动、摇摆等动作词。
- `open_close`：逐字稿原句包含打开、合上、开合等动作词。
- `press_push`：逐字稿原句包含按压、压住、推、顶住等动作词。
- `pull_stretch`：逐字稿原句包含拉伸、拉开、牵拉等动作词。
- `massage_rub`：逐字稿原句包含按摩、揉、摩擦、揉捏等动作词。
- `step_transition`：逐字稿原句包含接下来、然后、下一步、最后等转场词。
- `point_focus`：逐字稿原句包含看这里、注意这里、重点、记住等强调/指向词。

## 视频动作/画面标签

- `slide_or_scene_no_presenter_detected`：视频采样帧可读，但未检测到讲师脸/手/身体，画面更接近课件或静态场景。
- `face_visible_speaking_pending_review`：检测到脸部可见，但具体表情和口型需要人工复核。
- `body_pose_visible_neutral_or_motion_pending_review`：检测到身体姿态，但具体动作需要人工复核。
- `hand_open_explain`：检测到手部且手指展开，推定为张手解释动作。
- `hand_point_or_counting_pending_review`：检测到手部，但可能是指向或数数，需要人工复核。
- `hand_visible_pending_review`：只确认手部可见，动作语义待复核。
- `video_frame_unreadable_pending_review`：该采样点视频帧不可读或路径不可达，动作和表情不能确认为事实。

## 表情、视线、镜头标签

- `face_visible_expression_pending_review`：脸部可见，具体表情待复核。
- `no_face_detected`：未检测到脸部。
- `unknown_frame_unreadable`：视频帧不可读，无法判断表情或视线。
- `front_close_face_visible`：讲师脸部近景可见。
- `front_or_side_medium_presenter_visible`：讲师中景或侧面可见。
- `slide_or_screen_full_no_presenter_detected`：课件/屏幕为主，未检测到讲师。
- `scene_no_presenter_detected`：静态场景或课件画面，无讲师可见。
- `unknown_frame_unreadable`：镜头状态不可确认。

## 使用规则

- `final_action_label` 优先使用逐字稿动作词；如果该句没有明确动作词，再使用视频采样标签。
- 多个动作标签用 `|` 连接，表示同一句逐字稿同时命中多个动作或节奏关键词。
- `action_source_basis` 会标出来源：`transcript_text_action_keyword` 表示来自逐字稿，`video_sample_feature` 表示来自视频采样。
- 所有包含 `pending_review`、`unknown`、`unreadable` 的标签均不能当作确定事实，必须人工复核后再用于数字人动作规则。
