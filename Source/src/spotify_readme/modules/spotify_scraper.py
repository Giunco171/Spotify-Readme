import json
import re
from typing import TypedDict

import requests
from spotify_readme.modules.paths import PATHS
from spotify_scraper import SpotifyClient


class TrackDetails(TypedDict):
    name: str
    first_artist: str
    cover_art_url: str
    uri: str


class SpotifyScraper:
    cache_file = PATHS.SRC_DIRECTORY / "spotify_readme" / "data" / "cache.json"

    @classmethod
    def read_cache(cls) -> dict[str, TrackDetails]:
        if not cls.cache_file.exists():
            cls.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cls.cache_file.write_text("{}")
            return {}

        try:
            with open(cls.cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            cls.cache_file.write_text("{}")
            return {}

    @classmethod
    def get_fallback_cover_art(cls, track_id: str) -> str:
        oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/track/{track_id}"
        response = requests.get(
            oembed_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )

        if response.status_code == 200:
            oembed_response = response.json()
            return oembed_response.get("thumbnail_url")

        return ""

    @classmethod
    def sanitize_spotify_image_url(cls, url: str) -> str:
        if not url:
            return ""

        # Extract the 40-character hex hash from the end of the URL
        match = re.search(r"/image/([a-f0-9]{40})", url)
        if match:
            image_hash = match.group(1)
            # i.scdn.co is whitelisted on PythonAnywhere
            return f"https://i.scdn.co/image/{image_hash}"

        return url

    @classmethod
    def get_track(cls, track_id: str) -> TrackDetails:
        cache = cls.read_cache()

        if track_details := cache.get(track_id):
            return track_details

        with SpotifyClient() as client:
            track = client.get_track(track_id)

            first_artist = track.artists[0].name if track.artists else "Unknown Artist"
            cover_url = (
                track.album.images[0].url
                if (track.album and track.album.images)
                else cls.get_fallback_cover_art(track_id)
            )

            track_details: TrackDetails = {
                "name": track.name,
                "first_artist": first_artist,
                "cover_art_url": cls.sanitize_spotify_image_url(cover_url),
                "uri": track.uri,
            }

            cache[track_id] = track_details

            with open(cls.cache_file, "w") as f:
                json.dump(cache, f, indent=4)

            return track_details
