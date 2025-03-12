
import pandas as pd
import ast
from itertools import chain
from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient
import modules.main.util.constants as C


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
        if (year != None) & (genre_keyword != None):
            return self.__df[
                (self.__df[C.SORTER_YEAR_KEY] == year) & 
                    (self.__df[C.SORTER_GENRE_KEY].str.contains(genre_keyword, na=False))
            ]
        elif year != None:
            return self.__df[self.__df[C.SORTER_YEAR_KEY] == year]
        elif genre_keyword != None:
            return self.__df[self.__df[C.SORTER_GENRE_KEY].str.contains(genre_keyword, na=False)]
        else:
            return self.__df

    def __cleanDF(self, df: pd.DataFrame) -> pd.DataFrame:
        df[C.SORTER_RATING_KEY] = (df[C.SORTER_TOTAL_SCORE_KEY] / df[C.SORTER_HIGHEST_POSSIBLE_SCORE_KEY]) * 100
        df[C.SORTER_ALBUM_NAME_KEY] = df[C.SORTER_ALBUM_NAME_KEY].transform(lambda s: s[:40])
        df[C.SORTER_ARTISTS_KEY] = df[C.SORTER_ARTISTS_KEY].transform(lambda s: s[:40])
        df[C.SORTER_GENRE_KEY] = df[C.SORTER_GENRE_KEY].transform(lambda s: s[:30])
        dropped_df = df.drop([C.SORTER_TOTAL_SCORE_KEY, C.SORTER_HIGHEST_POSSIBLE_SCORE_KEY, C.SORTER_TIER_3_TRACKS_KEY], axis=1) \
            .sort_values(by=C.SORTER_RATING_KEY, ascending=False) \
            .reset_index(drop=True)
        dropped_df.index += 1
        return dropped_df
    
    def __get_albums_with_unknown_genre(self) -> pd.DataFrame:
        return self.__df[self.__df[C.SORTER_GENRE_KEY] == C.UNKNOWN_GENRE_NAME]
    
    def __add_tracks_to_genre_playlist(self, tracks_ids: list, genre: str) -> None:
        if tracks_ids != []:
            playlistFromFile = self.__configs.get_genre_playlist_by_name(name=genre)
            if playlistFromFile:
                playlist_uri = playlistFromFile[C.URI_KEY]
            else:
                playlist_uri = self.__client.createUserPlaylist(playlist_title=genre)
                self.__configs.update_playlist_data(genre=genre, playlist_id=playlist_uri)

            self.__client.addPlaylistItems(playlist_id=playlist_uri, tracks=tracks_ids)
            
    def __write_genres(self, artist_names: str, album_name: str, genres) -> None:
        self.__configs.update_genre_data(
            album_key=f"{artist_names} - {album_name}", #TODO
            genre_data={
                C.SORTER_ARTISTS_KEY: artist_names,
                C.SORTER_ALBUM_NAME_KEY: album_name,
                C.SORTER_GENRES_KEY: genres
            }
        )
        
    def refresh_df(self):
        self.__df = pd.read_csv(self.__configs.get_ranker_output_path())
        self.__df[C.SORTER_GENRE_KEY] = C.UNKNOWN_GENRE_NAME
        for key in self.__configs.get_genred_album_keys():
            genre_data = self.__configs.get_ranked_album_genres_by_album_key(key)
            self.__df.loc[
                (self.__df[C.SORTER_ARTISTS_KEY] == genre_data[C.SORTER_ARTISTS_KEY]) & 
                    (self.__df[C.SORTER_ALBUM_NAME_KEY] == genre_data[C.SORTER_ALBUM_NAME_KEY]), 
                C.SORTER_GENRE_KEY
            ] = genre_data[C.SORTER_GENRE_KEY] 

    def get_next_album_with_unknown_genre(self) -> list:
        albums_with_unknown_genre = self.__get_albums_with_unknown_genre()
        if len(albums_with_unknown_genre) != 0:
            unknown_row = albums_with_unknown_genre.iloc[0]
            return [unknown_row[C.SORTER_ARTISTS_KEY], unknown_row[C.SORTER_ALBUM_NAME_KEY]]
        else: 
            return []

    def get_genres(self) -> list:
        # TODO

        all_genres = self.__configs.get_genre_playlists_names()
        genre_word_counts = {}

        # Gather words and counts from genres.
        for genre in all_genres:
            for word in genre.split(' '):
                if word not in genre_word_counts:
                    genre_word_counts[word] = 1
                else:
                    genre_word_counts[word] += 1

        # Add words that appear in more than one genre.
        for word, count in genre_word_counts.items():
            if (count > 1):
                all_genres.append(word)

        # Return sorted list of words and genres.
        return [C.ALL_GENRES_NAME] + sorted(all_genres)

    def get_years(self) -> list:
        return [C.ALL_YEARS_NAME] + sorted(self.__df[C.SORTER_YEAR_KEY].unique().tolist(), reverse=True)

    def get_album_list(self, year: int, genre_keyword: str) -> str:
        self.refresh_df()
        df = self.__get_filtered_df(year=year, genre_keyword=genre_keyword)
        return self.__cleanDF(df).to_markdown()

    def get_tier_3_tracks(self, year: int) -> str:
        self.refresh_df()
        df = self.__get_filtered_df(year=year)
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

    def add_genres(self, artist_names: str, album_name: str, genres: str) -> None:

        genres = list(map(lambda genre: genre.strip(), genres.split(',')))
        track_ids = ast.literal_eval(self.__df[
            (self.__df[C.SORTER_ARTISTS_KEY] == artist_names) & 
            (self.__df[C.SORTER_ALBUM_NAME_KEY] == album_name)
        ].iloc[0][C.SORTER_TIER_3_TRACKS_KEY])
        
        for genre in genres:
            self.__add_tracks_to_genre_playlist(track_ids, genre)

        self.__write_genres(artist_names=artist_names, album_name=album_name, genres=genres)