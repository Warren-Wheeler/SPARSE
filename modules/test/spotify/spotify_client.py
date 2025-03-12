from modules.main.spotify.spotify_client import SpotifyClient
from modules.main.configs.sparse_configs import SparseConfigs
import modules.main.util.constants as C
import random


# Set up client.
configs = SparseConfigs()
client = SpotifyClient(configs=configs)

# Fetch Spotify album.
fetched_album = client.getAlbum("spotify:album:6DEjYFkNZh67HP7R9PSZvv")
print("Successfully fetched album from Spotify.")

# Add tracks to a Spotify playlist.
test_playlist_uri = "spotify:playlist:7hv2qsuUDSDrsytG0tAJMm"
album_uris = list(map(lambda track: track[C.URI_KEY], fetched_album[C.TRACKS_KEY][C.ITEMS_KEY]))
client.addPlaylistItems(test_playlist_uri, album_uris)
print("Successfully added tracks to Spotify playlist.")

# Fetch tracks from Spotify playlist.
tracks = client.getPlaylistItems(test_playlist_uri)
print("Successfully fetched playlist items from Spotify.")

# Fetch tracks from Spotify.
track_uris = list(map(lambda track: track[C.TRACK_KEY][C.URI_KEY], tracks))
client.getTracks(track_uris)
print("Successfully fetched tracks from Spotify.")

# Remove tracks from a Spotify playlist.
random.shuffle(album_uris) # We need to shuffle the tracks so that Spotify lets us delete the added tracks immediately.
client.removePlaylistItems(test_playlist_uri, album_uris)
print("Successfully removed tracks from Spotify playlist.")