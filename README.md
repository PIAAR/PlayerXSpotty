# Spotify Virtual Playback Environment

This project is designed to control Spotify playback through the Spotify Web API, enabling advanced automation and playback control on physical or virtual devices (like a headless server running a Spotify Connect device).

## Features
- Start and stop Spotify playback on any connected device.
- Play specific tracks, playlists, or albums using Spotify URIs.
- Enable repeat and shuffle modes programmatically.
- Automate playback on a virtual Spotify Connect device (using `librespot`).

## Requirements
### Spotify Account
- A **Spotify Premium** account is required to use the playback features of the Spotify Web API.

### Authentication
- Generate a **Spotify OAuth Access Token** with the following scopes:
  - `user-modify-playback-state`
  - `user-read-playback-state`
  - `user-read-currently-playing`

## Project Structure
```
spotify-virtual-playback/
│
├── librespot/             # For virtual Spotify Connect device (if needed)
├── scripts/               # Python scripts for API control
├── README.md              # Documentation
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (e.g., Spotify tokens)
├── .gitignore             # Ignore unnecessary files
├── Dockerfile             # Dockerfile for containerization (optional)
└── .github/
    └── workflows/         # For CI/CD workflows (e.g., GitHub Actions)
```

## Getting Started
### Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/spotify-virtual-playback.git
cd spotify-virtual-playback
```

### Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### Set Up Environment Variables
Create a `.env` file to store sensitive information:
```
SPOTIFY_ACCESS_TOKEN=your_access_token
SPOTIFY_DEVICE_ID=your_device_id
```

### Run the Script
Navigate to the `scripts/` directory and execute a script, for example:
```bash
python playback_control.py
```

## Example Usage
Here is an example Python script for starting playback:
```python
import requests

def play_track(device_id, access_token, track_uri):
    url = "https://api.spotify.com/v1/me/player/play"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "uris": [track_uri],
        "device_id": device_id
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 204:
        print("Playback started successfully!")
    else:
        print(f"Failed to start playback: {response.status_code}, {response.json()}")

# Example usage
if __name__ == "__main__":
    device_id = "YOUR_DEVICE_ID"
    access_token = "YOUR_ACCESS_TOKEN"
    track_uri = "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"
    play_track(device_id, access_token, track_uri)
```

## Optional: Virtual Spotify Connect Device
To run Spotify in a virtual environment, set up a headless Spotify Connect device using [librespot](https://github.com/librespot-org/librespot):
1. Install `librespot` on your server or virtual machine.
2. Start the `librespot` service.
3. Use the Spotify Web API to target the `librespot` device for playback.

## Contributing
Feel free to fork this repository and submit pull requests to improve the project.

## License
This project is licensed under the MIT License.
