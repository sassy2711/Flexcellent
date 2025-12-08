# # # backend/logging_setup.py

# # import logging
# # import json
# # import os
# # from logging.handlers import RotatingFileHandler
# # from datetime import datetime

# # LOG_DIR = os.getenv("FLEXCELLENT_LOG_DIR", "/var/log/flexcellent")
# # os.makedirs(LOG_DIR, exist_ok=True)
# # LOG_FILE = os.path.join(LOG_DIR, "app.log")


# # class JsonFormatter(logging.Formatter):
# #     """
# #     Format log records as a single-line JSON object.
# #     Extra fields passed via logger.xxx(..., extra={...}) are included.
# #     """

# #     def format(self, record: logging.LogRecord) -> str:
# #         log_record = {
# #             "timestamp": datetime.utcnow().isoformat() + "Z",
# #             "level": record.levelname,
# #             "logger": record.name,
# #             "message": record.getMessage(),
# #         }

# #         # Pull interesting fields from record.__dict__ if present
# #         for key in [
# #             "session_id",
# #             "pose_name",
# #             "pose_similar",
# #             "no_pose_detected",
# #             "wrong_joint_count",
# #             "latency_ms",
# #             "endpoint",
# #             "status_code",
# #             "error_type",
# #         ]:
# #             value = getattr(record, key, None)
# #             if value is not None:
# #                 log_record[key] = value

# #         return json.dumps(log_record)


# # def setup_logging() -> None:
# #     """
# #     Configure root logger once for the whole app.
# #     Writes JSON logs to /var/log/flexcellent/app.log
# #     and also prints to stdout (useful for debugging).
# #     """
# #     root = logging.getLogger()

# #     # Avoid duplicate handlers if called multiple times
# #     if root.handlers:
# #         return

# #     root.setLevel(logging.INFO)

# #     json_formatter = JsonFormatter()

# #     # File handler for ELK
# #     file_handler = RotatingFileHandler(
# #         LOG_FILE,
# #         maxBytes=10_000_000,  # 10 MB
# #         backupCount=5,
# #     )
# #     file_handler.setFormatter(json_formatter)
# #     root.addHandler(file_handler)

# #     # Optional: also log to console for local debugging
# #     console_handler = logging.StreamHandler()
# #     console_handler.setFormatter(json_formatter)
# #     root.addHandler(console_handler)


# # backend/logging_setup.py

# import logging
# import json
# import os
# from logging.handlers import RotatingFileHandler
# from datetime import datetime

# LOG_DIR = os.getenv("FLEXCELLENT_LOG_DIR", "/var/log/flexcellent")
# os.makedirs(LOG_DIR, exist_ok=True)
# LOG_FILE = os.path.join(LOG_DIR, "app.log")


# class JSONFormatter(logging.Formatter):
#     """
#     Format log records as a single-line JSON object.
#     Extra fields passed via logger.xxx(..., extra={...}) are included.
#     """

#     def format(self, record: logging.LogRecord) -> str:
#         log_record = {
#             "timestamp": datetime.utcnow().isoformat() + "Z",
#             "level": record.levelname,
#             "logger": record.name,
#             "message": record.getMessage(),
#         }

#         # Pull interesting fields from record.__dict__ if present
#         for key in [
#             "session_id",
#             "pose_name",
#             "pose_similar",
#             "no_pose_detected",
#             "wrong_joint_count",
#             "latency_ms",
#             "endpoint",
#             "status_code",
#             "error_type",
#         ]:
#             value = getattr(record, key, None)
#             if value is not None:
#                 log_record[key] = value

#         return json.dumps(log_record)


# class NoPHIFilter(logging.Filter):
#     """
#     Filter that redacts PHI-like content from logs.

#     Current rule for tests:
#     - If the message contains 'landmarks=', replace it entirely with
#       '[REDACTED_PHI_ATTEMPTED_LOG]'.
#     """

#     def filter(self, record: logging.LogRecord) -> bool:
#         msg = record.getMessage()
#         if "landmarks=" in msg:
#             record.msg = "[REDACTED_PHI_ATTEMPTED_LOG]"
#             record.args = ()
#         # Always keep the record; just maybe modified
#         return True


# def setup_logging() -> None:
#     """
#     Configure root logger once for the whole app.
#     Writes JSON logs to /var/log/flexcellent/app.log
#     and also prints to stdout (useful for debugging).
#     Applies NoPHIFilter to avoid logging PHI-like content.
#     """
#     root = logging.getLogger()

#     # Avoid duplicate handlers if called multiple times
#     if root.handlers:
#         return

#     root.setLevel(logging.INFO)

#     json_formatter = JSONFormatter()
#     phi_filter = NoPHIFilter()

#     # File handler for ELK
#     file_handler = RotatingFileHandler(
#         LOG_FILE,
#         maxBytes=10_000_000,  # 10 MB
#         backupCount=5,
#     )
#     file_handler.setFormatter(json_formatter)
#     file_handler.addFilter(phi_filter)
#     root.addHandler(file_handler)

#     # Also log to console for local debugging
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(json_formatter)
#     console_handler.addFilter(phi_filter)
#     root.addHandler(console_handler)

# backend/logging_setup.py

import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = os.getenv("FLEXCELLENT_LOG_DIR", "/var/log/flexcellent")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")


class JSONFormatter(logging.Formatter):
    """
    Format log records as a single-line JSON object.
    Extra fields passed via logger.xxx(..., extra={...}) are included.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Pull interesting fields from record.__dict__ if present
        for key in [
            "session_id",
            "pose_name",
            "pose_result",         # NEW: CORRECT / PARTIALLY_CORRECT / INCORRECT / NO_POSE
            "pose_similar",
            "no_pose_detected",
            "wrong_joint_count",
            "wrong_joint_names",   # NEW: list of joints that were wrong
            "latency_ms",
            "endpoint",
            "status_code",
            "error_type",
            "mediapipe_version",   # NEW (for MLOps observability)
            "model_name",
            "model_version",
        ]:
            value = getattr(record, key, None)
            if value is not None:
                log_record[key] = value

        return json.dumps(log_record)


class NoPHIFilter(logging.Filter):
    """
    Filter that redacts PHI-like content from logs.

    Current rule:
    - If the message contains 'landmarks=', replace it entirely with
      '[REDACTED_PHI_ATTEMPTED_LOG]'.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "landmarks=" in msg:
            record.msg = "[REDACTED_PHI_ATTEMPTED_LOG]"
            record.args = ()
        # Always keep the record; just maybe modified
        return True


def setup_logging() -> None:
    """
    Configure root logger once for the whole app.
    Writes JSON logs to /var/log/flexcellent/app.log
    and also prints to stdout (for ELK + local debugging).
    Applies NoPHIFilter to avoid logging PHI-like content.
    """
    root = logging.getLogger()

    # Avoid duplicate handlers if called multiple times
    if root.handlers:
        return

    root.setLevel(logging.INFO)

    json_formatter = JSONFormatter()
    phi_filter = NoPHIFilter()

    # File handler for ELK
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10_000_000,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(phi_filter)
    root.addHandler(file_handler)

    # Also log to console for local debugging / Kubernetes stdout
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(phi_filter)
    root.addHandler(console_handler)
