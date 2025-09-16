

from datetime import datetime

# (Added milestone, streak, and consistency badges)
def award_badges(history: list, latest_session: dict) -> list:
    """
    history: list of past sessions (each is a dict)
    latest_session: dict with keys like
        {"squat_reps": 25, "pushup_reps": 10, "situp_reps": 15,

         "streak_days": 3, "above_avg": True}

         "streak_days": 3, "above_avg": True, "date": "2025-09-13"}

    returns: list of badge names earned this session
    """

    badges = []


    # 1. First 10 Squats
    if latest_session.get("squat_reps", 0) >= 10:
        badges.append("First 10 Squats")

    # 2. Consistency King
    if latest_session.get("streak_days", 0) >= 3:
        badges.append("Consistency King")

    # 3. Above Average
    if latest_session.get("above_avg", False):
        badges.append("Above Average")

    # 4. Endurance Hero
    if latest_session.get("squat_reps", 0) >= 50:
        badges.append("Endurance Hero")

    # 5. Daily Starter
    if latest_session.get("logged_days", 0) >= 1:
        badges.append("Daily Starter")

    # 6. Pushup Pro
    if latest_session.get("pushup_reps", 0) >= 30:
        badges.append("Pushup Pro")

    # 7. Perfect Form

    reps = latest_session.get("squat_reps", 0)

    # ✅ Day 2 Milestone Badges
    if reps >= 10:
        badges.append("First 10 Squats")
    if reps >= 20:
        badges.append("20 Reps Hero")
    if reps >= 50:
        badges.append("50 Reps Champion")

    # ✅ Day 2 Streak Badges
    try:
        # Combine history + latest session
        all_sessions = history + [latest_session]
        # Sort by date
        all_sessions = sorted(
            all_sessions,
            key=lambda s: datetime.strptime(s["date"], "%Y-%m-%d")
        )

        # Count streak backwards
        streak = 1
        for i in range(len(all_sessions) - 2, -1, -1):
            curr_date = datetime.strptime(all_sessions[i]["date"], "%Y-%m-%d")
            next_date = datetime.strptime(all_sessions[i + 1]["date"], "%Y-%m-%d")
            if (next_date - curr_date).days == 1:
                streak += 1
            else:
                break

        if streak >= 3:
            badges.append("3-Day Streak")
        if streak >= 7:
            badges.append("Weekly Warrior")

    except Exception:
        pass  # if dates missing or bad format, skip streak check

    # ✅ Day 2 Consistency Badge
    try:
        # Take last 5 sessions including latest
        all_sessions = history + [latest_session]
        last_five = all_sessions[-5:]

        if len(last_five) == 5 and all(s.get("squat_reps", 0) >= 5 for s in last_five):
            badges.append("Consistency Badge")

    except Exception:
        pass

    # ✅ Existing badges (Day 1 rules)
    if latest_session.get("streak_days", 0) >= 3:
        badges.append("Consistency King")

    if latest_session.get("above_avg", False):
        badges.append("Above Average")

    if reps >= 50:
        badges.append("Endurance Hero")

    if latest_session.get("logged_days", 0) >= 1:
        badges.append("Daily Starter")

    if latest_session.get("pushup_reps", 0) >= 30:
        badges.append("Pushup Pro")

# ddc5db4 (Added milestone, streak, and consistency badges)
    if latest_session.get("good_reps_percent", 0) >= 90:
        badges.append("Perfect Form")

    return badges
