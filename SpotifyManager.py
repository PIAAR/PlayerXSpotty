import requests
import json
import asyncio
import random
import subprocess

class SpotifyPodcastFetcher:
    def __init__(self, credentials_file="credentials.json"):
        """
        Initialize the SpotifyPodcastFetcher.

        :param credentials_file: Path to the credentials file.
        """
        self.credentials_file = credentials_file
        self.base_url = "https://api.spotify.com/v1"
        self.client_id, self.client_secret, self.podcast_id, self.episode_ids, self.device_id = self.load_client_credentials()
        self.access_token = self.get_access_token()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def load_client_credentials(self):
        """
        Load client ID, client secret, podcast ID, episode IDs, and device ID from the credentials file.

        :return: A tuple of client ID, client secret, podcast ID, episode IDs, and device ID.
        """
        try:
            with open(self.credentials_file, 'r') as file:
                credentials = json.load(file)
                client_id = credentials.get("spotify", {}).get("client_id")
                client_secret = credentials.get("spotify", {}).get("client_secret")
                podcast_id = credentials.get("spotify", {}).get("podcast_id")
                episode_ids = credentials.get("spotify", {}).get("episode_ids", [])
                device_id = credentials.get("spotify", {}).get("device_id")
                if client_id and client_secret and podcast_id and episode_ids and device_id:
                    return client_id, client_secret, podcast_id, episode_ids, device_id
                else:
                    raise ValueError("Missing required fields in credentials file.")
        except (FileNotFoundError, json.JSONDecodeError):
            raise FileNotFoundError("Credentials file not found or invalid JSON format.")

    def get_access_token(self):
        """
        Retrieve a valid access token from the credentials file.
        """
        try:
            with open(self.credentials_file, 'r') as file:
                credentials = json.load(file)
                access_token = credentials.get("spotify", {}).get("access_token")
                if access_token and self.is_token_valid(access_token):
                    return access_token
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise FileNotFoundError(
                "Credentials file not found or invalid JSON format."
            ) from e
        # Request a new token
        return self.request_new_token()

    def is_token_valid(self, token):
        """
        Check if the access token is valid by making a simple API call.

        :param token: The access token to validate.
        :return: True if the token is valid, False otherwise.
        """
        url = f"{self.base_url}/me"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        return response.status_code == 200

    def request_new_token(self):
        """
        Request a new access token using the client credentials flow and update the credentials file.

        :return: The new access token.
        """
        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, headers=headers, data=data)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch access token: {response.status_code}, {response.json()}")
        access_token = response.json().get("access_token")
        self.update_credentials_file(access_token)
        return access_token

    def update_credentials_file(self, access_token):
        """
        Update the credentials file with the new access token.

        :param access_token: The new access token to store.
        """
        try:
            with open(self.credentials_file, 'r') as file:
                credentials = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            credentials = {}

        credentials.setdefault("spotify", {})["access_token"] = access_token

        with open(self.credentials_file, 'w') as file:
            json.dump(credentials, file, indent=4)

    def is_enabled(self):
        """
        Check if the playback system is enabled in the credentials file.
        """
        try:
            with open(self.credentials_file, 'r') as file:
                credentials = json.load(file)
                return credentials.get("spotify", {}).get("enabled", False)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: Could not read the credentials file.")
            return False

    def start_librespot(self):
        """
        Start the Librespot process using the pipe backend.
        """
        command = [
            "./target/release/librespot",
            "--name", "AutomationMgrDevice",
            "--token", self.access_token,
            "--backend", "pipe",
            "--device", "/dev/null"
        ]
        try:
            process = subprocess.Popen(command)
            print("Librespot process started with PID:", process.pid)
        except FileNotFoundError:
            print("Error: Librespot binary not found.")

    async def play_episode(self, episode_id, semaphore):
        """
        Play a specific Spotify episode by ID.

        :param episode_id: Spotify episode ID.
        :param semaphore: Async semaphore to control concurrency.
        """
        async with semaphore:
            url = f"{self.base_url}/me/player/play"
            data = {
                "uris": [f"spotify:episode:{episode_id}"],
                "device_id": self.device_id
            }

            response = requests.put(url, headers=self.headers, json=data)
            if response.status_code == 204:
                print(f"Playing episode: {episode_id}")
                await asyncio.sleep(5)  # Simulate playback duration
                print(f"Finished playing: {episode_id}")
            else:
                print(f"Failed to play {episode_id}: {response.json()}")

    async def play_randomly(self, max_concurrent=5):
        """
        Play episodes in random order repeatedly.

        :param max_concurrent: Maximum number of concurrent playback tasks.
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        while True:
            if not self.is_enabled():
                print("Playback is disabled. Exiting.")
                break

            random.shuffle(self.episode_ids)
            tasks = [self.play_episode(episode_id, semaphore) for episode_id in self.episode_ids]
            await asyncio.gather(*tasks)

    def print_episode_list(self):
        """
        Print the list of episode IDs from the credentials.
        """
        print("Configured episode IDs:")
        for episode_id in self.episode_ids:
            print(f"- {episode_id}")

# Example usage
if __name__ == "__main__":
    # Create an instance of SpotifyPodcastFetcher
    showman = SpotifyPodcastFetcher()

    # Print configured episode IDs
    showman.print_episode_list()

    # Start Librespot process
    showman.start_librespot()

    # Play episodes asynchronously in random order
    try:
        asyncio.run(showman.play_randomly())
    except KeyboardInterrupt:
        print("\nPlayback stopped.")
