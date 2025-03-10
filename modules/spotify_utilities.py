import modules.album_ranker_constants as album_ranker_constants
import math

def getTierKey(tier: int) -> str:
    """Get the key for a tier playlist in memory."""
    return f"tier_{tier}_tracks"

def getArtistNameFromArtist(artist: dict) -> str:
    """Get the artist name from a Spotify artist."""
    return artist[album_ranker_constants.NAME_KEY]

def getArtistNamesFromAlbum(album: dict) -> str:
    """Get the comma-separated list of artist names from a Spotify album."""
    return ', '.join(map(getArtistNameFromArtist, album[album_ranker_constants.ARTISTS_KEY]))

def getScoreFromTrack(track: dict) -> float:
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
    duration_min = track[album_ranker_constants.DURATION_MS_KEY]/1000/60

    if (duration_min < .25):
        return 0
    elif (duration_min < 1.5):
        return 0.5
    elif (duration_min > 6):
        return math.floor(duration_min/6) + 1
    else:
        return 1

def getNameFromTrack(track: dict) -> str:
    """Get the track name from a Spotify track."""
    return track[album_ranker_constants.NAME_KEY]

def getTrackNamesFromAlbum(album_tracks: list) -> list:
    """Get the track names from all of the tracks in a Spotify album."""
    return list(map(getNameFromTrack, album_tracks))

def getAlbumHighestPossibleScore(album_tracks: list) -> float:
    """
    Get the highest possible score for this album given the length of each track.
    
    Args:
        album_tracks (dict): The album tracks.

    Returns:
        float: The highest possible score this album could achieve based on the length of its tracks.
    """

    # Get the highest possible score for a single tier.
    single_tier_score = 0
    for track in album_tracks:
        single_tier_score += getScoreFromTrack(track)

    # We need to multiply this score by 3 since there are 3 tiers.
    highest_score = single_tier_score * 3

    return highest_score