import time
from services import StorageManager
from models import DownloadStatus

class OfflinePlayer:
    def __init__(self, storage: StorageManager):
        self.storage = storage

    def play(self, content_id: str):
        print(f"\n[Player] Attempting to play {content_id} in OFFLINE mode...")

        # 1. Load Metadata & Verify License
        asset = self.storage.load_asset_metadata(content_id)
        if not asset:
            print("[Player] Error: Content not found on disk.")
            return

        if asset.status != DownloadStatus.COMPLETED:
            print("[Player] Error: Download is incomplete. Cannot play.")
            return

        if time.time() > asset.expiry_timestamp:
            print("[Player] Error: License expired. Please go online to renew.")
            return

        print(f"[Player] License Valid. Key: {asset.license_key}")
        print("[Player] Starting Playback...")
        print("-" * 40)

        # 2. Streaming Loop simulation
        chunk_indices = sorted(asset.downloaded_chunks)
        for idx in chunk_indices:
            try:
                # Retrieve encrypted chunk
                raw_data = self.storage.load_chunk(content_id, idx)
                
                # Decrypt (Simulated)
                decrypted_frame = self._decrypt_chunk(raw_data, asset.license_key)
                
                # Render (Simulated)
                self._render_frame(decrypted_frame)
                
            except Exception as e:
                print(f"[Player] Playback Error at chunk {idx}: {e}")
                break
        
        print("\n" + "-" * 40)
        print("[Player] Playback Finished.")

    def _decrypt_chunk(self, encrypted_data: bytes, key: str) -> str:
        # In reality, this uses AES with the key.
        # Here we just decode the dummy bytes.
        return encrypted_data.decode('utf-8')

    def _render_frame(self, frame_data: str):
        # Simulate video rendering time
        time.sleep(0.5) 
        print(f" > RENDERED: {frame_data}")
