# tests/test_logic.py
from exercise_logic import SquatCounter

logic = SquatCounter(min_frames_between=3, alpha=1.0)

# Fake squat sequence: standing -> down -> up
frames = [
    {"left_hip": (0,0,1), "left_knee": (0,1,1), "left_ankle": (0,2,1)},  # standing ~170°
    {"left_hip": (0,0,1), "left_knee": (0,1,1), "left_ankle": (1,2,1)},  # down ~88°
    {"left_hip": (0,0,1), "left_knee": (0,1,1), "left_ankle": (0,2,1)},  # up ~170°
]

print("Simulated squat sequence:")
for f in frames:
    out = logic.update(f)
    print(out)

print("Total reps:", logic.reps)
