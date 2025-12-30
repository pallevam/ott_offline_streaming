import enum
import json
from dataclasses import dataclass, asdict
from typing import List, Optional

class DownloadStatus(enum.Enum):
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

@dataclass
class ContentMetadata:
    content_id: str
    title: str
    total_duration_sec: int
    total_chunks: int
    file_size_mb: float

@dataclass
class OfflineAsset:
    content_id: str
    local_path: str
    status: DownloadStatus
    downloaded_chunks: List[int]
    license_key: str  # Simulated DRM key
    expiry_timestamp: float # Unix timestamp

    def to_json(self):
        data = asdict(self)
        data['status'] = self.status.value
        return json.dumps(data, indent=4)

    @staticmethod
    def from_json(json_str: str):
        data = json.loads(json_str)
        data['status'] = DownloadStatus(data['status'])
        return OfflineAsset(**data)
