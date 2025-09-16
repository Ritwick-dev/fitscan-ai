# exercise_logic.py
# Squat counter with knee angle calculation, smoother, and form checks.
# Beginner-friendly, safe fallbacks, and clear comments.

import math
from typing import Tuple, Dict, Any, Optional

# -----------------------
# Angle computation (dot-product)
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

    bax, bay = ax - bx, ay - by
    bcx, bcy = cx - bx, cy - by

    norm1 = math.hypot(bax, bay)
    norm2 = math.hypot(bcx, bcy)
    if norm1 == 0 or norm2 == 0:
        return 180.0

    dot = bax * bcx + bay * bcy
    cos_angle = dot / (norm1 * norm2)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle_rad = math.acos(cos_angle)
    return math.degrees(angle_rad)


# -----------------------
# Angle computation (atan2 method)
# -----------------------
def calculate_angle(a: Tuple[float, float],
                    b: Tuple[float, float],
                    c: Tuple[float, float]) -> Optional[float]:
    """
    a, b, c are (x,y) tuples.
    Returns angle at point b in degrees (0..180).
    Uses atan2 method and guards errors.
    """
    try:
        ang = math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0]) -
            math.atan2(a[1] - b[1], a[0] - b[0])
        )
        ang = abs(ang)
        if ang > 180:
            ang = 360 - ang
        return ang
    except Exception:
        return None


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
      - Emits form flags: "go_lower", "depth_ok", "low_confidence", "too_fast"
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

    def update(self, keypoints: Dict[str, Tuple[float, ...]]) -> Dict[str, Any]:
        """
        Main per-frame call using keypoints dict from AI Person.
        Grabs left & right leg angles, uses smaller one, and updates counter.
        Expected keypoints format:
          { "left_hip":(x,y,conf), "left_knee":(x,y,conf), "left_ankle":(x,y,conf),
            "right_hip":..., "right_knee":..., "right_ankle":... }
        """
        angles = []

        for side in ("left", "right"):
            hip = keypoints.get(f"{side}_hip")
            knee = keypoints.get(f"{side}_knee")
            ankle = keypoints.get(f"{side}_ankle")

            if hip and knee and ankle:
                # confidences (fallback 1.0 if missing)
                hconf = hip[2] if len(hip) > 2 else 1.0
                kconf = knee[2] if len(knee) > 2 else 1.0
                aconf = ankle[2] if len(ankle) > 2 else 1.0
                conf = min(hconf, kconf, aconf)

                if conf >= self.min_conf:
                    # use calculate_angle on (x,y) pairs
                    ang = calculate_angle((hip[0], hip[1]),
                                          (knee[0], knee[1]),
                                          (ankle[0], ankle[1]))
                    if ang is not None:
                        angles.append((ang, conf))

        if not angles:
            # No reliable legs found
            return {
                "reps": self.reps,
                "state": self.state,
                "knee_angle": None,
                "form_flags": ["low_confidence"]
            }

        # choose the smaller angle (deeper squat)
        angle, conf = min(angles, key=lambda x: x[0])
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
            # Provide live form feedback while down
            if smooth_angle > 100:
                flags.append("go_lower")
            else:
                flags.append("depth_ok")

            # Check if returned to standing
            if smooth_angle >= self.th_up:
                # returned to standing
                if self.depth_reached:
                    # only count if debounce passed
                    if (self.frame - self.last_rep_frame) >= self.min_frames_between:
                        self.reps += 1
                        # depth_ok already added while down; keep as coach feedback
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
