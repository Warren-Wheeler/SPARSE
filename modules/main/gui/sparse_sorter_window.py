from modules.main.sorting.album_sorter import AlbumSorter
import modules.main.util.constants as C
import PySimpleGUI as sg
from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient
import modules.main.util.utilities as utilities


def run(sorter: AlbumSorter):
    """Run the album sorter window."""

    # Pre-select an album that doesn't have a genre for the genre entry tab:
    selected_ungenred_album = sorter.get_next_album_with_unknown_genre()
    selected_ungenred_album_key = utilities.get_album_key(
        artist_names=selected_ungenred_album[0], 
        album_name=selected_ungenred_album[1]
    ) if selected_ungenred_album != None else ""

    # Album list tab:
    album_list_tab = [  
        [sg.Titlebar(C.APPLICATION_TITLE)],
        [sg.Text(C.YEAR_TAG)],
        [sg.OptionMenu(sorter.get_years(), default_value=C.ALL_YEARS_NAME, key=C.ALBUM_LIST_YEAR_KEY)],
        [sg.Text(C.GENRE_TAG)],
        [sg.OptionMenu(sorter.get_genre_keywords(), default_value=C.ALL_GENRES_NAME, key=C.ALBUM_LIST_GENRE_KEY)],
        [sg.Button(C.LIST_ALBUMS_TAG)],
        [sg.Output(size=C.DEFAULT_DIMENSIONS, font=(C.DEFAULT_FONT), key=C.ALBUM_LIST_OUTPUT_KEY)]
    ]

    # Tier 3 track list tab:
    tier_3_track_list_view_tab = [
        [sg.Titlebar(C.APPLICATION_TITLE)],
        [sg.Text(C.YEAR_TAG)],
        [sg.OptionMenu(sorter.get_years(), default_value=C.ALL_YEARS_NAME, key=C.TIER_3_LIST_YEAR_KEY)],
        [sg.Button(C.LIST_TIER_3_TAG)],
        [sg.Output(size=C.DEFAULT_DIMENSIONS, font=(C.DEFAULT_FONT), key=C.TIER_3_LIST_OUTPUT_KEY)]
    ]

    # Genre entry/Override entry tab:
    entry_tab = [
        [sg.Titlebar(C.APPLICATION_TITLE)],
        [sg.Text(selected_ungenred_album_key, key=C.UNKNOWN_ALBUM_KEY)],
        [sg.Text(C.SET_GENRE_TAG)],
        [sg.Input(default_text='', key=C.GENRE_INPUT_KEY)],
        [sg.Button(C.CONFIRM_GENRE_TAG)],
        [sg.HorizontalLine()],
        [sg.Text(C.SET_ALBUM_ARTISTS_TAG)],
        [sg.Input(default_text='', key=C.ALBUM_ARTISTS_INPUT_KEY)],
        [sg.Text(C.SET_ALBUM_NAME_TAG)],
        [sg.Input(default_text='', key=C.ALBUM_NAME_INPUT_KEY)],
        [sg.Text(C.SET_OVERRIDE_URI_TAG)],
        [sg.Input(default_text='', key=C.OVERRIDE_URI_INPUT_KEY)],
        [sg.Button(C.CONFIRM_OVERRIDE_TAG)]
    ]

    # Tab layout:
    layout = [
        [sg.TabGroup([[
            sg.Tab(C.ALBUM_LIST_TITLE, album_list_tab), 
            sg.Tab(C.TIER_3_TRACK_LIST_TITLE, tier_3_track_list_view_tab),
            sg.Tab(C.ENTRY_TITLE, entry_tab)
        ]])]
    ]

    # Open window:
    window = sg.Window(C.APPLICATION_TITLE, layout)

    # Event Loop to process events and get the values of the inputs:
    while True:
        event, values = window.read()

        # If tue user closes window:
        if event == sg.WIN_CLOSED:
            break

        # If the user clicks the `list albums` button:
        elif event == C.LIST_ALBUMS_TAG:

            # List the album data using the year and genre filters:
            try:
                year_value = values[C.ALBUM_LIST_YEAR_KEY]
                if year_value == C.ALL_YEARS_NAME:
                    year = None
                else:
                    year = int(year_value)
                genre_value = values[C.ALBUM_LIST_GENRE_KEY]
                if genre_value != C.ALL_GENRES_NAME:
                    genre_keyword = utilities.remove_suffix_if_exists(word=genre_value, suffix=C.KEYWORD_SUFFIX)
                else:
                    genre_keyword = None
                album_list = sorter.get_album_list(year=year, genre_keyword=genre_keyword)
                window[C.ALBUM_LIST_OUTPUT_KEY].update(album_list)

            # Display a helpful error message if the year was invalid:
            except ValueError:
                window[C.ALBUM_LIST_OUTPUT_KEY].update(C.YEAR_ERROR_MESSAGE)
            
        # If the user clicks the `list tier 3 tracks` button:
        elif event == C.LIST_TIER_3_TAG:

            # List the tier 3 tracks for the specified year:
            try:
                year_value = values[C.TIER_3_LIST_YEAR_KEY]
                if year_value == C.ALL_YEARS_NAME:
                    year = None
                else:
                    year = int(year_value)
                tier_3_list = sorter.get_tier_3_tracks(year)
                window[C.TIER_3_LIST_OUTPUT_KEY].update(tier_3_list)

            # Display a helpful error message if the year was invalid.
            except ValueError:
                window[C.TIER_3_LIST_OUTPUT_KEY].update(C.YEAR_ERROR_MESSAGE)

        # If the user clicks the `confirm genre` button:
        elif event == C.CONFIRM_GENRE_TAG:

            # Save the current un-genred album to memory + disk and add the tier three tracks to genre-specific playlists 
            # based on the comma-separated list of genres currently entered into the genre input field.
            genre_input = values[C.GENRE_INPUT_KEY]
            if (len(selected_ungenred_album) == 2) & (genre_input != ""):
                sorter.assign_genres_to_album(
                    artist_names=selected_ungenred_album[0],
                    album_name=selected_ungenred_album[1],
                    genres=genre_input
                )
                selected_ungenred_album = sorter.get_next_album_with_unknown_genre()
                album_key = utilities.get_album_key(artist_names=selected_ungenred_album[0], album_name=selected_ungenred_album[1])
                window[C.UNKNOWN_ALBUM_KEY].update(album_key)

        # If the user clicks the `confirm override` button:
        elif event == C.CONFIRM_OVERRIDE_TAG:

            # Make an entry in memory and disk to override the album currently entered into the artist names & album name 
            # input fields with the data from the album entered into the override uri input field.
            artists_input = values[C.ALBUM_ARTISTS_INPUT_KEY]
            name_input = values[C.ALBUM_NAME_INPUT_KEY]
            override_uri = values[C.OVERRIDE_URI_INPUT_KEY]

            # Only create the override if all inputs are valid.
            if artists_input and name_input and override_uri:

                override = sorter.add_override(album_key=album_key, override_uri=override_uri)

                if override:
                    album_key = utilities.get_album_key(artists_input, name_input)
                    sg.Popup(f"{C.OVERRIDE_ADDED_MESSAGE}\n\n{album_key}:\n{override}")
                else:
                    sg.Popup(C.OVERRIDE_NOT_ADDED_MESSAGE)


    # Close window when loop ends:
    window.close()


if __name__ == "__main__":
    configs = SparseConfigs()
    client = SpotifyClient(configs=configs)
    sorter = AlbumSorter(configs=configs, client=client)
    run(sorter=sorter)
    