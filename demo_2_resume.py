import time
import os
import shutil
from services import MockCloudService, StorageManager, DownloaderService, DownloadStatus
from player import OfflinePlayer

class FlakyCloudService(MockCloudService):
    def __init__(self, fail_at_chunk):
        super().__init__()
        self.fail_at_chunk = fail_at_chunk
    
    def download_chunk(self, content_id: str, chunk_index: int) -> bytes:
        if chunk_index == self.fail_at_chunk:
            print(f"\n[Cloud] Simulating connection drop at chunk {chunk_index}!")
            raise ConnectionError("Simulated Network Failure!")
        return super().download_chunk(content_id, chunk_index)

def clean_env():
    if os.path.exists("downloads"):
        shutil.rmtree("downloads")
    print("Environment cleaned.")

def run():
    print("=== OTT Offline Simulation: Interruption & Resume ===")
    clean_env()
    
    # Setup
    flaky_cloud = FlakyCloudService(fail_at_chunk=2) # Fail on 3rd chunk (0, 1, *2*)
    cloud = MockCloudService()
    storage = StorageManager()
    
    downloader_flaky = DownloaderService(flaky_cloud, storage)
    downloader_stable = DownloaderService(cloud, storage)
    player = OfflinePlayer(storage)
    
    cid = "movie_001"
    
    # 1. Start Download (Expected to fail)
    print(f"\n[Step 1] Starting download (Simulating failure)...")
    downloader_flaky.download_content(cid)
    
    # Verify it failed
    asset = storage.load_asset_metadata(cid)
    if asset:
        print(f"\n[Status Check] Asset Status: {asset.status}")
        print(f"[Status Check] Downloaded Chunks: {asset.downloaded_chunks}")
    
    time.sleep(1)

    # 2. Resume Download
    print(f"\n[Step 2] Resuming download with stable connection...")
    downloader_stable.download_content(cid)
    
    # Verify completion
    asset = storage.load_asset_metadata(cid)
    if asset:
        print(f"\n[Status Check] Asset Status: {asset.status}")
        print(f"[Status Check] Downloaded Chunks: sorted({sorted(asset.downloaded_chunks)})")

    # 3. Play to confirm integrity
    print(f"\n[Step 3] Playing content to verify integrity...")
    player.play(cid)

if __name__ == "__main__":
    run()
