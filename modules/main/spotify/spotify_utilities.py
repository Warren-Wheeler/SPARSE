import modules.main.util.constants as C
import math
import sys


class SparsePlaylistTierException(Exception):
    """An exception that is thrown when there is an invalid playlist tier."""
    pass


class SparseURIException(Exception):
    """An exception that is thrown when there is an invalid Spotify URI."""
    pass

class SparseReturnDataException(Exception):
    """An exception that is thrown when a dict returned from Spotify API has an unexpected format."""
    pass


def is_valid_tier(tier: int) -> bool:
    """Returns true if the tier is 1, 2 or 3."""
    return 3 >= tier >= 1


def get_track_key(name: str, tier: int) -> str:
    """
    Get the track key for a Spotify track at a certain tier. Throws a SparsePlaylistTierException if the album tier is not 1, 2 or 3.
    
    Returns:
        str: The track key formatted as: "<TRACK_NAME>_<TIER>"
    """

    if not name:
        raise SparsePlaylistTierException("Tried to add a track with no name to tier {tier}.")
    if not is_valid_tier(tier):
        raise SparsePlaylistTierException("Tried to add {name} to tier {tier}, but playlist tiers can only be `1`, `2` or `3`.")
    
    return f"{name}_{tier}"


def get_tier_key(tier: int) -> str:
    """Get the key for a tier playlist in memory. Throws a SparsePlaylistTierException if the album tier is not 1, 2 or 3."""

    if not is_valid_tier(tier):
        raise SparsePlaylistTierException(
            "Tried to get the tier key for invalid tier {tier}. Playlist tiers can only be `1`, `2` or `3`."
        )
    
    return f"tier_{tier}_tracks"


def get_artist_name(spotify_artist: dict) -> str:
    """
    Get the artist name from a Spotify artist.
    Throws SparseReturnDataException if it could not be found.
    """

    try:
        return spotify_artist[C.NAME_KEY]
    except KeyError as e:
        tb = sys.exception().__traceback__
        raise SparseReturnDataException(e.with_traceback(tb))


def get_album_artist_names(spotify_album: dict) -> str:
    """
    Get the comma-separated list of artist names from a Spotify album.
    Throws SparseReturnDataException if it could not be found.
    """

    try:
        return ', '.join(map(get_artist_name, spotify_album[C.ARTISTS_KEY]))
    except KeyError as e:
        tb = sys.exception().__traceback__
        raise SparseReturnDataException(e.with_traceback(tb))


def get_track_score(spotify_track: dict) -> float:
    """
    Get the score of a track based on its length. Scoring is determined based on the track length:
        length < 15 seconds                 => 0
        15 seconds <= length < 90 seconds   => 0.5
        90 seconds <= length <= 6 minutes   => 1
        length > 6 minutes                  => 1 + (1 for every 6 minutes)
    
    Args:
        track (dict): The Spotify track.

    Returns:
        float: The track score.
    """

    try:
        duration_min = spotify_track[C.DURATION_MS_KEY]/1000/60
    except KeyError as e:
        tb = sys.exception().__traceback__
        raise SparseReturnDataException(e.with_traceback(tb))

    if (duration_min < .25):
        return 0
    elif (duration_min < 1.5):
        return 0.5
    elif (duration_min > 6):
        return math.floor(duration_min/6) + 1
    else:
        return 1


def get_track_name(spotify_track: dict) -> str:
    """Get the track name from a Spotify track. Throws SparseReturnDataException if it could not be found."""

    try:
        return spotify_track[C.NAME_KEY]
    except KeyError as e:
        tb = sys.exception().__traceback__
        raise SparseReturnDataException(e.with_traceback(tb))


def get_track_names(spotify_album_tracks: list) -> list:
    """
    Get the track names from all of the tracks in a Spotify album. 
    Throws SparseReturnDataException if they could not be found.
    """

    try:
        return list(map(get_track_name, spotify_album_tracks))
    except KeyError as e:
        tb = sys.exception().__traceback__
        raise SparseReturnDataException(e.with_traceback(tb))


def get_tracks(spotify_album: dict) -> list:
    """
    Get the list of tracks from a Spotify album.
    Throws SparseReturnDataException if they could not be found.
    """
    
    try:
        return spotify_album[C.TRACKS_KEY][C.ITEMS_KEY]
    except KeyError as e:
        tb = sys.exception().__traceback__
        raise SparseReturnDataException(e.with_traceback(tb))


def get_album_highest_possible_score(spotify_album_tracks: list) -> float:
    """
    Get the highest possible score for this album given the length of each track.
    
    Args:
        spotify_album_tracks (dict): The Spotify album tracks.

    Returns:
        float: The highest possible score this album could achieve based on the length of its tracks.
    """

    # Get the highest possible score for a single tier.
    single_tier_score = 0
    for track in spotify_album_tracks:
        single_tier_score += get_track_score(track)

    # We need to multiply this score by 3 since there are 3 tiers.
    highest_score = single_tier_score * 3

    return highest_score


def get_album_uri_from_share_link(share_link: str):
    """Get the Spotify album URI from a share link. Returns the share link if it was already a URI."""

    if not share_link.startswith(C.SPOTIFY_ALBUM_URI_PREFIX):
        # Get album code.
        album_code = share_link.split(C.QUESTION_MARK)[0].split(C.SLASH)[-1]

        # Return uri.
        return f"{C.SPOTIFY_ALBUM_URI_PREFIX}{album_code}"
    else:
        return share_link
