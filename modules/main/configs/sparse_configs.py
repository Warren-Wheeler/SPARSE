import modules.main.util.constants as constants
from modules.main.configs.sparse_configs_validation import validate
import modules.main.util.utilities as utilities


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
        configs = self.__getConfigsFromFile(configs_file_path=configs_file_path)
        validate(configs, configs_file_path=configs_file_path)
        self.__client_id = configs[constants.CLIENT_ID_KEY]
        self.__client_secret = configs[constants.CLIENT_SECRET_KEY]
        self.__tier_3_playlist_id = configs[constants.TIER_3_PLAYLIST_ID_KEY]
        self.__tier_2_playlist_id = configs[constants.TIER_2_PLAYLIST_ID_KEY]
        self.__tier_1_playlist_id = configs[constants.TIER_1_PLAYLIST_ID_KEY]
        self.__override = utilities.read_json_file(file_path=configs[constants.OVERRIDE_FILE_PATH_KEY])
        self.__ranker_output_path = configs[constants.RANKER_OUTPUT_PATH_KEY]
        self.__tier_3_yearly_threshold = configs[constants.TIER_3_YEARLY_THRESHOLD_KEY]
        self.__album_length_threshold_min = configs[constants.ALBUM_LENGTH_THRESHOLD_MIN_KEY]

    def __getConfigsFromFile(self, configs_file_path: str) -> dict:
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
        
    def getClientID(self) -> str:
        """Get the client ID."""
        return self.__client_id
    
    def getClientSecret(self) -> str:
        """Get the client secret."""
        return self.__client_secret

    def getTier3PlaylistID(self) -> str:
        """Get the tier 3 playlist ID."""
        return self.__tier_3_playlist_id

    def getTier2PlaylistID(self) -> str:
        """Get the tier 3 playlist ID."""
        return self.__tier_2_playlist_id

    def getTier1PlaylistID(self) -> str:
        """Get the tier 3 playlist ID."""
        return self.__tier_1_playlist_id

    def getAlbumOverrides(self) -> dict:
        """Get the album overrides."""
        return self.__override

    def getAlbumRankerOutputPath(self) -> str:
        """Get the Album Ranker output path."""
        return self.__ranker_output_path

    def getTier3YearlyThreshold(self) -> int:
        """Get the Tier 3 yearly threshold."""
        return self.__tier_3_yearly_threshold

    def getAlbumLengthThresholdMin(self) -> int:
        """Get the Album length threshold in minutes. All albums shorter than this length will be filtered out."""
        return self.__album_length_threshold_min