import time
from itertools import batched
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import modules.main.util.constants as C
from modules.main.configs.sparse_configs import SparseConfigs


class SpotifyClient:
    """A class representing a client for interacting with Spotify API using retry logic."""
        
    # The redirect uri for authenticating the Spotify client.
    __redirect_uri = "https://example.com/callback"
    # The scope for the python API. We need modify permissions to remove all tracks from each temp playlist and add them back.
    __scope = "playlist-modify-public"


    def __init__(self, configs: SparseConfigs):
        """
        Initializes an Spotify Client object.

        Args:
            configs (AlbumRankerConfigs): The Album Ranker configs.
        """

        self.__client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=configs.get_client_id(),
            client_secret=configs.get_client_secret(),
            redirect_uri=self.__redirect_uri,
            scope=self.__scope
        ))
        self.__user = configs.get_user()


    def __run_with_retry(
        self, 
        func, 
        param_1: any = None, 
        param_2: any = None, 
        max_retries: int=3, 
        delay_seconds: int=1
    ) -> any:
        """
        Run something with a variable number of times if an exception is encountered.

        Args:
            func (function): The function containing the call to the resource.
            param_1 (any): The first param to pass into `func`.
            param_2 (any): The second param to pass into `func`.
            retries (int): The number of retries before throwing an exception. 2 by default.
            delay_seconds (int): Delay between tries in seconds.
        """

        for attempt in range(max_retries):
            try:
                return func(param_1, param_2)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise  # Re-raise exception on the last attempt
                print(f"Attempt {attempt + 1} failed: {e}, retrying in {delay_seconds} seconds...")
                time.sleep(delay_seconds)


    def getAlbum(self, album_id: str) -> dict:
        """Try to fetch an album using the Spotify client."""
        return self.__run_with_retry(func=self.__client.album, param_1=album_id)


    def getPlaylistItems(self, playlist_id: str) -> dict:
        """Try to fetch the tracks from a playlist using the Spotify client."""
        return self.__run_with_retry(func=self.__client.playlist, param_1=playlist_id)[C.TRACKS_KEY][C.ITEMS_KEY]


    def getTracks(self, track_uris) -> list:
        """Try to fetch tracks using Spotify client."""

        gathered_tracks = []
        for batch in batched(track_uris, 50):
            gathered_tracks.extend(self.__run_with_retry(func=self.__client.tracks, param_1=batch)[C.TRACKS_KEY])
        return gathered_tracks


    def removePlaylistItems(self, playlist_id: str, tracks: list) -> None:
        """Try to remove tracks from a playlist in batches of 100 using the Spotify client."""

        for batch in batched(tracks, 100):
            self.__run_with_retry(
                func=self.__client.playlist_remove_all_occurrences_of_items, 
                param_1=playlist_id, 
                param_2=batch
            )


    def addPlaylistItems(self, playlist_id: str, tracks: list) -> None:
        """Try to add tracks to a playlist in batches of 100 using the Spotify client."""

        for batch in batched(tracks, 100):
            self.__run_with_retry(
                func=self.__client.playlist_add_items,
                param_1=playlist_id, 
                param_2=batch
            )


    def createUserPlaylist(self, playlist_title: str) -> str:
        """Try to create a playlist using the Spotify client."""

        return self.__run_with_retry(
            func=self.__client.user_playlist_create,
            param_1=self.__user,
            param_2=playlist_title
        )['uri']
