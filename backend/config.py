from dataclasses import dataclass

@dataclass
class AppConfig:
    # Phase 0 decisions: no storage of PHI, offline pose processing
    store_raw_frames: bool = False     # never write frames to disk
    store_landmarks: bool = False      # never write landmarks to disk
    allow_network: bool = False        # for PHI; gTTS for TTS text is OK

    # Logging level (ELK-friendly)
    log_level: str = "INFO"

config = AppConfig()
