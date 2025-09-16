from gamification import award_badges

# Sample history
history = [
    {"squat_reps": 12, "date": "2025-09-10"},
    {"squat_reps": 15, "date": "2025-09-11"},
    {"squat_reps": 8,  "date": "2025-09-12"},
]

# Latest session
latest = {"squat_reps": 20, "date": "2025-09-13"}

# Run badge awarder
badges = award_badges(history, latest)
print("Badges earned:", badges)
