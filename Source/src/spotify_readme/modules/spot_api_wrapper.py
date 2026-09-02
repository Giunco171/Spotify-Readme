import json
import sys
from collections.abc import Mapping
from typing import Any, TypedDict
from unittest.mock import MagicMock

from spotify_readme.modules.paths import PATHS

"""
`spotapi` requires `redis` and `pymongo`, but they aren't needed for this script.
The following lines are used to avoid import errors from not installing them.
"""
sys.modules["pymongo"] = MagicMock()
sys.modules["redis"] = MagicMock()

from spotapi import Song


class TrackDetails(TypedDict):
    name: str
    first_artist: str
    cover_art_url: str
    uri: str


class SpotApiWrapper:
    cache_file = PATHS.SRC_DIRECTORY / "spotify_readme" / "data" / "cache.json"

    @classmethod
    def read_cache(cls) -> dict[str, TrackDetails]:
        if not cls.cache_file.exists():
            cls.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cls.cache_file.touch()
            cls.cache_file.write_text("{}")
        with open(cls.cache_file, "r") as f:
            cache: dict[str, TrackDetails] = json.load(f)
            return cache

    @classmethod
    def get_track(cls, track_id: str) -> TrackDetails:
        cache: dict[str, TrackDetails] = cls.read_cache()

        if track_details := cache.get(track_id):
            return track_details

        song: Song = Song()
        track: Mapping[str, Any()] = song.get_track_info(track_id)
        track_data: dict = track["data"]["trackUnion"]

        name = track_data["name"]
        first_artist = track_data["firstArtist"]["items"][0]["profile"]["name"]

        track_images = track_data["albumOfTrack"]["coverArt"]["sources"]
        source = next(source for source in track_images if source["width"] == 640)
        cover_art_url = source["url"]

        uri = track_data["uri"]

        track_details: TrackDetails = {
            "name": name,
            "first_artist": first_artist,
            "cover_art_url": cover_art_url,
            "uri": uri,
        }

        cache[track_id] = track_details

        with open(cls.cache_file, "w") as f:
            json.dump(cache, f)

        return track_details
