# utils/draw.py
import cv2
import numpy as np
import math
import time

# Minimal connections for a lower-body stick figure
LINES = [
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("left_hip", "right_hip"),
]

def _demo_keypoints(frame_w, frame_h, t):
    """
    Produce a simple animated 'stick figure' so we can test overlays without the AI module.
    t = seconds since start (float)
    """
    cx, cy = frame_w // 2, int(frame_h * 0.55)
    stride = int(40 * math.sin(t))  # leg sway

    # Fake joints: hips fixed, knees/ankles sway a bit
    pts = {
        "left_hip":   (cx - 25, cy, 1.0),
        "right_hip":  (cx + 25, cy, 1.0),
        "left_knee":  (cx - 25 - stride//2, cy + 45, 1.0),
        "right_knee": (cx + 25 + stride//2, cy + 45, 1.0),
        "left_ankle": (cx - 25 - stride,    cy + 90, 1.0),
        "right_ankle":(cx + 25 + stride,    cy + 90, 1.0),
    }
    return pts

def draw_skeleton_and_overlay(frame_bgr, keypoints, out, demo=False, t=0.0):
    """
    frame_bgr: OpenCV BGR frame
    keypoints: dict like {"left_knee": (x,y,conf), ...} (ignored if demo=True)
    out: {"reps": int, "state": str, "knee_angle": float, "form_flags": [...]}
    demo: if True, we ignore `keypoints` and draw a fake animated stick figure
    t: animation time in seconds (float)
    returns: RGB image (numpy) ready for Streamlit
    """
    img = frame_bgr.copy()
    h, w = img.shape[:2]

    # pick source joints
    joints = _demo_keypoints(w, h, t) if demo else keypoints

    # draw joints
    for name, vals in joints.items():
        if not isinstance(vals, (list, tuple)) or len(vals) < 3:
            continue
        x, y, conf = vals
        if conf and conf > 0.3:
            cv2.circle(img, (int(x), int(y)), 5, (0, 255, 0), -1)

    # draw lines
    for a, b in LINES:
        if a in joints and b in joints:
            ax, ay, ac = joints[a]
            bx, by, bc = joints[b]
            if (ac or 0) > 0.3 and (bc or 0) > 0.3:
                cv2.line(img, (int(ax), int(ay)), (int(bx), int(by)), (255, 0, 0), 2)

    # text HUD
    text = f"Reps: {out.get('reps',0)} | State: {out.get('state','-')} | Angle: {int(out.get('knee_angle',0))}"
    cv2.putText(img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # convert to RGB for Streamlit
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
