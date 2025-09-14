# test_squat_counter.py
from exercise_logic import SquatCounter

# Use alpha=1.0 (no smoothing) and small debounce for unit test speed
c = SquatCounter(min_frames_between=3, alpha=1.0)

sequence = [
    170,           # standing
    88, 88,        # down (deep)
    165,           # up -> rep 1
    170, 170, 170, # idle frames to allow debounce
    88, 88,        # second down
    165            # up -> rep 2
]

for a in sequence:
    out = c.update_with_angle(a, conf=1.0)
    print(f"frame {c.frame:02d} angle={out['knee_angle']} state={out['state']} reps={out['reps']} flags={out['form_flags']}")

print("FINAL REPS:", c.reps)
