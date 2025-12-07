# # import base64
# # import io
# # import logging
# # import os

# # import cv2 as cv
# # import numpy as np
# # from flask import Flask, jsonify, request

# # from .logging_setup import setup_logging
# # from .session import new_session
# # from .config import config
# # from . import PoseModule as pm
# # from . import pose_equal_check as pec

# # # -------------------------------------------------------------------
# # # Environment / logging setup
# # # -------------------------------------------------------------------

# # RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "1"

# # setup_logging()
# # logger = logging.getLogger(__name__)

# # # -------------------------------------------------------------------
# # # Pose detection setup (same as in main.py)
# # # -------------------------------------------------------------------

# # detector = pm.PoseDetector()
# # PoseSimilarity = pec.PoseSimilarity()


# # # -------------------------------------------------------------------
# # # Small helper: make arbitrary structures JSON-safe
# # # -------------------------------------------------------------------

# # def _make_jsonable(obj):
# #     """Recursively convert numbers / arrays into JSON-serializable types."""
# #     import numpy as _np

# #     if isinstance(obj, (str, int, float, bool)) or obj is None:
# #         return obj
# #     if isinstance(obj, (_np.floating, _np.integer)):
# #         return float(obj)
# #     if isinstance(obj, (list, tuple)):
# #         return [_make_jsonable(x) for x in obj]
# #     if isinstance(obj, dict):
# #         return {str(k): _make_jsonable(v) for k, v in obj.items()}
# #     # Fallback for unexpected types
# #     return str(obj)


# # # -------------------------------------------------------------------
# # # Flask app
# # # -------------------------------------------------------------------

# # app = Flask(__name__)


# # @app.route("/health", methods=["GET"])
# # def health():
# #     """Simple liveness endpoint."""
# #     return jsonify({"status": "ok", "service": "flexcellent-backend"}), 200


# # @app.route("/analyze_frame", methods=["POST"])
# # def analyze_frame():
# #     """
# #     Request JSON format:

# #     {
# #       "pose_name": "pranamasana",
# #       "frame_b64": "<base64-encoded JPEG/PNG>"
# #     }

# #     Response JSON format (example):

# #     {
# #       "session_id": "...",
# #       "pose_name": "pranamasana",
# #       "pose_similar": true,
# #       "no_pose_detected": false,
# #       "wrong_joints": [
# #         {
# #           "joint": "left_knee",
# #           "change": "increase",
# #           "angle_info": [90.0, 120.0]
# #         }
# #       ],
# #       "message": "You're doing it absolutely right."
# #     }
# #     """
# #     try:
# #         data = request.get_json(silent=True) or {}
# #         pose_name = (data.get("pose_name") or "").strip()
# #         frame_b64 = data.get("frame_b64")

# #         if not pose_name:
# #             return jsonify({"error": "pose_name is required"}), 400
# #         if not frame_b64:
# #             return jsonify({"error": "frame_b64 is required"}), 400

# #         # Create a session mainly for logging/tracing
# #         session = new_session(pose_name)
# #         session_id = session.session_id

# #         # -------------------------------------------------------------------
# #         # Decode base64 image into a BGR frame (OpenCV style)
# #         # -------------------------------------------------------------------
# #         try:
# #             img_bytes = base64.b64decode(frame_b64)
# #             np_arr = np.frombuffer(img_bytes, np.uint8)
# #             frame_bgr = cv.imdecode(np_arr, cv.IMREAD_COLOR)
# #         except Exception as e:
# #             logger.error(
# #                 "Failed to decode frame",
# #                 extra={"session_id": session_id, "error": str(e)},
# #             )
# #             return jsonify({"error": "invalid frame_b64"}), 400

# #         if frame_bgr is None:
# #             return jsonify({"error": "could not decode image"}), 400

# #         # -------------------------------------------------------------------
# #         # Reuse the pipeline from main.py
# #         # (resize, find pose, normalize landmarks, check similarity)
# #         # -------------------------------------------------------------------

# #         original_height, original_width = frame_bgr.shape[:2]
# #         scale_factor = 1.5
# #         new_width = int(original_width * scale_factor)
# #         new_height = int(original_height * scale_factor)

# #         frame_bgr = cv.resize(
# #             frame_bgr,
# #             (new_width, new_height),
# #             interpolation=cv.INTER_AREA,
# #         )

# #         frame_bgr = detector.findPose(frame_bgr)
# #         input_landmarks = detector.findPosition(frame_bgr)

# #         if len(input_landmarks) == 0:
# #             logger.info(
# #                 "No landmarks detected in frame",
# #                 extra={"session_id": session_id, "pose_name": pose_name},
# #             )
# #             return jsonify(
# #                 {
# #                     "session_id": session_id,
# #                     "pose_name": pose_name,
# #                     "pose_similar": False,
# #                     "no_pose_detected": True,
# #                     "wrong_joints": [],
# #                     "message": "No pose detected in the frame.",
# #                 }
# #             ), 200

# #         # Normalize landmarks for comparison (same as main.py)
# #         input_landmarks = PoseSimilarity.normalize_landmarks(
# #             input_landmarks,
# #             reference_idx=0,
# #         )

# #         # Thresholds reused from main.py logic
# #         similarity_threshold = 0.1
# #         angle_threshold = 15

# #         isSimilar, correct_landmarks = PoseSimilarity.isSimilar(
# #             pose_name,
# #             input_landmarks,
# #             similarity_threshold,
# #         )

# #         response = {
# #             "session_id": session_id,
# #             "pose_name": pose_name,
# #             "pose_similar": bool(isSimilar),
# #             "no_pose_detected": False,
# #             "wrong_joints": [],
# #             "message": "",
# #         }

# #         if isSimilar:
# #             wrong_joints = PoseSimilarity.get_wrong_joints(
# #                 pose_name,
# #                 correct_landmarks,
# #                 input_landmarks,
# #                 angle_threshold,
# #             )

# #             logger.info(
# #                 "Pose evaluated",
# #                 extra={
# #                     "session_id": session_id,
# #                     "pose_name": pose_name,
# #                     "pose_similar": True,
# #                     "wrong_joint_count": len(wrong_joints),
# #                 },
# #             )

# #             if len(wrong_joints) == 0:
# #                 response["message"] = "You're doing it absolutely right."
# #                 response["wrong_joints"] = []
# #             else:
# #                 # Convert wrong_joints dict into a JSON-safe list
# #                 items = []
# #                 for joint_name, value in wrong_joints.items():
# #                     # In your main.py you do: for joint_name, (_, change) in wrong_joints.items()
# #                     # so value is expected to be (angle_info, change)
# #                     if isinstance(value, (list, tuple)) and len(value) == 2:
# #                         angle_info, change = value
# #                     else:
# #                         angle_info, change = None, value

# #                     items.append(
# #                         {
# #                             "joint": str(joint_name),
# #                             "change": str(change),
# #                             "angle_info": _make_jsonable(angle_info),
# #                             "joint_words": " ".join(str(joint_name).split("_")),
# #                         }
# #                     )

# #                 response["wrong_joints"] = items
# #                 response["message"] = "Some joint angles need correction."
# #         else:
# #             logger.info(
# #                 "Pose evaluated",
# #                 extra={
# #                     "session_id": session_id,
# #                     "pose_name": pose_name,
# #                     "pose_similar": False,
# #                 },
# #             )
# #             response["message"] = "Pose does not match the target posture."

# #         return jsonify(response), 200

# #     except Exception as e:
# #         logger.error(
# #             "Error in /analyze_frame: %s",
# #             str(e),
# #             extra={"error_type": type(e).__name__},
# #         )
# #         return jsonify({"error": "internal server error", "details": str(e)}), 500



# # def main():
# #     # Bind host/port from config if you like, otherwise default 0.0.0.0:5000
# #     host = getattr(config, "host", "0.0.0.0")
# #     port = getattr(config, "port", 5000)

# #     logger.info(
# #         "Starting Flexcellent Flask API",
# #         extra={"host": host, "port": port, "running_in_docker": RUNNING_IN_DOCKER},
# #     )

# #     app.run(host=host, port=port)


# # if __name__ == "__main__":
# #     main()


# import base64
# import logging
# import os

# import cv2 as cv
# import numpy as np
# from flask import Flask, jsonify, request

# from .logging_setup import setup_logging
# from .session import new_session
# from .config import config
# from . import PoseModule as pm
# from . import pose_equal_check as pec

# # -------------------------------------------------------------------
# # Environment / logging setup
# # -------------------------------------------------------------------

# RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "1"

# setup_logging()
# logger = logging.getLogger(__name__)

# # -------------------------------------------------------------------
# # Pose detection setup (same as in main.py)
# # -------------------------------------------------------------------

# detector = pm.PoseDetector()
# PoseSimilarity = pec.PoseSimilarity()

# # -------------------------------------------------------------------
# # Flask app
# # -------------------------------------------------------------------

# app = Flask(__name__)


# @app.route("/health", methods=["GET"])
# def health():
#     """Simple liveness endpoint."""
#     return jsonify({"status": "ok", "service": "flexcellent-backend"}), 200


# @app.route("/analyze_frame", methods=["POST"])
# def analyze_frame():
#     """
#     Request JSON format:

#     {
#       "pose_name": "pranamasana",
#       "frame_b64": "<base64-encoded JPEG/PNG>"
#     }

#     Response JSON format (example):

#     {
#       "session_id": "...",
#       "pose_name": "pranamasana",
#       "pose_similar": true,
#       "no_pose_detected": false,
#       "wrong_joints": [
#         {
#           "joint": "left_knee",
#           "change": "increase",
#           "joint_words": "left knee",
#           "speak_text": "increase angle at left knee"
#         }
#       ],
#       "message": "Thoda Galat.",
#       "annotated_frame_b64": "<base64 JPEG with landmarks drawn>"
#     }
#     """
#     try:
#         data = request.get_json(silent=True) or {}
#         pose_name = (data.get("pose_name") or "").strip()
#         frame_b64 = data.get("frame_b64")

#         if not pose_name:
#             return jsonify({"error": "pose_name is required"}), 400
#         if not frame_b64:
#             return jsonify({"error": "frame_b64 is required"}), 400

#         # Create a session mainly for logging/tracing
#         session = new_session(pose_name)
#         session_id = session.session_id

#         # -------------------------------------------------------------------
#         # Decode base64 image into a BGR frame (OpenCV style)
#         # -------------------------------------------------------------------
#         try:
#             img_bytes = base64.b64decode(frame_b64)
#             np_arr = np.frombuffer(img_bytes, np.uint8)
#             frame_bgr = cv.imdecode(np_arr, cv.IMREAD_COLOR)
#         except Exception as e:
#             logger.error(
#                 "Failed to decode frame",
#                 extra={"session_id": session_id, "error": str(e)},
#             )
#             return jsonify({"error": "invalid frame_b64"}), 400

#         if frame_bgr is None:
#             return jsonify({"error": "could not decode image"}), 400

#         # -------------------------------------------------------------------
#         # Resize + detect pose
#         # -------------------------------------------------------------------

#         original_height, original_width = frame_bgr.shape[:2]
#         scale_factor = 1.5
#         new_width = int(original_width * scale_factor)
#         new_height = int(original_height * scale_factor)

#         frame_bgr = cv.resize(
#             frame_bgr,
#             (new_width, new_height),
#             interpolation=cv.INTER_AREA,
#         )

#         # detector.findPose draws landmarks on frame_bgr
#         frame_bgr = detector.findPose(frame_bgr)
#         input_landmarks = detector.findPosition(frame_bgr)

#         # Encode the annotated frame (with pose points) to send back
#         annotated_frame_b64 = None
#         ok, buf = cv.imencode(".jpg", frame_bgr)
#         if ok:
#             annotated_frame_b64 = base64.b64encode(buf.tobytes()).decode("utf-8")

#         if len(input_landmarks) == 0:
#             logger.info(
#                 "No landmarks detected in frame",
#                 extra={"session_id": session_id, "pose_name": pose_name},
#             )
#             return jsonify(
#                 {
#                     "session_id": session_id,
#                     "pose_name": pose_name,
#                     "pose_similar": False,
#                     "no_pose_detected": True,
#                     "wrong_joints": [],
#                     "message": "No pose detected in the frame.",
#                     "annotated_frame_b64": annotated_frame_b64,
#                 }
#             ), 200

#         # Normalize landmarks for comparison (same as main.py)
#         input_landmarks = PoseSimilarity.normalize_landmarks(
#             input_landmarks,
#             reference_idx=0,
#         )

#         # Thresholds reused from main.py logic
#         similarity_threshold = 0.1
#         angle_threshold = 15

#         isSimilar, correct_landmarks = PoseSimilarity.isSimilar(
#             pose_name,
#             input_landmarks,
#             similarity_threshold,
#         )

#         response = {
#             "session_id": session_id,
#             "pose_name": pose_name,
#             "pose_similar": bool(isSimilar),
#             "no_pose_detected": False,
#             "wrong_joints": [],
#             "message": "",
#             "annotated_frame_b64": annotated_frame_b64,
#         }

#         if isSimilar:
#             # get_wrong_joints returns: { joint_name: (joint_name, "increase"/"decrease") }
#             wrong_joints = PoseSimilarity.get_wrong_joints(
#                 pose_name,
#                 correct_landmarks,
#                 input_landmarks,
#                 angle_threshold,
#             )

#             logger.info(
#                 "Pose evaluated",
#                 extra={
#                     "session_id": session_id,
#                     "pose_name": pose_name,
#                     "pose_similar": True,
#                     "wrong_joint_count": len(wrong_joints),
#                 },
#             )

#             if len(wrong_joints) == 0:
#                 response["message"] = "You're doing it absolutely right."
#                 response["wrong_joints"] = []
#             else:
#                 items = []
#                 for joint_name, (_, change) in wrong_joints.items():
#                     joint_words = " ".join(str(joint_name).split("_"))
#                     items.append(
#                         {
#                             "joint": str(joint_name),
#                             "change": str(change),
#                             "joint_words": joint_words,
#                             "speak_text": f"{change} angle at {joint_words}",
#                         }
#                     )

#                 response["wrong_joints"] = items
#                 response["message"] = items["speak_text"]
#         else:
#             logger.info(
#                 "Pose evaluated",
#                 extra={
#                     "session_id": session_id,
#                     "pose_name": pose_name,
#                     "pose_similar": False,
#                 },
#             )
#             # Overall pose not similar enough
#             response["message"] = "Thoda Galat."
#             response["wrong_joints"] = []

#         return jsonify(response), 200

#     except Exception as e:
#         logger.error(
#             "Error in /analyze_frame: %s",
#             str(e),
#             extra={"error_type": type(e).__name__},
#         )
#         return jsonify({"error": "internal server error", "details": str(e)}), 500


# def main():
#     # Bind host/port from config if you like, otherwise default 0.0.0.0:5000
#     host = getattr(config, "host", "0.0.0.0")
#     port = getattr(config, "port", 5000)

#     logger.info(
#         "Starting Flexcellent Flask API",
#         extra={"host": host, "port": port, "running_in_docker": RUNNING_IN_DOCKER},
#     )

#     app.run(host=host, port=port)


# if __name__ == "__main__":
#     main()

import base64
import logging
import os

import cv2 as cv
import numpy as np
from flask import Flask, jsonify, request

from .logging_setup import setup_logging
from .session import new_session
from .config import config
from . import PoseModule as pm
from . import pose_equal_check as pec

# -------------------------------------------------------------------
# Environment / logging setup
# -------------------------------------------------------------------

RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "1"

setup_logging()
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Pose detection setup (same as in main.py)
# -------------------------------------------------------------------

detector = pm.PoseDetector()
PoseSimilarity = pec.PoseSimilarity()

# -------------------------------------------------------------------
# Flask app
# -------------------------------------------------------------------

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    """Simple liveness endpoint."""
    return jsonify({"status": "ok", "service": "flexcellent-backend"}), 200


@app.route("/analyze_frame", methods=["POST"])
def analyze_frame():
    """
    Request JSON format:

    {
      "pose_name": "pranamasana",
      "frame_b64": "<base64-encoded JPEG/PNG>"
    }

    Response JSON format (example):

    {
      "session_id": "...",
      "pose_name": "pranamasana",
      "pose_similar": true,
      "no_pose_detected": false,
      "wrong_joints": [
        {
          "joint": "neck_joint",
          "change": "increase",
          "joint_words": "neck joint",
          "speak_text": "Increase angle at neck joint"
        }
      ],
      "message": "Increase angle at neck joint. Decrease angle at right knee joint",
      "annotated_frame_b64": "<base64 JPEG with landmarks drawn>"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        pose_name = (data.get("pose_name") or "").strip()
        frame_b64 = data.get("frame_b64")

        if not pose_name:
            return jsonify({"error": "pose_name is required"}), 400
        if not frame_b64:
            return jsonify({"error": "frame_b64 is required"}), 400

        # Create a session mainly for logging/tracing
        session = new_session(pose_name)
        session_id = session.session_id

        # -------------------------------------------------------------------
        # Decode base64 image into a BGR frame (OpenCV style)
        # -------------------------------------------------------------------
        try:
            img_bytes = base64.b64decode(frame_b64)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            frame_bgr = cv.imdecode(np_arr, cv.IMREAD_COLOR)
        except Exception as e:
            logger.error(
                "Failed to decode frame",
                extra={"session_id": session_id, "error": str(e)},
            )
            return jsonify({"error": "invalid frame_b64"}), 400

        if frame_bgr is None:
            return jsonify({"error": "could not decode image"}), 400

        # -------------------------------------------------------------------
        # Resize + detect pose
        # -------------------------------------------------------------------

        original_height, original_width = frame_bgr.shape[:2]
        scale_factor = 1.5
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        frame_bgr = cv.resize(
            frame_bgr,
            (new_width, new_height),
            interpolation=cv.INTER_AREA,
        )

        # detector.findPose draws landmarks on frame_bgr
        frame_bgr = detector.findPose(frame_bgr)
        input_landmarks = detector.findPosition(frame_bgr)

        # Encode the annotated frame (with pose points) to send back
        annotated_frame_b64 = None
        ok, buf = cv.imencode(".jpg", frame_bgr)
        if ok:
            annotated_frame_b64 = base64.b64encode(buf.tobytes()).decode("utf-8")

        if len(input_landmarks) == 0:
            logger.info(
                "No landmarks detected in frame",
                extra={"session_id": session_id, "pose_name": pose_name},
            )
            return jsonify(
                {
                    "session_id": session_id,
                    "pose_name": pose_name,
                    "pose_similar": False,
                    "no_pose_detected": True,
                    "wrong_joints": [],
                    "message": "No pose detected in the frame.",
                    "annotated_frame_b64": annotated_frame_b64,
                }
            ), 200

        # Normalize landmarks for comparison (same as main.py)
        input_landmarks = PoseSimilarity.normalize_landmarks(
            input_landmarks,
            reference_idx=0,
        )

        # Thresholds reused from main.py logic
        similarity_threshold = 0.1
        angle_threshold = 15

        isSimilar, correct_landmarks = PoseSimilarity.isSimilar(
            pose_name,
            input_landmarks,
            similarity_threshold,
        )

        response = {
            "session_id": session_id,
            "pose_name": pose_name,
            "pose_similar": bool(isSimilar),
            "no_pose_detected": False,
            "wrong_joints": [],
            "message": "",
            "annotated_frame_b64": annotated_frame_b64,
        }

        if isSimilar:
            # Pose is within similarity threshold: now check joints
            wrong_joints = PoseSimilarity.get_wrong_joints(
                pose_name,
                correct_landmarks,
                input_landmarks,
                angle_threshold,
            )

            logger.info(
                "Pose evaluated",
                extra={
                    "session_id": session_id,
                    "pose_name": pose_name,
                    "pose_similar": True,
                    "wrong_joint_count": len(wrong_joints),
                },
            )

            if len(wrong_joints) == 0:
                # Completely correct pose
                response["message"] = "You are doing it absolutely right."
                response["wrong_joints"] = []
            else:
                # Some joints need correction: build joint-wise feedback
                items = []
                speak_phrases = []

                for joint_name, (_, change) in wrong_joints.items():
                    joint_words = " ".join(str(joint_name).split("_"))
                    # Capitalize change for nicer speech
                    phrase = f"{change.capitalize()} angle at {joint_words}"
                    speak_phrases.append(phrase)

                    items.append(
                        {
                            "joint": str(joint_name),
                            "change": str(change),
                            "joint_words": joint_words,
                            "speak_text": phrase,
                        }
                    )

                response["wrong_joints"] = items
                # Combine all phrases into one message string
                response["message"] = ". ".join(speak_phrases)
        else:
            # Similarity check failed: overall pose is off
            logger.info(
                "Pose evaluated",
                extra={
                    "session_id": session_id,
                    "pose_name": pose_name,
                    "pose_similar": False,
                },
            )
            response["message"] = "Thoda galat."
            response["wrong_joints"] = []

        return jsonify(response), 200

    except Exception as e:
        logger.error(
            "Error in /analyze_frame: %s",
            str(e),
            extra={"error_type": type(e).__name__},
        )
        return jsonify({"error": "internal server error", "details": str(e)}), 500


def main():
    # Bind host/port from config if you like, otherwise default 0.0.0.0:5000
    host = getattr(config, "host", "0.0.0.0")
    port = getattr(config, "port", 5000)

    logger.info(
        "Starting Flexcellent Flask API",
        extra={"host": host, "port": port, "running_in_docker": RUNNING_IN_DOCKER},
    )

    app.run(host=host, port=port)


if __name__ == "__main__":
    main()
