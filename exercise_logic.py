# exercise_logic.py
# Simple squat-angle calculator, smoother, and counter.
# Safe for beginners: guarded against divide-by-zero and missing keypoints.

import math
from typing import Tuple, Dict, Any, Optional

# -----------------------
# Angle computation
# -----------------------
def compute_angle(a, b, c) -> float:
    """
    Compute the angle at point b (in degrees) formed by points a-b-c.
    Each point can be (x,y) or (x,y,conf). We only use x,y here.
    Returns 180.0 on malformed input or zero-length vectors (safe fallback).
    """
    try:
        ax, ay = a[0], a[1]
        bx, by = b[0], b[1]
        cx, cy = c[0], c[1]
    except Exception:
        return 180.0

    # vectors BA (A - B) and BC (C - B)
    bax, bay = ax - bx, ay - by
    bcx, bcy = cx - bx, cy - by

    norm1 = math.hypot(bax, bay)
    norm2 = math.hypot(bcx, bcy)
    if norm1 == 0 or norm2 == 0:
        return 180.0

    dot = bax * bcx + bay * bcy
    cos_angle = dot / (norm1 * norm2)

    # clamp for numerical safety
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)


# -----------------------
# Tiny EMA smoother
# -----------------------
class ExponentialSmoother:
    """Small exponential moving average smoother."""
    def __init__(self, alpha: float = 0.3):
        assert 0.0 < alpha <= 1.0, "alpha must be in (0,1]"
        self.alpha = float(alpha)
        self.value: Optional[float] = None

    def update(self, x: float) -> float:
        """Feed a new scalar x. Returns smoothed value."""
        if x is None:
            # if nothing new, return last value or a safe default
            return self.value if self.value is not None else 180.0
        if self.value is None:
            self.value = float(x)
        else:
            self.value = self.alpha * float(x) + (1.0 - self.alpha) * self.value
        return self.value


# -----------------------
# SquatCounter class
# -----------------------
class SquatCounter:
    """
    SquatCounter:
      - Uses knee angle (hip-knee-ankle) per frame.
      - Counts when DOWN (<= th_down) -> UP (>= th_up).
      - Debounces with min_frames_between.
      - Uses min_conf to require keypoint confidence.
    """

    def __init__(self,
                 th_down: float = 90.0,
                 th_up: float = 160.0,
                 min_frames_between: int = 18,
                 min_conf: float = 0.3,
                 alpha: float = 0.3):
        self.th_down = float(th_down)
        self.th_up = float(th_up)
        self.min_frames_between = int(min_frames_between)
        self.min_conf = float(min_conf)
        self.smoother = ExponentialSmoother(alpha=alpha)

        # runtime state
        self.reps = 0
        self.state = "UP"              # "UP" or "DOWN"
        self.depth_reached = False
        self.last_rep_frame = -9999
        self.frame = 0
        self.min_angle_since_up = 180.0

    def reset(self):
        """Reset counters and smoothing (start fresh)."""
        self.smoother = ExponentialSmoother(alpha=self.smoother.alpha)
        self.reps = 0
        self.state = "UP"
        self.depth_reached = False
        self.last_rep_frame = -9999
        self.frame = 0
        self.min_angle_since_up = 180.0

    def _angle_and_conf_from_keypoints(self, keypoints: Dict[str, Tuple[float, ...]]) -> Tuple[Optional[float], Optional[float]]:
        """
        keypoints: dict with keys like 'left_hip', 'left_knee', 'left_ankle', same for 'right_'.
        Each value: (x, y, conf) or (x, y).
        Returns: (angle_degrees or None, confidence or None).
        Chooses the valid side with the smallest (deepest) angle.
        """
        candidates = []
        for side in ("left", "right"):
            hip = keypoints.get(f"{side}_hip")
            knee = keypoints.get(f"{side}_knee")
            ankle = keypoints.get(f"{side}_ankle")
            if hip is None or knee is None or ankle is None:
                continue
            # confidences if present
            hconf = hip[2] if len(hip) > 2 else 1.0
            kconf = knee[2] if len(knee) > 2 else 1.0
            aconf = ankle[2] if len(ankle) > 2 else 1.0
            side_conf = min(hconf, kconf, aconf)
            if side_conf < self.min_conf:
                continue
            angle = compute_angle(hip, knee, ankle)
            candidates.append((angle, side_conf))

        if not candidates:
            return None, None

        # choose the smallest angle (deepest knee)
        best = min(candidates, key=lambda x: x[0])
        return best[0], best[1]

    def update(self, keypoints: Dict[str, Tuple[float, ...]]) -> Dict[str, Any]:
        """
        Main per-frame call using keypoints dict from AI Person.
        Returns status dict with reps, state, knee_angle, form_flags.
        """
        angle, conf = self._angle_and_conf_from_keypoints(keypoints)
        return self.update_with_angle(angle, conf)

    def update_with_angle(self, angle: Optional[float], conf: Optional[float]) -> Dict[str, Any]:
        """
        For tests/demo: pass angle in degrees and a confidence (0..1).
        Returns status dict.
        """
        self.frame += 1
        flags = []

        # If no valid angle or low confidence -> keep state, set flag
        if angle is None or conf is None or conf < self.min_conf:
            flags.append("low_confidence")
            knee_angle_val = round(float(self.smoother.value), 2) if self.smoother.value is not None else None
            return {
                "reps": self.reps,
                "state": self.state,
                "knee_angle": knee_angle_val,
                "form_flags": flags
            }

        # Smooth incoming angle
        smooth_angle = self.smoother.update(angle)

        # Behavior depending on current state
        if self.state == "UP":
            # record minimum angle seen while above -> used to detect shallow attempts
            self.min_angle_since_up = min(self.min_angle_since_up, smooth_angle)
            if smooth_angle <= self.th_down:
                # went down deep enough
                self.state = "DOWN"
                self.depth_reached = True
        else:  # currently DOWN
            if smooth_angle >= self.th_up:
                # returned to standing
                if self.depth_reached:
                    # only count if debounce passed
                    if (self.frame - self.last_rep_frame) >= self.min_frames_between:
                        self.reps += 1
                        flags.append("depth_ok")
                        self.last_rep_frame = self.frame
                    else:
                        flags.append("too_fast")
                else:
                    flags.append("go_lower")
                # reset cycle
                self.state = "UP"
                self.depth_reached = False
                self.min_angle_since_up = 180.0

        knee_angle_out = round(float(smooth_angle), 2)
        return {
            "reps": self.reps,
            "state": self.state,
            "knee_angle": knee_angle_out,
            "form_flags": flags
        }
