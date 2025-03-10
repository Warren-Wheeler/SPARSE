import modules.album_ranker_constants as constants
from dataclasses import dataclass
import datetime as dt
import logging
from itertools import batched
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import modules.spotify_utilities as spotify_utilities
import time
import modules.utilities as utilities

logging.basicConfig(filename='./log/album_ranker.log', level=logging.INFO)
logger = logging.getLogger(__name__)

class AlbumRankerConfigsException(Exception):
    """An exception that is thrown when there is a problem with validating the configs file."""
    pass

class AlbumRankerConfigs:
    """
    A class representing an Album Ranker configs.

    Attributes:
        config_file (str): The path to the configs JSON file.
    """
    
    def __init__(self, configs_file_path: str):
        """
        Initializes the Album Ranker configs.

        Args:
            configs_file_path (str): The path to the configs file. Should be JSON format.
        """
        configs = self.__getConfigsFromFile(configs_file_path=configs_file_path)
        self.__validate(configs, configs_file_path=configs_file_path)
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

    def __raiseExceptionIfIssuesExist(self, issues: list, configs_file_path: str) -> None:
        """Throw an exception if there are issues with the config file."""
        if issues:
            issuesString = f"The following issues were found with the Album Ranker config file ({configs_file_path}):"
            for issue in issues: issuesString += f"\n\t{issue}"
            raise AlbumRankerConfigsException(issuesString)
        
    def __check_key(self, configs: dict, key: str, expected_type: type, issues: list) -> None:
        """
        Check a key to make sure it exists in the configs and matches the expected type. If a key is
        missing or doesn't match the expected type, append a detailed message about it to the issues list.
        """
        if key not in configs:
            issues.append(f"No `{key}` detected in Album Ranker configs.")
        elif not isinstance(configs[key], expected_type):
            issues.append(f"`{key}` in Album Ranker configs must be a `{expected_type.__name__}`.")
        elif isinstance(configs[key], str) and configs[key] == "":
            issues.append(f"`{key}` in Album Ranker configs must not be empty.")

    def __validate(self, configs: dict, configs_file_path: str) -> None:
        """
        Validates the parsed configs. Throws a detailed exception if there are issues with the configs.

        Args:
            configs (dict): The parsed configs.
            configs_file_path (str): The path to the configs file.
        """
        issues = []

        # Check the config dict to make sure the expected keys exist and have the expected type.
        keys_and_types = {
            constants.CLIENT_ID_KEY: str,
            constants.CLIENT_SECRET_KEY: str,
            constants.TIER_3_PLAYLIST_ID_KEY: str,
            constants.TIER_2_PLAYLIST_ID_KEY: str,
            constants.TIER_1_PLAYLIST_ID_KEY: str,
            constants.OVERRIDE_FILE_PATH_KEY: str,
            constants.RANKER_OUTPUT_PATH_KEY: str,
            constants.TIER_3_YEARLY_THRESHOLD_KEY: int,
            constants.ALBUM_LENGTH_THRESHOLD_MIN_KEY: int
        }
        
        for key, expected_type in keys_and_types.items():
            self.__check_key(configs, key, expected_type, issues)
        self.__raiseExceptionIfIssuesExist(issues=issues, configs_file_path=configs_file_path)

        # Extra validation:
        if not configs[constants.RANKER_OUTPUT_PATH_KEY].lower().endswith(constants.CSV_EXTENSION): 
            issues.append(f"Album Ranker output file must be a {constants.CSV_EXTENSION} file. Please check configs.") 
        if (configs[constants.TIER_3_YEARLY_THRESHOLD_KEY] <= 0):
            issues.append("Tier 3 yearly threshold must be greater than 0.")
        if (configs[constants.ALBUM_LENGTH_THRESHOLD_MIN_KEY] <= 0):
            issues.append("Album length threshold must be greater than 0.")
        self.__raiseExceptionIfIssuesExist(issues=issues, configs_file_path=configs_file_path)

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

@dataclass
class Album:
    """
    A class representing an Album Ranker album.

    Attributes:
        artists (str): The comma-separated list of album artists.
        name (str): The album name.
        highest_possible_score (float): The highest score this album can achieve given the number and length of tracks.
        year (int): The year the album was released.
        duration_ms (int): The length of the album in milliseconds.
        album_track_names (set): The set of track names for all tracks in the album.
        playlist_placements (dict): The mapping from tier playlist placement key to track score the tracks in this album. 
            Tier placement key formatted as: "<TRACK_NAME>_<TIER>"
        best_tracks (set): The set of tier 3 tracks in this album.
        album_id (str): The Spotify album ID.
    """
    artists: str
    name: str
    highest_possible_score: float
    year: int
    duration_ms: int
    album_track_names: set
    playlist_placements: dict
    best_tracks: set
    album_id: str

class AlbumRankerPlaylistTierException(Exception):
    pass

class SpotifyClient:
    """A class representing a client for interacting with Spotify API using retry logic."""
        
    # The redirect uri for authenticating the Spotify client.
    __redirect_uri = "https://example.com/callback"
    # The scope for the python API. We need modify permissions to remove all tracks from each temp playlist and add them back.
    __scope = "playlist-modify-private"

    def __init__(self, configs: AlbumRankerConfigs):
        """
        Initializes an Spotify Client object.

        Args:
            configs (AlbumRankerConfigs): The Album Ranker configs.
        """
        self.__client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=configs.getClientID(),
            client_secret=configs.getClientSecret(),
            redirect_uri=self.__redirect_uri,
            scope=self.__scope
        ))

    def __run_with_retry(self, func, id: str, items: list = None, max_retries: int=3, delay_seconds: int=1):
        """
        Run something with a variable number of times if an exception is encountered.

        Args:
            func (function): The function containing the call to the resource.
            retries (int): The number of retries before throwing an exception. 2 by default.
            delay_seconds (int): Delay between tries in seconds.
        """
        for attempt in range(max_retries):
            try:
                if (items == None):
                    return func(id)
                else:
                    return func(id, items)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise  # Re-raise exception on the last attempt
                print(f"Attempt {attempt + 1} failed: {e}, retrying in {delay_seconds} seconds...")
                time.sleep(delay_seconds)

    def getAlbum(self, album_id: str) -> dict:
        """Try to fetch an album using the Spotify client."""
        return self.__run_with_retry(func=self.__client.album, id=album_id)

    def getPlaylistItems(self, playlist_id: str) -> dict:
        """Try to fetch the tracks from a playlist using the Spotify client."""
        return self.__run_with_retry(func=self.__client.playlist, id=playlist_id)[constants.TRACKS_KEY][constants.ITEMS_KEY]

    def removePlaylistItems(self, playlist_id: str, tracks: list) -> None:
        """Try to remove tracks from a playlist in batches of 100 using the Spotify client."""
        for batch in batched(tracks, 100):
            self.__run_with_retry(
                func=self.__client.playlist_remove_all_occurrences_of_items, 
                id=playlist_id, 
                items=batch
            )

    def addPlaylistItems(self, playlist_id: str, tracks: list) -> None:
        """Try to add tracks to a playlist in batches of 100 using the Spotify client."""
        for batch in batched(tracks, 100):
            self.__run_with_retry(
                func=self.__client.playlist_add_items,
                id=playlist_id, 
                items=batch
            )

class AlbumRanker:
    """
    A class representing an Album Ranker.

    Attributes:
        client_id (str): The unique identifier for this Spotify application.
        client_secret (str): The confidential string for this Spotify application used for authentication.
    """

    # The columns of the CSV file generated by the ranker.
    __cols = "Artists,Album Name,Year,Total Score,Highest Possible Score,Tier 3 Tracks"

    def __init__(self, configs: AlbumRankerConfigs):
        """
        Initializes an Album Ranker object.

        Args:
            configs (AlbumRankerConfigs): The Album Ranker configs.
        """
        # Set the Album Ranker configs.
        self.__configs = configs

        # Set the Spotify API client.
        self.__client = SpotifyClient(configs=configs)

    def __getAlbumKeyGivenArtists(self, artists: str, album: dict) -> str:
        """
        Get the album key from a Spotify album. 
        Formatted as: "<COMMA_SEPARATED_ALBUM_ARTISTS> - <ALBUM_TITLE>")
        """
        return f"{artists} - {album[constants.NAME_KEY]}"

    def __getEmptyAlbum(self, track: dict, artist_names: str) -> Album:
        """
        Create an empty album container based on a Spotify track.

        Args:
            track (dict): The Spotify track that belongs to the new album.
            artist_names (str): The comma-separated list of artist names for this album.

        Returns:
            dict: The empty album for the provided Spotify track.
        """
        album = track[constants.ALBUM_KEY]
        album_id = album[constants.URI_KEY]

        # We need more metadata for this album than we can get from the track.
        enriched_album = self.__client.getAlbum(album_id=album_id)

        album_tracks = enriched_album[constants.TRACKS_KEY][constants.ITEMS_KEY]
        highest_possible_score = spotify_utilities.getAlbumHighestPossibleScore(album_tracks=album_tracks)
        year = utilities.extractYearFromDate(date=album[constants.RELEASE_DATE_KEY])
        tracks = spotify_utilities.getTrackNamesFromAlbum(album_tracks=album_tracks)
        
        new_album = Album(
            artists=artist_names,
            name=album[constants.NAME_KEY],
            highest_possible_score=highest_possible_score,
            year=year,
            duration_ms=0,
            album_track_names=tracks,
            playlist_placements={},
            best_tracks=set(),
            album_id=album_id
        )

        return new_album

    def __getTrackKey(self, name: str, tier: int) -> str:
        """
        Get the track key for a Spotify track at a certain tier.
        
        Returns:
            str: The track key formatted as: "<TRACK_NAME>_<TIER>"
        """
        if (tier > 3) or (tier < 1):
            raise AlbumRankerPlaylistTierException("Tried to add {name} to tier {tier}, but there is only a tier for 1, 2 and 3.")
        return f"{name}_{tier}"

    def __addTieredTrackToMemory(
        self, 
        tier: int,
        album_key: str, 
        duration_ms: int, 
        memory: dict, 
        tier_tracks: dict,
        name: str, 
        score: float, 
        track_id: str
    ) -> None:
        """
        Add a tiered track to memory. This function also adds this track to memory for tier 2 and tier 1. This method is
        idempotent.

        Args:
            tier (int): The tier of the track we're adding to memory.
            album_key (str): The album key for the album we're adding this track to. 
                (formatted as: "<COMMA_SEPARATED_ALBUM_ARTISTS> - <ALBUM_TITLE>")
            duration_ms (int): The duration of the track we're adding in milliseconds.
            memory (dict): The Albums encountered during this Album Ranker run, grouped by album key.
            tier_tracks (dict): The Spotify track IDs for tracks encountered during this Album Ranker run, grouped by tier ID.
            name (str): The name of the track.
            score (float): The score for the track.
            track_id (str): The Spotify track ID for the track.
        """
        key = self.__getTrackKey(name=name, tier=tier)
        memory[album_key].playlist_placements[key] = score
        tier_key = spotify_utilities.getTierKey(tier)
        # Only add to best tracks and increase album duration if this track hasn't been counted yet.
        if (tier_key not in tier_tracks[tier_key]):
            tier_tracks[tier_key].add(track_id)
            if (tier == 3):
                # Only add to best tracks if tier 3.
                memory[album_key].best_tracks.add(track_id)
            elif (tier == 1):
                # Only add duration if tier 1.
                memory[album_key].duration_ms += duration_ms
                # Do not recurse if tier 1.
                return
        
        self.__addTieredTrackToMemory(
            tier=tier-1,
            album_key=album_key, 
            duration_ms=duration_ms, 
            memory=memory, 
            tier_tracks=tier_tracks,
            name=name, 
            score=score, 
            track_id=track_id
        )

    def __saveTrackData(
        self, track: dict, 
        tier: int, 
        album_key: str, 
        memory: dict, 
        tier_tracks: dict
    ) -> None:
        """
        Save a track to the album it belongs to in memory and the tier it belongs to in tier_tracks.

        Args:
            track (dict): The Spotify track we're adding to memory.
            tier (int): The tier this track belongs to.
            album_key (str): The album key for the album we're adding this track to. 
                Formatted as: "<COMMA_SEPARATED_ALBUM_ARTISTS> - <ALBUM_TITLE>"
            memory (dict): The Albums encountered during this Album Ranker run, grouped by album key.
            tier_tracks (dict): The Spotify track IDs for tracks encountered during this Album Ranker run, grouped by tier ID.
        """
        name = spotify_utilities.getNameFromTrack(track=track)
        score = spotify_utilities.getScoreFromTrack(track=track)
        track_id = track[constants.URI_KEY]
        duration_ms=track[constants.DURATION_MS_KEY]

        # A track's judged quality correllates directly with the highest tier playlist it is in. Tier 3 is the highest quality rating a 
        # track can receive, however, some tracks in an album are missing from all tier playlists entirely. To reflect this, a track in a 
        # high tier is also counted for all lower tiers, even if this is not explicitly represented in the playlists. To that end, each 
        # time this method is called, we add a track to its album's `playlist_placements` up to 3 times. We use a Python set for an
        # album's `playlist_placements` to make this method idempotent. This means that each can be added to memory using this function
        # any number of times, but will only be recorded the same number of times as the track's highest tier.
        # 
        # For example, see this execution:
        #
        #   memory = self.__saveTrackData(track=track_x, tier=1)
        #   memory = self.__saveTrackData(track=track_x, tier=2)
        #   memory = self.__saveTrackData(track=track_x, tier=1)
        #   memory = self.__saveTrackData(track=track_x, tier=1)
        # 
        # After the above code runs, memory will only contain a record of track_x for tier 1 and tier 2 since 2 is the highest tier
        # that was executed.

        self.__addTieredTrackToMemory(
            tier=tier,
            album_key=album_key,
            duration_ms=duration_ms,
            memory=memory,
            tier_tracks=tier_tracks,
            name=name,
            score=score,
            track_id=track_id
        )

    def __executeTier(
        self, 
        playlist_id: str, 
        tier: int, 
        memory: dict, 
        tier_tracks: dict
    ) -> None:
        """
        Collect scoring metadata on a tier playlist.

        Args:
            playlist_id (str): The Spotify Playlist ID for the playlist that contains the tracks in this tier.
            tier (int): The tier that this group of tracks.
            memory (dict): The Albums encountered during this Album Ranker run, grouped by album key.
        """

        # Only 100 tracks can be fetched from a playlist at a time, and the order of the fetched tracks cannot be guaranteed. 
        # Therefore, we need to collect scoring metadata in batches. We also need to delete each batch from the Spotify playlist 
        # after a batch has been recorded to prevent fetching duplicate tracks. 

        logger.info(f"Running Tier {tier}...")

        # Fetch the initial batch.
        playlist_tracks = self.__client.getPlaylistItems(playlist_id=playlist_id)

        # Run until there are no more tracks in the playlist.
        while len(playlist_tracks) != 0:
            tracks_to_delete = []

            for track in playlist_tracks:

                unwrapped_track = track[constants.TRACK_KEY]
                album = unwrapped_track[constants.ALBUM_KEY]
                artists = spotify_utilities.getArtistNamesFromAlbum(album=album)
                album_key = self.__getAlbumKeyGivenArtists(artists=artists, album=album)

                # If the album this track belongs to does not exist in memory, add it.
                if album_key not in memory:
                    new_album = self.__getEmptyAlbum(track=unwrapped_track, artist_names=artists)
                    memory[album_key] = new_album

                # Add the track to memory.
                self.__saveTrackData(
                    track=unwrapped_track, 
                    tier=tier, 
                    album_key=album_key, 
                    memory=memory,
                    tier_tracks=tier_tracks
                )

                # Mark this track for deletion from the playlist.
                tracks_to_delete.append(unwrapped_track[constants.URI_KEY])

            # Remove this batch from the playlist.
            self.__client.removePlaylistItems(playlist_id=playlist_id, tracks=tracks_to_delete)

            # Fetch the next batch.
            playlist_tracks = self.__client.getPlaylistItems(playlist_id=playlist_id)

        logger.info(f"Tier {tier} complete.")
    
    def __isSubset(self, subsetAlbum: Album, supersetAlbum: Album) -> bool:
        """Check if the tracks in one album are a subset of the tracks in another album."""
        trackExistsInSuperset = lambda track: track in supersetAlbum.album_track_names
        return all(trackExistsInSuperset(track) for track in subsetAlbum.album_track_names)

    def __needsConsolidation(self, smallerAlbum: Album, largerAlbum: Album) -> bool:
        """
        Check if a smaller album needs to be consolidated with a larger album. Albums need consolidation if:
            1. The smaller album and larger album have the same artists, name and year.
            2. The tracks in the smaller album is a subset of the tracks in the larger album.
        """
        names_match = smallerAlbum.artists == largerAlbum.artists and \
            smallerAlbum.name == largerAlbum.name and \
            smallerAlbum.year == largerAlbum.year
        return names_match or self.__isSubset(subsetAlbum=smallerAlbum, supersetAlbum=largerAlbum)

    def __consolidateAlbums(self, memory: dict) -> None:
        """
        Consolidates albums in memory. Some albums are spread out among multiple album entries in memory. For example, a some tracks 
        may be in a standard version of an album and others in the deluxe version. This function would move the tracks in the regular
        version into the deluxe version and delete the regular version from memory.

        Args:
            memory (dict): The Albums encountered during this Album Ranker run, grouped by album key.
        """

        # Initialize list of keys that need to be deleted.
        keys_to_delete = set()

        # Move albums that only contain a subset of tracks from other albums to the bigger album.
        album_keys = memory.keys()
        for l in album_keys:
            for r in album_keys:
                if memory[l].highest_possible_score < memory[r].highest_possible_score:

                    # Check if each track in the left album is also in the right album.
                    if (self.__needsConsolidation(smallerAlbum=memory[l], largerAlbum=memory[r])):

                        # Move tracks from the smaller album to the larger album.
                        memory[r].playlist_placements.update(memory[l].playlist_placements)
                        memory[r].best_tracks.update(memory[l].best_tracks)
                        keys_to_delete.add(l)

                        # End iteration after this album's match has been found.
                        break

        # Delete the albums there were moved to larger albums.
        for key in keys_to_delete:
            del memory[key]
        keys_to_delete = set()

        # Override album values using the override file.
        album_keys = memory.keys()
        overrides = self.__configs.getAlbumOverrides()
        for key in album_keys:
            album_length_threshold_ms = self.__configs.getAlbumLengthThresholdMin() * 60 * 1000
            if memory[key].duration_ms < album_length_threshold_ms:
                keys_to_delete.add(key)
            else: 
                album_id = memory[key].album_id
                if album_id in overrides:
                    if constants.HIGHEST_POSSIBLE_SCORE_KEY in overrides[album_id]:
                        memory[key].highest_possible_score = overrides[album_id][constants.HIGHEST_POSSIBLE_SCORE_KEY]
                    if constants.YEAR_KEY in overrides[album_id]:
                        memory[key].year = overrides[album_id][constants.YEAR_KEY]
            
        # Filter out short albums.
        for key in keys_to_delete:
            del memory[key]

    def __addTracksToPlaylist(self, tier: int, playlist_id: str, tracks: list) -> None:
        """
        Adds tracks to a Spotify playlist in batches of 100 at a time. Tracks need to be batched in this way because Spotify API
        only allows adding a maximum of 100 tracks to a playlist per transaction.

        Args:
            tier (int): The tier playlist that we're adding tracks to.
            playlist_id (str): The Spotify Playlist ID for the playlist that we're adding tracks to.
            tracks (list): The list of Spotify track IDs we're adding to the playlist
        """
        logger.info(f"Adding tracks back to tier {tier}...")
        self.__client.addPlaylistItems(playlist_id=playlist_id, tracks=tracks)

    def __executeTierTrackDiff(self, tier_tracks: dict) -> None:
        """Remove tracks represented in higher tiers from lower tiers in memory."""
        tier_tracks[spotify_utilities.getTierKey(2)] = tier_tracks[spotify_utilities.getTierKey(2)].difference(
            tier_tracks[spotify_utilities.getTierKey(3)]
        )
        tier_tracks[spotify_utilities.getTierKey(1)] = tier_tracks[spotify_utilities.getTierKey(1)].difference(
            tier_tracks[spotify_utilities.getTierKey(3)] | tier_tracks[spotify_utilities.getTierKey(2)]
        )

    def __getOutputRowFromAlbum(self, album: Album) -> str:
        """Get a stringified row for the Album Ranker output file given an album."""
        artists = album.artists
        name = album.name
        year = album.year
        total_score = sum(album.playlist_placements.values())
        highest_score = album.highest_possible_score
        best_songs = str(album.best_tracks)
        return f"\n\"{artists}\",\"{name}\",{year},{total_score},{highest_score},\"{best_songs}\""

    def __writeAlbumRankerResults(self, memory: dict) -> None:
        """Write the album ranker results to a CSV file."""
        logging.basicConfig(filename='album_ranker.log', level=logging.WARN)

        outputPath = self.__configs.getAlbumRankerOutputPath()

        # Write the column names.
        with open(file=outputPath, mode='w') as output_file:
            output_file.write(self.__cols)
                    
        # Write a row for each album & keep a count of tracks for each year.
        year_counts = {}
        with open(file=outputPath, mode='a') as output_file:
            album_keys = memory.keys()
            for key in album_keys:
                album = memory[key]
                output_file.write(self.__getOutputRowFromAlbum(album))
                if (album.year in year_counts):
                    year_counts[album.year] += 1  
                else:
                    year_counts[album.year] = 1

        # Log a warning if there are more than the threshold number of tier 3 tracks in a given year.
        for key in year_counts:
            if year_counts[key] > self.__configs.getTier3YearlyThreshold():
                logger.warning(f"Warning: {year_counts[key]} tier 3 tracks in year {key}.")

    def __executeAllTiers(self, memory: dict, tier_tracks:dict) -> None:
        """Collect scoring metadata on all tier playlists."""

        # Execute tier 3:
        self.__executeTier(
            playlist_id=self.__configs.getTier3PlaylistID(),
            tier=3,
            memory=memory,
            tier_tracks=tier_tracks
        )

        # Execute tier 2:
        self.__executeTier(
            playlist_id=self.__configs.getTier2PlaylistID(),
            tier=2,
            memory=memory,
            tier_tracks=tier_tracks
        )

        # Execute tier 1:
        self.__executeTier(
            playlist_id=self.__configs.getTier1PlaylistID(),
            tier=1,
            memory=memory,
            tier_tracks=tier_tracks
        )   

    def __addTracksBackToTierPlaylists(self, tier_tracks: dict) -> None:
        """Add all tracks back to tier playlists that were deleted during the process of collecting scoring metadata."""

        # Add tracks back to tier 3 playlist.
        self.__addTracksToPlaylist(
            tier=3, 
            playlist_id=self.__configs.getTier3PlaylistID(), 
            tracks=tier_tracks[spotify_utilities.getTierKey(3)]
        )

        # Add tracks back to tier 2 playlist.
        self.__addTracksToPlaylist(
            tier=2, 
            playlist_id=self.__configs.getTier2PlaylistID(), 
            tracks=tier_tracks[spotify_utilities.getTierKey(2)]
        )

        # Add tracks back to tier 1 playlist.
        self.__addTracksToPlaylist(
            tier=1, 
            playlist_id=self.__configs.getTier1PlaylistID(), 
            tracks=tier_tracks[spotify_utilities.getTierKey(1)]
        )

    def run(self) -> None:
        """Runs the Album Ranker."""

        t0 = dt.datetime.now()

        # Initialize memory:
        memory = {}
        tier_tracks = {
            spotify_utilities.getTierKey(3): set(),
            spotify_utilities.getTierKey(2): set(),
            spotify_utilities.getTierKey(1): set()
        }

        # Collect scoring metadata for all tiers:
        self.__executeAllTiers(memory=memory, tier_tracks=tier_tracks)

        # Consolidate albums in memory:
        self.__consolidateAlbums(memory=memory)

        # Remove tracks represented in higher tiers from lower tiers in memory:
        self.__executeTierTrackDiff(tier_tracks=tier_tracks)

        # Add tracks back to tier playlists:
        self.__addTracksBackToTierPlaylists(tier_tracks=tier_tracks)

        # Write ranker results to file:
        self.__writeAlbumRankerResults(memory=memory)

        logger.info(f"Ranker completed in {utilities.getSecondsSinceDatetime(t0)} seconds.")

configs = AlbumRankerConfigs(configs_file_path="./config.json")
ranker = AlbumRanker(configs=configs)
ranker.run()