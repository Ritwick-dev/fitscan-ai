from exercise_logic import ExponentialSmoother

s = ExponentialSmoother(alpha=0.5)
print(s.update(10))   # first input -> should be 10
print(s.update(20))   # average -> should be 15
print(s.update(30))   # mix -> should be 22.5

