# # import cv2
# # import base64
# # import requests
# # import time
# # import pyttsx3

# # # Backend Flask API
# # BACKEND_URL = "http://127.0.0.1:5000/analyze_frame"

# # # Supported poses (must match backend pose_equal_check.py)
# # POSES = [
# #     "pranamasana",
# #     "hastauttanasana",
# #     "hastapadasana",
# #     "right_ashwa_sanchalanasana",
# #     "dandasana",
# #     "ashtanga_namaskara",
# #     "bhujangasana",
# #     "adho_mukha_svanasana",
# #     "ashwa_sanchalanasana",
# # ]


# # def speak(text, engine):
# #     if not text:
# #         return
# #     engine.say(text)
# #     engine.runAndWait()


# # def build_feedback_text(pose_name, data):
# #     """
# #     Build a short feedback line to draw on the video frame,
# #     based on the JSON returned by /analyze_frame.
# #     """
# #     if not isinstance(data, dict):
# #         return "Invalid response from backend."

# #     if data.get("no_pose_detected"):
# #         return "No pose detected in the frame."

# #     msg = data.get("message", "")

# #     wrong_joints = data.get("wrong_joints") or []
# #     if wrong_joints:
# #         parts = []
# #         for item in wrong_joints:
# #             joint_words = item.get("joint_words") or item.get("joint") or ""
# #             change = item.get("change") or ""
# #             if joint_words and change:
# #                 parts.append(f"{joint_words}: {change}")
# #         if parts:
# #             joints_summary = "; ".join(parts[:3])  # cap to 3 for brevity
# #             return f"{pose_name}: {msg} ({joints_summary})"

# #     if msg:
# #         return f"{pose_name}: {msg}"

# #     return f"{pose_name}: Pose evaluated."


# # def select_pose_from_menu():
# #     print("Select a pose from the list below:\n")
# #     for idx, pose in enumerate(POSES, start=1):
# #         print(f"{idx}. {pose}")
# #     print()

# #     while True:
# #         choice = input(f"Enter pose number (1-{len(POSES)}) or 'q' to quit: ").strip().lower()

# #         if choice == "q":
# #             return None

# #         if choice.isdigit():
# #             idx = int(choice)
# #             if 1 <= idx <= len(POSES):
# #                 pose_name = POSES[idx - 1]
# #                 print(f"Selected pose: {pose_name}\n")
# #                 return pose_name

# #         print("Invalid choice. Please try again.")


# # def main():
# #     pose_name = select_pose_from_menu()
# #     if pose_name is None:
# #         print("Exiting without starting camera.")
# #         return

# #     cap = cv2.VideoCapture(0)
# #     if not cap.isOpened():
# #         print("❌ Could not open camera")
# #         return

# #     tts_engine = pyttsx3.init()
# #     last_feedback_time = 0.0
# #     FEEDBACK_INTERVAL = 2.0  # seconds

# #     print("Press 'q' in the video window to quit.")

# #     feedback_text = ""

# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             print("❌ Failed to read frame")
# #             break

# #         now = time.time()

# #         # Only call backend every FEEDBACK_INTERVAL seconds
# #         if now - last_feedback_time > FEEDBACK_INTERVAL:
# #             last_feedback_time = now

# #             ok, buffer = cv2.imencode(".jpg", frame)
# #             if ok:
# #                 img_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

# #                 payload = {
# #                     "pose_name": pose_name,
# #                     "frame_b64": img_b64,  # ✅ matches backend api.py
# #                 }

# #                 try:
# #                     resp = requests.post(BACKEND_URL, json=payload, timeout=5)
# #                     if resp.status_code == 200:
# #                         data = resp.json()
# #                         feedback_text = build_feedback_text(pose_name, data)

# #                         # Speak only the main message from backend
# #                         speak(data.get("message", ""), tts_engine)
# #                     else:
# #                         try:
# #                             err = resp.json()
# #                             feedback_text = f"Backend error {resp.status_code}: {err}"
# #                             print("Backend error response:", err)
# #                         except Exception:
# #                             feedback_text = f"Backend error: HTTP {resp.status_code}"
# #                 except Exception as e:
# #                     feedback_text = f"Error contacting backend: {e}"
# #             else:
# #                 feedback_text = "Error encoding frame"

# #         # Draw feedback text on the video frame
# #         if feedback_text:
# #             cv2.putText(
# #                 frame,
# #                 feedback_text[:80],  # truncate line for display
# #                 (10, 30),
# #                 cv2.FONT_HERSHEY_SIMPLEX,
# #                 0.7,
# #                 (0, 255, 0),
# #                 2,
# #                 cv2.LINE_AA,
# #             )

# #         cv2.imshow("Flexcellent - Frontend", frame)

# #         if cv2.waitKey(1) & 0xFF == ord("q"):
# #             break

# #     cap.release()
# #     cv2.destroyAllWindows()


# # if __name__ == "__main__":
# #     main()


# import cv2
# import base64
# import requests
# import time
# import threading
# import pygame
# import gtts as gTTS
# import io

# # Backend Flask API
# BACKEND_URL = "http://127.0.0.1:5000/analyze_frame"

# # Supported poses (must match backend pose_equal_check.py)
# POSES = [
#     "pranamasana",
#     "hastauttanasana",
#     "hastapadasana",
#     "right_ashwa_sanchalanasana",
#     "dandasana",
#     "ashtanga_namaskara",
#     "bhujangasana",
#     "adho_mukha_svanasana",
#     "ashwa_sanchalanasana",
# ]

# # --- audio (pygame + gTTS) setup ---

# AUDIO_AVAILABLE = True
# try:
#     pygame.mixer.init()
# except Exception as e:
#     AUDIO_AVAILABLE = False
#     print("Warning: Audio device not available, TTS will be disabled.", e)


# def text_to_speech(text: str) -> None:
#     """
#     Plays TTS audio using gTTS + pygame.
#     Runs in a background thread so it doesn't block the main loop.
#     """
#     if not AUDIO_AVAILABLE:
#         print("TTS skipped (no audio device):", text)
#         return

#     if not text:
#         return

#     try:
#         # gTTS calls Google over the network (text only, no images)
#         tts = gTTS.gTTS(text=text, lang="en")

#         mp3_fp = io.BytesIO()
#         tts.write_to_fp(mp3_fp)
#         mp3_fp.seek(0)

#         pygame.mixer.music.load(mp3_fp, "mp3")
#         pygame.mixer.music.play()

#         # Block only this background thread until audio finishes
#         while pygame.mixer.music.get_busy():
#             time.sleep(0.1)

#     except Exception as e:
#         print("Error in text_to_speech:", e)


# def speak_async(text: str) -> None:
#     """
#     Fire-and-forget TTS in a separate thread.
#     """
#     if not text:
#         return
#     threading.Thread(
#         target=text_to_speech,
#         args=(text,),
#         daemon=True,
#     ).start()


# def build_feedback_text(pose_name, data):
#     """
#     Build a short feedback line to draw on the video frame,
#     based on the JSON returned by /analyze_frame.
#     """
#     if not isinstance(data, dict):
#         return "Invalid response from backend."

#     if data.get("no_pose_detected"):
#         return "No pose detected in the frame."

#     msg = data.get("message", "")

#     wrong_joints = data.get("wrong_joints") or []
#     if wrong_joints:
#         parts = []
#         for item in wrong_joints:
#             joint_words = item.get("joint_words") or item.get("joint") or ""
#             change = item.get("change") or ""
#             if joint_words and change:
#                 parts.append(f"{joint_words}: {change}")
#         if parts:
#             joints_summary = "; ".join(parts[:3])  # cap to 3 for brevity
#             return f"{pose_name}: {msg} ({joints_summary})"

#     if msg:
#         return f"{pose_name}: {msg}"

#     return f"{pose_name}: Pose evaluated."


# def select_pose_from_menu():
#     print("Select a pose from the list below:\n")
#     for idx, pose in enumerate(POSES, start=1):
#         print(f"{idx}. {pose}")
#     print()

#     while True:
#         choice = input(f"Enter pose number (1-{len(POSES)}) or 'q' to quit: ").strip().lower()

#         if choice == "q":
#             return None

#         if choice.isdigit():
#             idx = int(choice)
#             if 1 <= idx <= len(POSES):
#                 pose_name = POSES[idx - 1]
#                 print(f"Selected pose: {pose_name}\n")
#                 return pose_name

#         print("Invalid choice. Please try again.")


# def main():
#     pose_name = select_pose_from_menu()
#     if pose_name is None:
#         print("Exiting without starting camera.")
#         return

#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         print("❌ Could not open camera")
#         return

#     last_feedback_time = 0.0
#     FEEDBACK_INTERVAL = 2.0  # seconds

#     print("Press 'q' in the video window to quit.")

#     feedback_text = ""

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("❌ Failed to read frame")
#             break

#         now = time.time()

#         # Only call backend every FEEDBACK_INTERVAL seconds
#         if now - last_feedback_time > FEEDBACK_INTERVAL:
#             last_feedback_time = now

#             ok, buffer = cv2.imencode(".jpg", frame)
#             if ok:
#                 img_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

#                 payload = {
#                     "pose_name": pose_name,
#                     "frame_b64": img_b64,  # ✅ matches backend api.py
#                 }

#                 try:
#                     resp = requests.post(BACKEND_URL, json=payload, timeout=5)
#                     if resp.status_code == 200:
#                         data = resp.json()
#                         feedback_text = build_feedback_text(pose_name, data)

#                         # Speak only the main message from backend, asynchronously
#                         speak_async(data.get("message", ""))
#                     else:
#                         try:
#                             err = resp.json()
#                             feedback_text = f"Backend error {resp.status_code}: {err}"
#                             print("Backend error response:", err)
#                         except Exception:
#                             feedback_text = f"Backend error: HTTP {resp.status_code}"
#                 except Exception as e:
#                     feedback_text = f"Error contacting backend: {e}"
#             else:
#                 feedback_text = "Error encoding frame"

#         # Draw feedback text on the video frame
#         if feedback_text:
#             cv2.putText(
#                 frame,
#                 feedback_text[:80],  # truncate line for display
#                 (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 255, 0),
#                 2,
#                 cv2.LINE_AA,
#             )

#         cv2.imshow("Flexcellent - Frontend", frame)

#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()


import cv2
import base64
import requests
import time
import threading
import pygame
import gtts as gTTS
import io

# Use backend's PoseDetector to draw pose points locally
from backend import PoseModule as pm

# Backend Flask API
BACKEND_URL = "http://127.0.0.1:5000/analyze_frame"

# Supported poses (must match backend pose_equal_check.py)
POSES = [
    "pranamasana",
    "hastauttanasana",
    "hastapadasana",
    "right_ashwa_sanchalanasana",
    "dandasana",
    "ashtanga_namaskara",
    "bhujangasana",
    "adho_mukha_svanasana",
    "ashwa_sanchalanasana",
]

# --- pose detection setup (for drawing only, not for scoring) ---
detector = pm.PoseDetector()

# --- audio (pygame + gTTS) setup ---

AUDIO_AVAILABLE = True
try:
    pygame.mixer.init()
except Exception as e:
    AUDIO_AVAILABLE = False
    print("Warning: Audio device not available, TTS will be disabled.", e)


def text_to_speech(text: str) -> None:
    """
    Plays TTS audio using gTTS + pygame.
    Runs in a background thread so it doesn't block the main loop.
    """
    if not AUDIO_AVAILABLE:
        print("TTS skipped (no audio device):", text)
        return

    if not text:
        return

    try:
        # gTTS calls Google over the network, sending only text.
        tts = gTTS.gTTS(text=text, lang="en")

        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        pygame.mixer.music.load(mp3_fp, "mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    except Exception as e:
        print("Error in text_to_speech:", e, " (text=", text, ")")


def speak_async(text: str) -> None:
    """
    Fire-and-forget TTS in a separate thread.
    """
    if not text:
        return
    threading.Thread(
        target=text_to_speech,
        args=(text,),
        daemon=True,
    ).start()


def build_feedback_text(pose_name, data):
    """
    Build a short feedback line to draw on the video frame,
    based on the JSON returned by /analyze_frame.
    """
    if not isinstance(data, dict):
        return "Invalid response from backend."

    if data.get("no_pose_detected"):
        return "No pose detected in the frame."

    msg = data.get("message", "")

    wrong_joints = data.get("wrong_joints") or []
    if wrong_joints:
        parts = []
        for item in wrong_joints:
            joint_words = item.get("joint_words") or item.get("joint") or ""
            change = item.get("change") or ""
            if joint_words and change:
                parts.append(f"{joint_words}: {change}")
        if parts:
            joints_summary = "; ".join(parts[:3])  # cap to 3 for brevity
            return f"{pose_name}: {msg} ({joints_summary})"

    if msg:
        return f"{pose_name}: {msg}"

    return f"{pose_name}: Pose evaluated."


def select_pose_from_menu():
    print("Select a pose from the list below:\n")
    for idx, pose in enumerate(POSES, start=1):
        print(f"{idx}. {pose}")
    print()

    while True:
        choice = input(f"Enter pose number (1-{len(POSES)}) or 'q' to quit: ").strip().lower()

        if choice == "q":
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(POSES):
                pose_name = POSES[idx - 1]
                print(f"Selected pose: {pose_name}\n")
                return pose_name

        print("Invalid choice. Please try again.")


def main():
    pose_name = select_pose_from_menu()
    if pose_name is None:
        print("Exiting without starting camera.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera")
        return

    last_feedback_time = 0.0
    FEEDBACK_INTERVAL = 2.0  # seconds

    print("Press 'q' in the video window to quit.")

    feedback_text = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break

        # --- draw pose keypoints locally for display ---
        display_frame = frame.copy()
        display_frame = detector.findPose(display_frame)  # this draws the landmarks

        now = time.time()

        # Only call backend every FEEDBACK_INTERVAL seconds
        if now - last_feedback_time > FEEDBACK_INTERVAL:
            last_feedback_time = now

            # Send the raw frame (without local drawings) to backend
            ok, buffer = cv2.imencode(".jpg", frame)
            if ok:
                img_b64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

                payload = {
                    "pose_name": pose_name,
                    "frame_b64": img_b64,  # ✅ matches backend api.py
                }

                try:
                    resp = requests.post(BACKEND_URL, json=payload, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        feedback_text = build_feedback_text(pose_name, data)

                        # Speak only the main message (or whatever you put in "message")
                        speak_async(data.get("message", ""))
                    else:
                        try:
                            err = resp.json()
                            feedback_text = f"Backend error {resp.status_code}: {err}"
                            print("Backend error response:", err)
                        except Exception:
                            feedback_text = f"Backend error: HTTP {resp.status_code}"
                except Exception as e:
                    feedback_text = f"Error contacting backend: {e}"
            else:
                feedback_text = "Error encoding frame"

        # Draw feedback text on the annotated frame
        if feedback_text:
            cv2.putText(
                display_frame,
                feedback_text[:80],  # truncate line for display
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        cv2.imshow("Flexcellent - Frontend", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
