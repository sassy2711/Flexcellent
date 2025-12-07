import logging
import sys
import json
from datetime import datetime

from .config import config



class NoPHIFilter(logging.Filter):
    """
    Prevent obvious attempts to log frames/landmarks/images.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.getMessage()).lower()
        banned = ["frame=", "landmarks=", "image="]
        if any(b in msg for b in banned):
            record.msg = "[REDACTED_PHI_ATTEMPTED_LOG]"
        return True


class JSONFormatter(logging.Formatter):
    """
    Simple JSON formatter so ELK can parse fields easily.
    """

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach safe extras (e.g., session_id, pose_name)
        for key, value in record.__dict__.items():
            if key.startswith("_"):
                continue
            if key in log:
                continue
            # avoid dumping giant/binary payloads accidentally
            if isinstance(value, (bytes, bytearray)):
                log[key] = "[BINARY_DATA_REDACTED]"
            else:
                log[key] = value

        return json.dumps(log)


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(config.log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    handler.addFilter(NoPHIFilter())

    root.handlers.clear()
    root.addHandler(handler)
