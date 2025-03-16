import modules.main.util.constants as C
from modules.main.configs.sparse_configs_validation import validate
import modules.main.util.utilities as utilities
import json


class SparseConfigs:
    """
    A class representing an Album Ranker configs.

    Attributes:
        config_file (str): The path to the configs JSON file.
    """
    

    def __init__(self, configs_file_path: str = "./config.json"):
        """
        Initializes the Album Ranker configs.

        Args:
            configs_file_path (str): The path to the configs file. Should be JSON format.
        """

        # Fetch and validate configs.
        configs = self.__get_configs_from_file(configs_file_path=configs_file_path)
        validate(configs, configs_file_path=configs_file_path)

        # Store configs in memory.
        self.__album_length_threshold_min = configs[C.ALBUM_LENGTH_THRESHOLD_MIN_KEY]
        self.__client_id = configs[C.CLIENT_ID_KEY]
        self.__client_secret = configs[C.CLIENT_SECRET_KEY]
        self.__genre_playlists_file_path = configs[C.GENRE_PLAYLISTS_FILE_PATH_KEY]
        self.__genre_playlists_by_name = utilities.read_json_file(file_path=configs[C.GENRE_PLAYLISTS_FILE_PATH_KEY])
        self.__ranked_album_genres_file_path = configs[C.RANKED_ALBUM_GENRES_FILE_PATH_KEY]
        self.__ranked_album_genres_by_album_key = utilities.read_json_file(file_path=configs[C.RANKED_ALBUM_GENRES_FILE_PATH_KEY])
        self.__ranker_overrides_file_path = configs[C.RANKER_OVERRIDE_FILE_PATH_KEY]
        self.__ranker_overrides = utilities.read_json_file(file_path=configs[C.RANKER_OVERRIDE_FILE_PATH_KEY])
        self.__ranker_output_path = configs[C.RANKER_OUTPUT_FILE_PATH_KEY]
        self.__tier_1_playlist_id = configs[C.TIER_1_PLAYLIST_ID_KEY]
        self.__tier_2_playlist_id = configs[C.TIER_2_PLAYLIST_ID_KEY]
        self.__tier_3_playlist_id = configs[C.TIER_3_PLAYLIST_ID_KEY]
        self.__tier_3_yearly_threshold = configs[C.TIER_3_YEARLY_THRESHOLD_KEY]
        self.__user = configs[C.USER_KEY]


    def __get_configs_from_file(self, configs_file_path: str) -> dict:
        """
        Parse the configs from the config file. Throw a detailed exception if there are problems.

        Args:
            configs_file_path (str): The path to the config file. Should be JSON format.

        Returns:
            dict: The parsed configs.
        """

        try:
            return utilities.read_json_file(file_path=configs_file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"The config file couldn't be found at `{configs_file_path}`.")
        

    def get_album_length_threshold_min(self) -> int:
        """Get the Album length threshold in minutes. All albums shorter than this length will be filtered out."""
        return self.__album_length_threshold_min
    

    def get_all_genres(self) -> set:
        """Get the list of all genres."""
        return self.__genre_playlists_by_name.keys()


    def get_client_id(self) -> str:
        """Get the Spotify application client ID."""
        return self.__client_id
    

    def get_client_secret(self) -> str:
        """Get the Spotify application client secret."""
        return self.__client_secret 
    

    def get_genre_playlists_names(self) -> list:
        """Get the mapping from genre name to Spotify playlist ID. Returns None if the key wasn't found."""
        return list(self.__genre_playlists_by_name.keys())
    
    
    def get_genre_playlist_by_name(self, name: str) -> str:
        """Get the mapping from genre name to Spotify playlist ID. Returns None if the key wasn't found."""
        return utilities.get(data=self.__genre_playlists_by_name, key=name)
    

    def get_genred_album_keys(self) -> set:
        """Get a set of album keys for all albums whose genres have been determined."""
        return self.__ranked_album_genres_by_album_key.keys()
    
    
    def get_ranked_album_genres_by_album_key(self, album_key: str) -> dict:
        """Get a comma-separated list of genres for the matching album. Returns None if the key wasn't found."""
        return utilities.get(data=self.__ranked_album_genres_by_album_key, key=album_key)
    
    
    def update_genre_data(self, album_key: str, genre_data: dict) -> None:
        """Update the genres for a ranked album in memory and on disk."""

        # Add to configs in memory.
        self.__ranked_album_genres_by_album_key[album_key] = genre_data
        # Add to configs on disk.
        with open(self.__ranked_album_genres_file_path, 'w') as json_file:
            json.dump(self.__ranked_album_genres_by_album_key, json_file, indent=4)


    def update_overrides(self, album_key: str, override_data: dict) -> None:
        """Update the album overrides in memory and on disk."""

        # Add to configs in memory.
        self.__ranker_overrides[album_key] = override_data
        # Add to configs on disk.
        with open(self.__ranker_overrides_file_path, 'w') as json_file:
            json.dump(self.__ranker_overrides, json_file, indent=4)
 

    def update_playlist_data(self, genre: str, playlist_id: str):
        """Update the genre playlists in memory and on disk."""

        # Add to configs in memory.
        self.__genre_playlists_by_name[genre] = playlist_id
        # Add to configs on disk.
        with open(self.__genre_playlists_file_path, 'w') as json_file:
            json.dump(self.__genre_playlists_by_name, json_file, indent=4)

    
    def get_ranker_output_path(self) -> str:
        """Get the Album Ranker output path."""
        return self.__ranker_output_path
    

    def get_ranker_override_by_album_key(self, album_key: str) -> dict:
        """Get album override values for the matching album. Returns None if the key wasn't found."""
        return utilities.get(data=self.__ranker_overrides, key=album_key)


    def get_tier_1_playlist_id(self) -> str:
        """Get the tier 3 playlist ID."""
        return self.__tier_1_playlist_id


    def get_tier_2_playlist_id(self) -> str:
        """Get the tier 3 playlist ID."""
        return self.__tier_2_playlist_id
    

    def get_tier_3_playlist_id(self) -> str:
        """Get the tier 3 playlist ID."""
        return self.__tier_3_playlist_id


    def get_tier_3_yearly_threshold(self) -> int:
        """Get the Tier 3 yearly threshold."""
        return self.__tier_3_yearly_threshold
    

    def get_user(self) -> str:
        """Get the Spotify user."""
        return self.__user
