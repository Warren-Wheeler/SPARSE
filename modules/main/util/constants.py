# Config file key names:
ALBUM_LENGTH_THRESHOLD_MIN_KEY = "album_length_threshold_min"
CLIENT_ID_KEY = "client_id"
CLIENT_SECRET_KEY = "client_secret"
GENRE_PLAYLISTS_FILE_PATH_KEY = "genre_playlists_file_path"
RANKER_OVERRIDE_FILE_PATH_KEY = "ranker_override_file_path"
RANKED_ALBUM_GENRES_FILE_PATH_KEY = "ranked_album_genres_file_path"
RANKER_OUTPUT_FILE_PATH_KEY = "ranker_output_file_path"
TIER_1_PLAYLIST_ID_KEY = "tier_1_playlist_id"
TIER_2_PLAYLIST_ID_KEY = "tier_2_playlist_id"
TIER_3_PLAYLIST_ID_KEY = "tier_3_playlist_id"
TIER_3_YEARLY_THRESHOLD_KEY = "tier_3_yearly_threshold"
USER_KEY = "user"

# Spotify JSON response key names:
ALBUM_KEY = "album"
ARTISTS_KEY = "artists"
DURATION_MS_KEY = "duration_ms"
HIGHEST_POSSIBLE_SCORE_KEY = "highest_possible_score"
ITEMS_KEY = "items"
NAME_KEY = "name"
RELEASE_DATE_KEY = "release_date"
TRACK_KEY = "track"
TRACKS_KEY = "tracks"
URI_KEY = "uri"
YEAR_KEY = "year"

# Sorting key names:
SORTER_ALBUM_NAME_KEY = "Album Name"
SORTER_ARTISTS_KEY = "Artists"
SORTER_GENRE_KEY = "Genre"
SORTER_GENRES_KEY = "Genres"
SORTER_HIGHEST_POSSIBLE_SCORE_KEY = "Highest Possible Score"
SORTER_RATING_KEY = "Rating"
SORTER_TIER_3_TRACKS_KEY = "Tier 3 Tracks"
SORTER_TOTAL_SCORE_KEY = "Total Score"
SORTER_YEAR_KEY = "Year"

# Ranking constants:
OUTPUT_FILE_COLUMN_NAMES = f"{SORTER_ARTISTS_KEY}," + \
    f"{SORTER_ALBUM_NAME_KEY}," + \
    f"{SORTER_YEAR_KEY}," + \
    f"{SORTER_TOTAL_SCORE_KEY}," + \
    f"{SORTER_HIGHEST_POSSIBLE_SCORE_KEY}," + \
    f"{SORTER_TIER_3_TRACKS_KEY}"

# Sorting constants:
ALL_GENRES_NAME = "All Genres"
ALL_YEARS_NAME = "All Years"
KEYWORD_SUFFIX = " (word)"
UNKNOWN_GENRE_NAME = "UNK"
GENRE_SIMILARITY_THRESHOLD = 0.7
END_OF_LIST = "End of list."

# Sorter GUI constants:
ALBUM_ARTISTS_INPUT_KEY = "-ALBUM_ARTISTS_INPUT-"
ALBUM_NAME_INPUT_KEY = "-ALBUM_NAME_INPUT-"
ALBUM_LIST_GENRE_KEY = "-ALBUM_LIST_GENRE-"
ALBUM_LIST_OUTPUT_KEY = "-DEFAULT_FONT-"
ALBUM_LIST_TITLE = "Album List"
ALBUM_LIST_YEAR_KEY = "-ALBUM_LIST_YEAR-"
APPLICATION_TITLE = "SPARSE (Spotify Python Album Ranking and Sorting Engine)"
CONFIRM_GENRE_TAG = "Confirm Genre"
CONFIRM_OVERRIDE_TAG = "Confirm Override"
DEFAULT_FONT = "Courier 14"
DEFAULT_HEIGHT = 40
DEFAULT_WIDTH = 175
DEFAULT_DIMENSIONS = (DEFAULT_WIDTH, DEFAULT_HEIGHT)
ENTRY_TITLE = "Entry"
GENRE_INPUT_KEY = "-GENRE_INPUT-"
GENRE_TAG = "Genre:"
LIST_ALBUMS_TAG = "List Albums"
LIST_TIER_3_TAG = "List Tier 3"
NOTICE_TAG = "Notice:"
OVERRIDE_ADDED_MESSAGE = "Override added:"
OVERRIDE_NOT_ADDED_MESSAGE = "Invalid Spotify album link. Override not added."
OVERRIDE_URI_INPUT_KEY = "-OVERRIDE_URI_INPUT-"
POPUP_FONT = "Courier 18"
SET_ALBUM_ARTISTS_TAG = "Set Album Artists:"
SET_ALBUM_NAME_TAG = "Set Album Name:"
SET_OVERRIDE_URI_TAG = "Set Override URI:"
SET_GENRE_TAG = "Set Genre:"
TIER_3_LIST_OUTPUT_KEY="-TIER_3_LIST_OUTPUT-"
TIER_3_LIST_YEAR_KEY="-TIER_3_LIST_YEAR-"
TIER_3_TRACK_LIST_TITLE = "Tier 3 Tracks"
UNKNOWN_ALBUM_KEY = "UNK_ALBUM"
YEAR_ERROR_MESSAGE = f"Year must be an integer or `{ALL_YEARS_NAME}`."
YEAR_TAG = "Year:"

# File extensions:
CSV_EXTENSION = ".csv"
JSON_EXTENSION = ".json"

# Utility constants:
QUESTION_MARK = "?"
SLASH = "/"
SPOTIFY_ALBUM_URI_PREFIX = "spotify:album:"