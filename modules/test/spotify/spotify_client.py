from modules.main.spotify.spotify_client import SpotifyClient
from modules.main.configs.sparse_configs import SparseConfigs
import modules.main.util.constants as constants
import logging
import random


# Set up logging.
logging.basicConfig(filename='./log/album_ranker.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up client.
configs = SparseConfigs()
client = SpotifyClient(configs=configs)

# Fetch Spotify album.
fetched_album = client.getAlbum("spotify:album:6DEjYFkNZh67HP7R9PSZvv")
logger.debug("Successfully fetched album from Spotify.")

# Add tracks to a Spotify playlist.
test_playlist_uri = "spotify:playlist:7hv2qsuUDSDrsytG0tAJMm"
album_uris = list(map(lambda track: track[constants.URI_KEY], fetched_album[constants.TRACKS_KEY][constants.ITEMS_KEY]))
client.addPlaylistItems(test_playlist_uri, album_uris)
logger.debug("Successfully added tracks to Spotify playlist.")

# Fetch tracks from Spotify playlist.
client.getPlaylistItems(test_playlist_uri)
logger.debug("Successfully fetched album from Spotify.")

# Remove tracks from a Spotify playlist.
random.shuffle(album_uris) # We need to shuffle the tracks so that Spotify lets us delete the added tracks immediately.
client.removePlaylistItems(test_playlist_uri, album_uris)
logger.debug("Successfully removed tracks from Spotify playlist.")