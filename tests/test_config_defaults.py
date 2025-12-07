#test file
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.config import config

def test_config_defaults_enforce_no_storage():
    assert config.store_raw_frames is False
    assert config.store_landmarks is False
    assert config.allow_network is False
