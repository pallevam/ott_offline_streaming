# OTT Offline Streaming Simulator

A hands-on simulator that models how modern OTT streaming platforms implement Download & Watch Later functionality.

This project demonstrates, end-to-end, what happens under the hood when a user downloads content for offline viewing:
- Content Discovery
- DRM / Licensing
- Chunk-based Downloading
- Offline Storage Management
- Playback & Decryption

## Project Structure
- `models.py`: Data models (Asset, Metadata).
- `services.py`: Core services (Cloud Mock, Downloader, Storage).
- `player.py`: Offline Player simulator.

## Running the Simulations

We have prepared three scripts to demonstrate different scenarios:

### 1. Basic Download & Play
Run a full successful flow of downloading a movie and playing it.
```bash
python3 demo_1_basic.py
```

### 2. Resume Capability
Simulate a network failure during download and verify that the downloader resumes from the last chunk instead of restarting.
```bash
python3 demo_2_resume.py
```

### 3. License Expiry
Simulate a DRM license expiring and the player enforcing the need to renew.
```bash
python3 demo_3_expiry.py
```
