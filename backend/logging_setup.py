# backend/logging_setup.py

import logging
import json
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

LOG_DIR = os.getenv("FLEXCELLENT_LOG_DIR", "/var/log/flexcellent")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")


class JsonFormatter(logging.Formatter):
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
            "pose_similar",
            "no_pose_detected",
            "wrong_joint_count",
            "latency_ms",
            "endpoint",
            "status_code",
            "error_type",
        ]:
            value = getattr(record, key, None)
            if value is not None:
                log_record[key] = value

        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Configure root logger once for the whole app.
    Writes JSON logs to /var/log/flexcellent/app.log
    and also prints to stdout (useful for debugging).
    """
    root = logging.getLogger()

    # Avoid duplicate handlers if called multiple times
    if root.handlers:
        return

    root.setLevel(logging.INFO)

    json_formatter = JsonFormatter()

    # File handler for ELK
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10_000_000,  # 10 MB
        backupCount=5,
    )
    file_handler.setFormatter(json_formatter)
    root.addHandler(file_handler)

    # Optional: also log to console for local debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    root.addHandler(console_handler)
