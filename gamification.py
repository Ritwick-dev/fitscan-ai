def award_badges(history: list, latest_session: dict) -> list:
    """
    history: list of past sessions (each is a dict)
    latest_session: dict with keys like
        {"squat_reps": 25, "pushup_reps": 10, "situp_reps": 15,
         "streak_days": 3, "above_avg": True}
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
    if latest_session.get("good_reps_percent", 0) >= 90:
        badges.append("Perfect Form")

    return badges
