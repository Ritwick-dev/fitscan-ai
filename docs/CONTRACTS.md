# FitScan AI – Module Contracts

> This file defines simple input/output contracts for each module so team members can implement against a stable interface.

## pose_engine.py
```py
def get_keypoints(frame) -> dict
```
**Input:** `frame` (BGR image from webcam / numpy array)  
**Output:** `dict` mapping keypoint name → `(x, y, conf)`  
**Example:**
```json
{
  "left_hip": [120, 240, 0.98],
  "left_knee": [130, 360, 0.95],
  "left_ankle": [140, 480, 0.96],
  ...
}
```
Notes:
- `x, y` are pixel coordinates (int or float).
- `conf` is confidence score (0.0–1.0).
- Include at least: left/right hip, knee, ankle, shoulder, elbow, wrist.

---

## exercise_logic.py
```py
class SquatCounter:
    def update(keypoints: dict) -> dict
```
**Input:** `keypoints` as produced by `pose_engine.get_keypoints`  
**Output:** dict with keys:
```json
{
  "reps": 3,
  "state": "UP" | "DOWN",
  "knee_angle": 88.4,
  "form_flags": ["knee_valgus"]
}
```
Notes:
- `reps` is cumulative integer.
- `state` indicates current posture.
- `knee_angle` in degrees (float).
- `form_flags` is a list of strings describing form issues (may be empty).

---

## analytics.py
```py
def compute_percentiles(results: dict) -> dict
```
**Input:** `results` (e.g. aggregated user session stats)  
**Output:** percentile dictionary, example:
```json
{
  "squat_reps_pct": 73,
  "avg_depth_pct": 55
}
```
Notes:
- Percent values are integers 0–100.
- Expect keys for common metrics (reps, depth, tempo).

---

## gamification.py
```py
def award_badges(history: list, latest: dict) -> list
```
**Input:** `history` (list of past session summaries), `latest` (current session summary)  
**Output:** list of badge strings:
```json
["First 10 Squats", "Consistent Week"]
```
Notes:
- Badges are short human-readable strings.

---

## app.py
- **Responsibilities:**
  - Import and connect the above modules.
  - Run webcam feed and pass frames to `pose_engine.get_keypoints`.
  - Use `SquatCounter.update()` to get reps/state.
  - Display overlays: keypoints, rep counter, live form flags.
  - Provide a session summary and pass results to `analytics.compute_percentiles` and `gamification.award_badges`.
- **Assumptions:**
  - Modules follow contracts above.
  - All module I/O uses plain Python objects (dict, list, int, float).
