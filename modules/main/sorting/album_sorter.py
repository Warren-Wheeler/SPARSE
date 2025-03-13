
import pandas as pd
import ast
from itertools import chain
from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient
import modules.main.util.constants as C
import modules.main.spotify.spotify_utilities as spotify_utilities
import modules.main.util.utilities as utilities


class AlbumSorter():
    """
    A class representing an Album Sorter.
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
        self.refresh_df()
    

    def __get_filtered_df(self, year: int, genre_keyword: str = None) -> pd.DataFrame:
        """
        Return a copy of the album data that has been filtered by year and/or genre keyword.

        Args:
            year (int): The year that all albums in the filtered dataframe must match. 
                If None, return all available years.
            genre_keyword (str): The keyword that the full genre must contain for all albums in the filtered dataframe. 
                If None, return all available genres.

        Return:
            pd.Dataframe: A new dataframe created by filtering the available album data by year and/or genre.
        """

        # If year and genre_keyword are not empty, filter on both.
        if (year != None) & (genre_keyword != None):
            return self.__df[
                (self.__df[C.SORTER_YEAR_KEY] == year) & 
                    (self.__df[C.SORTER_GENRES_KEY].str.contains(genre_keyword, na=False))
            ]
        
        # If year is not empty but genre_keyword is, just filter on year.
        elif year != None:
            return self.__df[self.__df[C.SORTER_YEAR_KEY] == year]
        
        # If genre_keyword is not empty but year is, just filter on genre_keyword.
        elif genre_keyword != None:
            return self.__df[self.__df[C.SORTER_GENRES_KEY].str.contains(genre_keyword, na=False)]
        
        # If both year and genre_keyword are empty, return all available album data.
        else:
            return self.__df


    def __album_data_to_str(self, df: pd.DataFrame) -> str:
        """Convert an album DataFrame to a readable string."""

        # Create rating column.
        df[C.SORTER_RATING_KEY] = (df[C.SORTER_TOTAL_SCORE_KEY] / df[C.SORTER_HIGHEST_POSSIBLE_SCORE_KEY]) * 100

        # Limit length of columns.
        df[C.SORTER_ALBUM_NAME_KEY] = df[C.SORTER_ALBUM_NAME_KEY].transform(lambda s: s[:40])
        df[C.SORTER_ARTISTS_KEY] = df[C.SORTER_ARTISTS_KEY].transform(lambda s: s[:40])
        df[C.SORTER_GENRES_KEY] = df[C.SORTER_GENRES_KEY].transform(lambda s: s[:30])

        # Drop unnecessary columns and sort by rating.
        dropped_df = df.drop([C.SORTER_TOTAL_SCORE_KEY, C.SORTER_HIGHEST_POSSIBLE_SCORE_KEY, C.SORTER_TIER_3_TRACKS_KEY], axis=1) \
            .sort_values(by=C.SORTER_RATING_KEY, ascending=False) \
            .reset_index(drop=True)
        dropped_df.index += 1

        # Convert to markdown to improve readability.
        return dropped_df.to_markdown()
    

    def __get_albums_with_unknown_genre(self) -> pd.DataFrame:
        """Fetch albums whose genre has not been determined yet from memory."""
        return self.__df[self.__df[C.SORTER_GENRES_KEY] == C.UNKNOWN_GENRE_NAME]
    
    
    def __add_tracks_to_genre_playlist(self, tracks_ids: list, genre: str) -> None:
        """Add a list of tracks to a genre-specific playlist in the user's library. Creates a new playlist if one doesn't exist yet."""

        # Do nothing if no tracks were passed in.
        if tracks_ids != []:

            # Use pre-existing genre playlist if it exists, otherwise create a new one.
            playlistFromFile = self.__configs.get_genre_playlist_by_name(name=genre)
            if playlistFromFile:
                playlist_uri = playlistFromFile
            else:
                playlist_uri = self.__client.createUserPlaylist(playlist_title=genre)
                self.__configs.update_playlist_data(genre=genre, playlist_id=playlist_uri)

            # Add the tracks to the playlist.
            self.__client.addPlaylistItems(playlist_id=playlist_uri, tracks=tracks_ids)
            

    def __write_genres(self, artist_names: str, album_name: str, genres: str) -> None:
        """Record an album's genres to memory and disk."""

        self.__configs.update_genre_data(
            album_key=utilities.get_album_key(artist_names=artist_names, album_name=album_name),
            genre_data={
                C.SORTER_ARTISTS_KEY: artist_names,
                C.SORTER_ALBUM_NAME_KEY: album_name,
                C.SORTER_GENRES_KEY: genres
            }
        )


    def __get_override_data(self, album_uri: str) -> dict:
        """
        Get the values needed to create a new album override.
        
        Args:
            album_uri (str): The Spotify URI for the album whose data we're fetching.

        Returns:
            dict: The data needed for an override (highest possible score, year, name and artists).
        """

        override_album = self.__client.getAlbum(album_id=album_uri)
        album_tracks = spotify_utilities.get_tracks(spotify_album=override_album)
        highest_possible_score = spotify_utilities.get_album_highest_possible_score(spotify_album_tracks=album_tracks)
        year = utilities.extract_year_from_date(date=override_album[C.RELEASE_DATE_KEY])
        artists = spotify_utilities.get_album_artist_names(spotify_album=override_album)
        
        override_data = {
            C.HIGHEST_POSSIBLE_SCORE_KEY: highest_possible_score,
            C.YEAR_KEY: year,
            C.NAME_KEY: override_album[C.NAME_KEY],
            C.ARTISTS_KEY: artists,
        }

        return override_data

        
    def refresh_df(self) -> None:
        """Refresh the album data in memory based on the data on disk."""

        # Read the album data from disk.
        self.__df = pd.read_csv(self.__configs.get_ranker_output_path())

        # Enrich with genre data from disk.
        self.__df[C.SORTER_GENRES_KEY] = C.UNKNOWN_GENRE_NAME
        for key in self.__configs.get_genred_album_keys():
            genre_data = self.__configs.get_ranked_album_genres_by_album_key(key)
            self.__df.loc[
                (self.__df[C.SORTER_ARTISTS_KEY] == genre_data[C.SORTER_ARTISTS_KEY]) & 
                    (self.__df[C.SORTER_ALBUM_NAME_KEY] == genre_data[C.SORTER_ALBUM_NAME_KEY]), 
                C.SORTER_GENRES_KEY
            ] = genre_data[C.SORTER_GENRES_KEY] 


    def get_next_album_with_unknown_genre(self) -> list:
        """Get an album that doesn't have a genre assignment yet. If all albums are assigned, return None."""

        self.refresh_df()
        albums_with_unknown_genre = self.__get_albums_with_unknown_genre()
        if len(albums_with_unknown_genre) != 0:
            unknown_row = albums_with_unknown_genre.iloc[0]
            return [unknown_row[C.SORTER_ARTISTS_KEY], unknown_row[C.SORTER_ALBUM_NAME_KEY]]
        else: 
            return None


    def get_genre_keywords(self) -> list:
        """Get a list of all genres and all words that appear in more than one genre. Includes an entry for all genres."""

        all_genres = self.__configs.get_genre_playlists_names()
        genre_word_counts = {}

        # Gather words and counts from genres.
        for genre in all_genres:
            for word in genre.split(' '):
                keyword = f"{word}{C.KEYWORD_SUFFIX}"
                if word not in genre_word_counts:
                    genre_word_counts[keyword] = 1
                else:
                    genre_word_counts[keyword] += 1

        # Add words that appear in more than one genre.
        for word, count in genre_word_counts.items():
            if (count > 1):
                all_genres.append(word)

        # Return sorted list of words and genres.
        return [C.ALL_GENRES_NAME] + sorted(all_genres)


    def get_years(self) -> list:
        """Get a list of all years in the album data. Includes an entry for all years."""
        return [C.ALL_YEARS_NAME] + sorted(self.__df[C.SORTER_YEAR_KEY].unique().tolist(), reverse=True)


    def get_album_list(self, year: int, genre_keyword: str) -> str:
        """Get the human-readable list of albums, filtered by year and genre keyword."""

        self.refresh_df()
        df = self.__get_filtered_df(year=year, genre_keyword=genre_keyword)
        return self.__album_data_to_str(df)


    def get_tier_3_tracks(self, year: int) -> str:
        """
        Get a list of all tier 3 tracks in a specific year. 
        If no year is provided, get a list of tier 3 tracks for all years.
        """

        self.refresh_df()
        df = self.__get_filtered_df(year=year)

        # Convert the stringified list of track URIs to a python list.
        all_tier_3_tracks = list(chain.from_iterable(
            df[C.SORTER_TIER_3_TRACKS_KEY].apply(lambda tracks: ast.literal_eval(tracks)).tolist()
        ))

        formatted_tracks = []
        tracks = self.__client.getTracks(track_uris=all_tier_3_tracks)
        for track in tracks:
            formatted_tracks.append([
                ", ".join(list(map(lambda artist: artist[C.NAME_KEY], track[C.ARTISTS_KEY])))[:40], 
                track[C.ALBUM_KEY][C.NAME_KEY][:40], 
                track[C.NAME_KEY][:40]
            ])

        return pd.DataFrame(formatted_tracks).to_markdown()


    def assign_genres_to_album(self, artist_names: str, album_name: str, genres: str) -> None:
        """
        Assign genres to a ranked album if it exists. Do nothing if the album does not exist.

        Args: 
            artist_names (str): The comma-separated list of album artists.
            album_name (str): The name of the album.
            genres_str (str): The comma-separated list of genres for this album.
        """

        # Fetch the album from memory.
        ranked_album = self.__df[
            (self.__df[C.SORTER_ARTISTS_KEY] == artist_names) & 
            (self.__df[C.SORTER_ALBUM_NAME_KEY] == album_name)
        ]

        if not ranked_album.empty:

            # Get a list of genres from the comma-separated string.
            genres_list = list(map(lambda genre: genre.strip(), genres.split(',')))

            # Get the tier 3 tracks from the ranked album.
            track_ids = ast.literal_eval(ranked_album.iloc[0][C.SORTER_TIER_3_TRACKS_KEY])
            
            # Add the tier 3 tracks to the genre playlist for each genre.
            for genre in genres_list:
                self.__add_tracks_to_genre_playlist(track_ids, genre)

            # Record the genre for this ranked album.
            self.__write_genres(artist_names=artist_names, album_name=album_name, genres=genres)


    def add_override(
        self, 
        album_key: str, 
        override_uri: str
    ) -> dict:
        """
        Create an entry to force the ranker to override an album key with the information from a different Spotify album.

        Args:
            album_key (str): The key of the album that needs to be overridden.
            override_uri (str): The Spotify album URI for the album whose highest possible score, name, artists and year should
                replace that of the album referenced by the album key.

        Returns:
            dict: The override data.
        """

        override_data = self.__get_override_data(album_uri=override_uri)
        self.__configs.update_overrides(album_key=album_key, override_data=override_data)
        return override_data
