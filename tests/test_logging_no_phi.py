import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.logging_setup import JSONFormatter, NoPHIFilter
from backend.config import config
import logging
import json
from io import StringIO


def capture_logs(log_func):
    """
    Utility to capture logs written to a temporary StreamHandler.
    """
    logger = logging.getLogger("test_logger")
    logger.setLevel(config.log_level)

    stream = StringIO()
    handler = logging.StreamHandler(stream)
    from backend.logging_setup import JSONFormatter, NoPHIFilter  # reuse your classes
    handler.setFormatter(JSONFormatter())
    handler.addFilter(NoPHIFilter())

    logger.handlers.clear()
    logger.addHandler(handler)

    log_func(logger)

    logger.removeHandler(handler)
    stream.seek(0)
    lines = stream.read().strip().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def test_logging_redacts_landmarks_keyword():
    def do_log(logger):
        logger.info("landmarks= [0.1, 0.2, 0.3]")

    records = capture_logs(do_log)
    assert len(records) == 1
    assert records[0]["message"] == "[REDACTED_PHI_ATTEMPTED_LOG]"


def test_logging_allows_safe_metadata():
    def do_log(logger):
        logger.info("Pose evaluated", extra={"pose_name": "pranamasana", "pose_similar": True})

    records = capture_logs(do_log)
    assert len(records) == 1
    rec = records[0]
    assert rec["message"] == "Pose evaluated"
    assert rec["pose_name"] == "pranamasana"
    assert rec["pose_similar"] is True
