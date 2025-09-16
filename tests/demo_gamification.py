from gamification import award_badges

# Fake history (not used much yet, but included)
history = [{"squat_reps": 15, "streak_days": 2}]

# Fake latest session
latest = {
    "squat_reps": 25,
    "pushup_reps": 10,
    "situp_reps": 15,
    "streak_days": 3,
    "above_avg": True,
    "logged_days": 1,
    "good_reps_percent": 95
}

# Call the function
result = award_badges(history, latest)

print("Badges earned:", result)
