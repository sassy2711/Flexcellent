import uuid
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PoseSession:
    session_id: str
    pose_name: str
    started_at: datetime

def new_session(pose_name: str) -> PoseSession:
    return PoseSession(
        session_id=str(uuid.uuid4()),
        pose_name=pose_name,
        started_at=datetime.utcnow(),
    )
