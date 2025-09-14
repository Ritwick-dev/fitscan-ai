# Squat Counter (exercise_logic.py)

This module provides SquatCounter, a simple rep counter and form checker.

- Call `logic = SquatCounter()` once.
- Each frame, call `status = logic.update(keypoints)`.
- `keypoints` format:
  {
    "left_hip": (x,y,conf), "left_knee": (x,y,conf), "left_ankle": (x,y,conf),
    "right_hip": (x,y,conf), "right_knee": (x,y,conf), "right_ankle": (x,y,conf)
  }
- Returned status dict:
  { "reps": int, "state": "UP"/"DOWN", "knee_angle": float, "form_flags": [...] }
- Thresholds: DOWN ≤ 90°, UP ≥ 160°, min_conf = 0.3.
- Includes smoothing (alpha=0.3) and min_frames_between=18 for stable counts.
- Run `demo_sequence.py` to see fake reps increasing.
