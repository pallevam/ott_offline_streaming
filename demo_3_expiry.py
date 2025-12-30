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
    print("=== OTT Offline Simulation: License Expiry ===")
    clean_env()
    
    # Setup
    cloud = MockCloudService()
    storage = StorageManager()
    downloader = DownloaderService(cloud, storage)
    player = OfflinePlayer(storage)
    cid = "movie_002" # Shorter one
    
    # 1. Download
    print(f"\n[Step 1] Downloading {cid}...")
    downloader.download_content(cid)
    
    # 2. Play (Should work)
    print("\n[Step 2] Playing immediately (Valid License)...")
    player.play(cid)
    
    # 3. Tamper with license expiry
    print("\n[Step 3] Simulating License Expiry (Fast forward 48h)...")
    asset = storage.load_asset_metadata(cid)
    asset.expiry_timestamp = time.time() - 3600 # Expired 1 hour ago
    storage.save_asset_metadata(asset)
    
    # 4. Play (Should fail)
    print("\n[Step 4] Attempting to play expired content...")
    player.play(cid)

if __name__ == "__main__":
    run()
