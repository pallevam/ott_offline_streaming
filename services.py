import os
import time
import random
from typing import List, Optional, Generator
from models import ContentMetadata, OfflineAsset, DownloadStatus

# --- Mock Cloud Service (The Backend) ---
class MockCloudService:
    def __init__(self):
        # Database of available content
        self.library = {
            "movie_001": ContentMetadata(
                content_id="movie_001",
                title="Stranger Things: Demo Edition",
                total_duration_sec=120, # Short for demo
                total_chunks=5,
                file_size_mb=50.0
            ),
            "movie_002": ContentMetadata(
                content_id="movie_002",
                title="The Crown: LLD Special",
                total_duration_sec=100,
                total_chunks=4,
                file_size_mb=40.0
            )
        }

    def get_metadata(self, content_id: str) -> Optional[ContentMetadata]:
        return self.library.get(content_id)

    def acquire_license(self, content_id: str, user_token: str) -> str:
        # Simulate checking user entitlement and returning a DRM license key
        print(f"[Cloud] Validating entitlement for {content_id}...")
        time.sleep(0.5)
        return f"LICENSE_KEY_{content_id}_{random.randint(1000, 9999)}"

    def download_chunk(self, content_id: str, chunk_index: int) -> bytes:
        # Simulate network latency and fetching bytes
        time.sleep(0.2) 
        # Generate dummy video data
        return f"VIDEO_DATA_CHUNK_{chunk_index}_FOR_{content_id}".encode('utf-8')

# --- Storage Manager (Local Disk) ---
class StorageManager:
    def __init__(self, root_dir: str = "downloads"):
        self.root_dir = root_dir
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

    def _get_content_dir(self, content_id: str) -> str:
        path = os.path.join(self.root_dir, content_id)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def save_chunk(self, content_id: str, chunk_index: int, data: bytes):
        content_dir = self._get_content_dir(content_id)
        file_path = os.path.join(content_dir, f"chunk_{chunk_index}.dat")
        # In a real app, we would encrypt 'data' here using the license key before writing
        with open(file_path, "wb") as f:
            f.write(data)

    def load_chunk(self, content_id: str, chunk_index: int) -> bytes:
        content_dir = self._get_content_dir(content_id)
        file_path = os.path.join(content_dir, f"chunk_{chunk_index}.dat")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Chunk {chunk_index} not found for {content_id}")
        
        with open(file_path, "rb") as f:
            return f.read()

    def save_asset_metadata(self, asset: OfflineAsset):
        content_dir = self._get_content_dir(asset.content_id)
        path = os.path.join(content_dir, "metadata.json")
        with open(path, "w") as f:
            f.write(asset.to_json())

    def load_asset_metadata(self, content_id: str) -> Optional[OfflineAsset]:
        path = os.path.join(self.root_dir, content_id, "metadata.json")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return OfflineAsset.from_json(f.read())
    
    def list_offline_items(self) -> List[str]:
        # Returns list of available content_ids
        # Simple implementation: list subdirectories
        return [d for d in os.listdir(self.root_dir) if os.path.isdir(os.path.join(self.root_dir, d))]

# --- Downloader Service (Orchestrator) ---
class DownloaderService:
    def __init__(self, cloud: MockCloudService, storage: StorageManager):
        self.cloud = cloud
        self.storage = storage

    def download_content(self, content_id: str):
        print(f"\n[Downloader] Starting download for {content_id}...")
        metadata = self.cloud.get_metadata(content_id)
        if not metadata:
            print("[Downloader] Content not found in cloud.")
            return

        # 1. Initialize or Load Offline Asset Record
        asset = self.storage.load_asset_metadata(content_id)
        
        if asset:
            print(f"[Downloader] Found existing asset in state: {asset.status.value}")
            if asset.status == DownloadStatus.COMPLETED:
                print("[Downloader] Content already downloaded completely.")
                return
            elif asset.status in [DownloadStatus.DOWNLOADING, DownloadStatus.FAILED]:
                print(f"[Downloader] Resuming download... ({len(asset.downloaded_chunks)}/{metadata.total_chunks} chunks already present)")
        else:
            print("[Downloader] Starting fresh download.")
            license_key = self.cloud.acquire_license(content_id, "user_token_123")
            asset = OfflineAsset(
                content_id=content_id,
                local_path=f"downloads/{content_id}",
                status=DownloadStatus.DOWNLOADING,
                downloaded_chunks=[],
                license_key=license_key,
                expiry_timestamp=time.time() + 172800 # 48 hours validity
            )
            self.storage.save_asset_metadata(asset)

        # 2. Start Downloading Chunks
        try:
            # Identify which chunks are missing
            existing_chunks = set(asset.downloaded_chunks)
            all_chunks = set(range(metadata.total_chunks))
            missing_chunks = sorted(list(all_chunks - existing_chunks))

            for i in missing_chunks:
                print(f"[Downloader] Fetching chunk {i+1}/{metadata.total_chunks}...", end='\r')
                data = self.cloud.download_chunk(content_id, i)
                
                # Verify integrity (hash check) - omitted for demo
                
                self.storage.save_chunk(content_id, i, data)
                asset.downloaded_chunks.append(i)
                
                # Checkpoint saving
                self.storage.save_asset_metadata(asset)
            
            asset.status = DownloadStatus.COMPLETED
            self.storage.save_asset_metadata(asset)
            print(f"\n[Downloader] Download COMPLETE for {content_id}!")

        except Exception as e:
            print(f"\n[Downloader] Failed: {e}")
            asset.status = DownloadStatus.FAILED
            self.storage.save_asset_metadata(asset)
