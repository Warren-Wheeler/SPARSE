import datetime as dt
import logging
from dataclasses import dataclass
import modules.main.util.constants as C
from modules.main.configs.sparse_configs import SparseConfigs
import modules.main.spotify.spotify_utilities as spotify_utilities
from modules.main.spotify.spotify_client import SpotifyClient
import modules.main.util.utilities as utilities


# Set up logging.
logging.basicConfig(filename='./log/album_ranker.log', level=logging.INFO)
logger = logging.getLogger(__name__)

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
            Tier placement key formatted as: "TRACK_NAME_TIER"
        best_tracks (set): The set of tier 3 tracks in this album.
    """

    artists: str
    name: str
    highest_possible_score: float
    year: int
    duration_ms: int
    album_track_names: set
    playlist_placements: dict
    best_tracks: set


class AlbumRanker:
    """
    A class representing an Album Ranker.

    Attributes:
        client_id (str): The unique identifier for this Spotify application.
        client_secret (str): The confidential string for this Spotify application used for authentication.
    """

    def __init__(self, configs: SparseConfigs, client: SpotifyClient):
        """
        Initializes an Album Ranker object.

        Args:
            configs (SparseConfigs): The Album Ranker configs.
            client (SpotifyClient): The Spotify client.
        """

        self.__configs = configs
        self.__client = client


    def __getAlbumKeyGivenArtists(self, artists: str, album: dict) -> str:
        """
        Get the album key from a Spotify album. 
            Formatted as: "{COMMA_SEPARATED_ALBUM_ARTISTS} - {ALBUM_TITLE}")
        """
        return utilities.get_album_key(artists, album[C.NAME_KEY])


    def __getEmptyAlbum(self, track: dict, artist_names: str) -> Album:
        """
        Create an empty album container based on a Spotify track.

        Args:
            track (dict): The Spotify track that belongs to the new album.
            artist_names (str): The comma-separated list of artist names for this album.

        Returns:
            dict: The empty album for the provided Spotify track.
        """

        album = track[C.ALBUM_KEY]
        album_id = album[C.URI_KEY]

        # We need more metadata for this album than we can get from the track.
        enriched_album = self.__client.getAlbum(album_id=album_id)

        album_tracks = spotify_utilities.get_tracks(spotify_album=enriched_album)
        highest_possible_score = spotify_utilities.get_album_highest_possible_score(spotify_album_tracks=album_tracks)
        year = utilities.extract_year_from_date(date=album[C.RELEASE_DATE_KEY])
        tracks = spotify_utilities.get_track_names(spotify_album_tracks=album_tracks)
        
        new_album = Album(
            artists=artist_names,
            name=album[C.NAME_KEY],
            highest_possible_score=highest_possible_score,
            year=year,
            duration_ms=0,
            album_track_names=tracks,
            playlist_placements={},
            best_tracks=set()
        )

        return new_album


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
        
        key = spotify_utilities.get_track_key(name=name, tier=tier)
        memory[album_key].playlist_placements[key] = score
        tier_key = spotify_utilities.get_tier_key(tier)

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
                Formatted as: "{COMMA_SEPARATED_ALBUM_ARTISTS} - {ALBUM_TITLE}"
            memory (dict): The Albums encountered during this Album Ranker run, grouped by album key.
            tier_tracks (dict): The Spotify track IDs for tracks encountered during this Album Ranker run, grouped by tier ID.
        """

        name = spotify_utilities.get_track_name(spotify_track=track)
        score = spotify_utilities.get_track_score(spotify_track=track)
        track_id = track[C.URI_KEY]
        duration_ms=track[C.DURATION_MS_KEY]

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

                unwrapped_track = track[C.TRACK_KEY]
                album = unwrapped_track[C.ALBUM_KEY]
                artists = spotify_utilities.get_album_artist_names(spotify_album=album)
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
                tracks_to_delete.append(unwrapped_track[C.URI_KEY])

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
        for key in album_keys:
            album_length_threshold_ms = self.__configs.get_album_length_threshold_min() * 60 * 1000
            if memory[key].duration_ms < album_length_threshold_ms:
                keys_to_delete.add(key)
            else: 
                override = self.__configs.get_ranker_override_by_album_key(album_key=key)
                if override:
                    if C.HIGHEST_POSSIBLE_SCORE_KEY in override:
                        memory[key].highest_possible_score = override[C.HIGHEST_POSSIBLE_SCORE_KEY]
                    if C.YEAR_KEY in override:
                        memory[key].year = override[C.YEAR_KEY]
                    if C.NAME_KEY in override:
                        memory[key].name = override[C.NAME_KEY]
                    if C.ARTISTS_KEY in override:
                        memory[key].artists = override[C.ARTISTS_KEY]
            
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

        tier_tracks[spotify_utilities.get_tier_key(2)] = tier_tracks[spotify_utilities.get_tier_key(2)].difference(
            tier_tracks[spotify_utilities.get_tier_key(3)]
        )
        tier_tracks[spotify_utilities.get_tier_key(1)] = tier_tracks[spotify_utilities.get_tier_key(1)].difference(
            tier_tracks[spotify_utilities.get_tier_key(3)] | tier_tracks[spotify_utilities.get_tier_key(2)]
        )


    def __getOutputRowFromAlbum(self, album: Album) -> str:
        """Get a stringified row for the Album Ranker output file given an album."""

        artists = album.artists
        name = album.name
        year = album.year
        total_score = sum(album.playlist_placements.values())
        highest_score = album.highest_possible_score
        best_songs = str(list(album.best_tracks))

        return f"\n\"{artists}\",\"{name}\",{year},{total_score},{highest_score},\"{best_songs}\""


    def __writeAlbumRankerResults(self, memory: dict) -> None:
        """Write the album ranker results to a CSV file."""

        logging.basicConfig(filename='album_ranker.log', level=logging.WARN)
        outputPath = self.__configs.get_ranker_output_path()

        # Write the column names.
        with open(file=outputPath, mode='w') as output_file:
            output_file.write(C.OUTPUT_FILE_COLUMN_NAMES)
                    
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
            if year_counts[key] > self.__configs.get_tier_3_yearly_threshold():
                logger.warning(f"Warning: {year_counts[key]} tier 3 tracks in year {key}.")


    def __executeAllTiers(self, memory: dict, tier_tracks:dict) -> None:
        """Collect scoring metadata on all tier playlists."""

        # Execute tier 3:
        self.__executeTier(
            playlist_id=self.__configs.get_tier_3_playlist_id(),
            tier=3,
            memory=memory,
            tier_tracks=tier_tracks
        )

        # Execute tier 2:
        self.__executeTier(
            playlist_id=self.__configs.get_tier_2_playlist_id(),
            tier=2,
            memory=memory,
            tier_tracks=tier_tracks
        )

        # Execute tier 1:
        self.__executeTier(
            playlist_id=self.__configs.get_tier_1_playlist_id(),
            tier=1,
            memory=memory,
            tier_tracks=tier_tracks
        )   


    def __addTracksBackToTierPlaylists(self, tier_tracks: dict) -> None:
        """Add all tracks back to tier playlists that were deleted during the process of collecting scoring metadata."""

        # Add tracks back to tier 3 playlist.
        self.__addTracksToPlaylist(
            tier=3, 
            playlist_id=self.__configs.get_tier_3_playlist_id(), 
            tracks=tier_tracks[spotify_utilities.get_tier_key(3)]
        )

        # Add tracks back to tier 2 playlist.
        self.__addTracksToPlaylist(
            tier=2, 
            playlist_id=self.__configs.get_tier_2_playlist_id(), 
            tracks=tier_tracks[spotify_utilities.get_tier_key(2)]
        )

        # Add tracks back to tier 1 playlist.
        self.__addTracksToPlaylist(
            tier=1, 
            playlist_id=self.__configs.get_tier_1_playlist_id(), 
            tracks=tier_tracks[spotify_utilities.get_tier_key(1)]
        )


    def run(self) -> None:
        """Runs the Album Ranker."""

        t0 = dt.datetime.now()

        # Initialize memory:
        memory = {}
        tier_tracks = {
            spotify_utilities.get_tier_key(3): set(),
            spotify_utilities.get_tier_key(2): set(),
            spotify_utilities.get_tier_key(1): set()
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

        logger.info(f"Ranker completed in {utilities.get_seconds_since_datetime(t0)} seconds.")
        
        
if __name__ == "__main__":
    configs = SparseConfigs()
    client = SpotifyClient(configs=configs)
    ranker = AlbumRanker(configs=configs, client=client)
    ranker.run()
