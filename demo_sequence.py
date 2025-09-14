from exercise_logic import SquatCounter
import time

c = SquatCounter()  # use defaults

# Fake sequence: should produce 2 clean reps
sequence = []
sequence += [170] * 5      # warm-up standing
sequence += [88] * 12      # go down
sequence += [165] * 5      # stand up -> rep 1
sequence += [170] * 18     # idle frames (debounce gap)
sequence += [88] * 12      # down again
sequence += [165] * 5      # up again -> rep 2

for i, angle in enumerate(sequence, start=1):
    out = c.update_with_angle(angle, conf=1.0)
    print(f"Frame {i:02d}: reps={out['reps']} state={out['state']} angle={out['knee_angle']} flags={out['form_flags']}")
    time.sleep(0.03)  # slow down so you can read

print("\nFinal reps:", c.reps)
