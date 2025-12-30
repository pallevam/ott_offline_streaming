import time
import os
import shutil
from services import MockCloudService, StorageManager, DownloaderService
from player import OfflinePlayer

def clean_env():
    if os.path.exists("downloads"):
        shutil.rmtree("downloads")
    print("Environment cleaned.")

def run():
    print("=== OTT Offline Simulation: Full Flow ===")
    clean_env()
    
    cloud = MockCloudService()
    storage = StorageManager()
    downloader = DownloaderService(cloud, storage)
    player = OfflinePlayer(storage)
    
    # 1. Discover
    print("\n[Step 1] Content Discovery")
    cid = "movie_001"
    meta = cloud.get_metadata(cid)
    print(f"Found: {meta.title} (Duration: {meta.total_duration_sec}s, Size: {meta.file_size_mb} MB)")
    
    # 2. Download
    print(f"\n[Step 2] Downloading {cid}...")
    downloader.download_content(cid)
    
    # 3. Play
    print(f"\n[Step 3] Playing {cid}...")
    player.play(cid)

if __name__ == "__main__":
    run()
