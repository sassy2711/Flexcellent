import cv2 as cv
import time
import threading
import pygame
import gtts as gTTS
import io
import warnings
import mediapipe as mp
import logging
import os

# Try package-relative imports first (for python -m backend.main / Docker),
# then fall back to local imports (for python main.py from backend/)
from .logging_setup import setup_logging
from .session import new_session
from .config import config
from . import PoseModule as pm
from . import pose_equal_check as pec


# --- environment flags ---
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "1"

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="google.protobuf.symbol_database"
)

# --- logging setup ---
setup_logging()
logger = logging.getLogger(__name__)

# --- pose detection setup ---
detector = pm.PoseDetector()
mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils
PoseSimilarity = pec.PoseSimilarity()

# --- audio (pygame) setup ---
AUDIO_AVAILABLE = True
try:
    pygame.mixer.init()
except Exception as e:
    AUDIO_AVAILABLE = False
    logger.warning(
        "Audio device not available, TTS will be disabled",
        extra={"error": str(e), "running_in_docker": RUNNING_IN_DOCKER},
    )


def text_to_speech(text: str) -> None:
    """Plays TTS audio. In Docker / no audio device, logs instead of playing."""
    if not AUDIO_AVAILABLE:
        logger.info(
            "TTS skipped (no audio device)",
            extra={"text": text},
        )
        return

    try:
        # NOTE: gTTS calls Google over the network, but sends only text,
        # not video/landmarks. For strict offline mode, swap gTTS out later.
        tts = gTTS.gTTS(text=text, lang="en")

        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        pygame.mixer.music.load(mp3_fp, "mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    except Exception as e:
        logger.error(
            "Error in text_to_speech",
            extra={"error": str(e), "text": text},
        )


def menu() -> None:
    print("Choose an asana:")
    print(
        "1. pranamasana\n"
        "2. hastauttanasana\n"
        "3. hastapadasana\n"
        "4. right_ashwa_sanchalanasana\n"
        "5. left_ashwa_sanchalanasana\n"
        "6. dandasana\n"
        "7. ashtanga_namaskara\n"
        "8. bhujangasana\n"
        "9. adho_mukha_svanasana"
    )


def main() -> None:
    text_to_speech("Program Starting.")
    logger.info("Program starting")

    menu()
    pose_name = input().strip()
    session = new_session(pose_name)

    logger.info(
        "New session started",
        extra={"session_id": session.session_id, "pose_name": pose_name},
    )

    last_check_time = time.time()
    vid = cv.VideoCapture(0)

    if not vid.isOpened():
        logger.error("Could not open camera")
        return

    while True:
        isTrue, input_frame = vid.read()

        if not isTrue:
            logger.error(
                "Failed to read from camera",
                extra={"session_id": session.session_id},
            )
            break

        original_height, original_width = input_frame.shape[:2]

        scale_factor = 1.5
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        input_frame = cv.resize(
            input_frame,
            (new_width, new_height),
            interpolation=cv.INTER_AREA,
        )

        input_frame = detector.findPose(input_frame)
        input_landmarks = detector.findPosition(input_frame)

        if len(input_landmarks) == 0:
            # No pose detected in this frame
            logger.debug(
                "No landmarks detected in frame",
                extra={"session_id": session.session_id},
            )

            if not RUNNING_IN_DOCKER:
                cv.imshow("Video", input_frame)
                if (cv.waitKey(10) & 0xFF) == ord("q"):
                    break

            continue

        # Normalize landmarks for comparison
        input_landmarks = PoseSimilarity.normalize_landmarks(
            input_landmarks,
            reference_idx=0,
        )
        current_time = time.time()

        # Check pose every 5 seconds
        if (current_time - last_check_time) > 5:
            last_check_time = current_time
            isSimilar, correct_landmarks = PoseSimilarity.isSimilar(
                pose_name,
                input_landmarks,
                0.1,
            )

            if isSimilar:
                wrong_joints = PoseSimilarity.get_wrong_joints(
                    pose_name,
                    correct_landmarks,
                    input_landmarks,
                    15,
                )

                logger.info(
                    "Pose evaluated",
                    extra={
                        "session_id": session.session_id,
                        "pose_name": pose_name,
                        "pose_similar": True,
                        "wrong_joint_count": len(wrong_joints),
                    },
                )

                if len(wrong_joints) == 0:
                    text = "You're doing it absolutely right."
                    threading.Thread(
                        target=text_to_speech,
                        args=(text,),
                        daemon=True,
                    ).start()
                else:
                    for joint_name, (_, change) in wrong_joints.items():
                        spoken = f"{change} angle at {' '.join(joint_name.split('_'))}"
                        threading.Thread(
                            target=text_to_speech,
                            args=(spoken,),
                            daemon=True,
                        ).start()
            else:
                logger.info(
                    "Pose evaluated",
                    extra={
                        "session_id": session.session_id,
                        "pose_name": pose_name,
                        "pose_similar": False,
                    },
                )
                text = "Thoda galat."
                threading.Thread(
                    target=text_to_speech,
                    args=(text,),
                    daemon=True,
                ).start()

        # Show video only in non-Docker/local mode
        if not RUNNING_IN_DOCKER:
            cv.imshow("Video", input_frame)

            # Quit on 'q'
            if (cv.waitKey(10) & 0xFF) == ord("q"):
                break
        else:
            # In Docker/headless mode: no imshow, no waitKey
            # Stop container with Ctrl+C or `docker stop`
            pass

    vid.release()
    cv.destroyAllWindows()

    logger.info(
        "Session ended",
        extra={"session_id": session.session_id},
    )


if __name__ == "__main__":
    main()
