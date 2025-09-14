# FitScan AI – Web Demo (Task 7: Summary Panel + Contracts for Data & Gamification)
# YOU: Web/UI Person

import streamlit as st
import cv2
import numpy as np
import time

from utils.draw import draw_skeleton_and_overlay

# ---- Safe imports for teammate modules (POSE / LOGIC) ----
POSE_AVAILABLE, LOGIC_AVAILABLE = True, True
POSE_ERR, LOGIC_ERR = "", ""

try:
    from pose_engine import get_keypoints  # get_keypoints(frame_bgr) -> dict {joint: (x,y,conf)}
except Exception as e:
    POSE_AVAILABLE = False
    POSE_ERR = f"{e}"

try:
    from exercise_logic import SquatCounter  # SquatCounter().update(keypoints) -> dict
except Exception as e:
    LOGIC_AVAILABLE = False
    LOGIC_ERR = f"{e}"

# ---- Safe imports for teammate modules (DATA / GAMIFICATION) ----
ANALYTICS_AVAILABLE, GAMIFICATION_AVAILABLE = True, True
ANALYTICS_ERR, GAMIFICATION_ERR = "", ""

try:
    from analytics import compute_percentiles  # compute_percentiles(session_totals_dict) -> {"squat_reps_pct": int}
except Exception as e:
    ANALYTICS_AVAILABLE = False
    ANALYTICS_ERR = f"{e}"

try:
    from gamification import award_badges  # award_badges(history, latest_session) -> list[str]
except Exception as e:
    GAMIFICATION_AVAILABLE = False
    GAMIFICATION_ERR = f"{e}"

st.set_page_config(page_title="FitScan AI", layout="wide")
st.title("FitScan AI – Web Demo")

# ---- Sidebar controls ----
with st.sidebar:
    st.header("Controls")
    exercise = st.selectbox("Exercise", ["Squats (Day 1)", "Push-ups (later)", "Sit-ups (later)"])
    run = st.checkbox("Start Camera", value=False, help="Tick to start a short live session")
    duration_sec = st.slider("Session duration (seconds)", 5, 120, 20)
    demo_mode = st.toggle(
        "Demo Overlay (fake skeleton today)",
        value=True,
        help="ON = draws a fake animated stick figure. OFF = use real keypoints + rep logic if available."
    )

# ---- Placeholders for video & stats ----
frame_window = st.empty()
col1, col2, col3 = st.columns(3)
rep_box = col1.metric("Reps", 0)
state_box = col2.metric("State", "-")
angle_box = col3.metric("Angle", 0)

# ---- Session state for summary/history ----
if "last_session" not in st.session_state:
    st.session_state.last_session = {"squat_reps": 0}
if "history" not in st.session_state:
    st.session_state.history = []  # you can append dicts of past sessions later

# ---- Prepare logic object (only if import succeeded) ----
logic = None
if LOGIC_AVAILABLE:
    try:
        logic = SquatCounter()
    except Exception as e:
        LOGIC_AVAILABLE = False
        LOGIC_ERR = f"{e}"

# ---- Integration status panel (for teammates) ----
with st.expander("Integration status (for teammates)", expanded=False):
    st.write({
        "pose_engine.py available": POSE_AVAILABLE,
        "exercise_logic.py available": LOGIC_AVAILABLE,
        "analytics.py available": ANALYTICS_AVAILABLE,
        "gamification.py available": GAMIFICATION_AVAILABLE,
    })
    if not POSE_AVAILABLE:
        st.warning(f"pose_engine not ready: {POSE_ERR}")
    if not LOGIC_AVAILABLE:
        st.warning(f"exercise_logic not ready: {LOGIC_ERR}")
    if not ANALYTICS_AVAILABLE:
        st.warning(f"analytics not ready: {ANALYTICS_ERR}")
    if not GAMIFICATION_AVAILABLE:
        st.warning(f"gamification not ready: {GAMIFICATION_ERR}")

# ---- Fallback logic_out for Demo Mode / safety ----
logic_out = {"reps": 0, "state": "-", "knee_angle": 0.0, "form_flags": []}

# ---- Webcam session ----
if run:
    cap = cv2.VideoCapture(0)  # try index 1 if you have multiple cameras
    if not cap.isOpened():
        st.error("Webcam not found. Try cv2.VideoCapture(1) or close other apps using the camera.")
    else:
        st.success("Camera started. It will auto-stop after the selected duration.")
        start_time = time.time()
        end_time = start_time + duration_sec

        while time.time() < end_time:
            ok, frame = cap.read()
            if not ok:
                st.error("Could not read from the camera.")
                break

            frame = cv2.flip(frame, 1)
            t = time.time() - start_time

            # --- Mode switch ---
            use_demo = demo_mode
            if not demo_mode:
                if not (POSE_AVAILABLE and LOGIC_AVAILABLE and logic is not None):
                    st.info("Real Mode requested but teammate modules not ready — falling back to Demo Mode.")
                    use_demo = True

            if use_demo:
                # Fake animation today (keeps UI stable)
                logic_out["reps"] = int(t // 3)
                logic_out["state"] = "DOWN" if int(t) % 2 == 0 else "UP"
                logic_out["knee_angle"] = 90 + 20 * np.sin(t)
                overlay = draw_skeleton_and_overlay(frame, keypoints={}, out=logic_out, demo=True, t=t)

            else:
                # Real mode: call teammates' contracts
                try:
                    keypoints = get_keypoints(frame)          # dict of joints
                    logic_out = logic.update(keypoints)       # {"reps","state","knee_angle","form_flags"}
                    overlay = draw_skeleton_and_overlay(frame, keypoints=keypoints, out=logic_out, demo=False, t=t)
                except Exception as e:
                    st.error(f"Real Mode error: {e}")
                    logic_out["reps"] = int(t // 3)
                    logic_out["state"] = "DOWN" if int(t) % 2 == 0 else "UP"
                    logic_out["knee_angle"] = 90 + 20 * np.sin(t)
                    overlay = draw_skeleton_and_overlay(frame, keypoints={}, out=logic_out, demo=True, t=t)

            # Render frame & mini HUD
            frame_window.image(overlay, channels="RGB")
            rep_box.metric("Reps", logic_out["reps"])
            state_box.metric("State", logic_out["state"])
            angle_box.metric("Angle", int(logic_out["knee_angle"]))
            time.sleep(0.01)

        cap.release()
        # Save this session’s totals for the Summary panel
        st.session_state.last_session = {"squat_reps": int(logic_out.get("reps", 0))}
        st.info("Camera session ended. Tick 'Start Camera' again to restart.")
else:
    st.info("Tick **Start Camera** to begin a timed webcam session. Use **Demo Overlay** to see a fake skeleton today.")

st.divider()

# ---- SUMMARY PANEL ----
st.subheader("Session Summary")

last = st.session_state.get("last_session", {"squat_reps": 0})
c1, c2, c3 = st.columns([1, 2, 2])
with c1:
    st.metric("Total Squats", last.get("squat_reps", 0))

# Percentiles (Data Person)
with c2:
    st.markdown("**Percentile vs Peers**")
    if ANALYTICS_AVAILABLE:
        try:
            pct = compute_percentiles({"squat_reps": last.get("squat_reps", 0)})
            pct_val = pct.get("squat_reps_pct", "—")
            st.write(f"**Squat Reps Percentile:** {pct_val}%")
        except Exception as e:
            st.warning(f"Analytics error: {e}")
    else:
        st.info("Analytics module not ready. Waiting for `analytics.compute_percentiles(...)`.")

# Badges (Gamification Person)
with c3:
    st.markdown("**Badges Earned**")
    if GAMIFICATION_AVAILABLE:
        try:
            badges = award_badges(history=st.session_state.get("history", []),
                                  latest_session={"squat_reps": last.get("squat_reps", 0)})
            if badges:
                st.write(", ".join(badges))
            else:
                st.write("—")
        except Exception as e:
            st.warning(f"Gamification error: {e}")
    else:
        st.info("Gamification module not ready. Waiting for `gamification.award_badges(...)`.")
