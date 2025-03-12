from modules.main.sorting.album_sorter import AlbumSorter
import modules.main.util.constants as C
import PySimpleGUI as sg
from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient

def run(sorter: AlbumSorter):

    # Pre-select an album that doesn't have a genre for the genre entry tab:
    selected_ungenred_album = sorter.get_next_album_with_unknown_genre()

    # Album list tab:
    album_list_tab = [  
        [sg.Titlebar(C.APPLICATION_TITLE)],
        [sg.Text(C.YEAR_TAG)],
        [sg.OptionMenu(sorter.get_years(), default_value=C.ALL_YEARS_NAME, key=C.ALBUM_LIST_YEAR_KEY)],
        [sg.Text(C.GENRE_TAG)],
        [sg.OptionMenu(sorter.get_genres(), default_value=C.ALL_GENRES_NAME, key=C.ALBUM_LIST_GENRE_KEY)],
        [sg.Button(C.LIST_ALBUMS_TAG)],
        [sg.Output(size=C.DEFAULT_DIMENSIONS, font=(C.DEFAULT_FONT), key=C.ALBUM_LIST_OUTPUT_KEY)]
    ]

    # Tier 3 track list tab:
    tier_3_track_list_view_tab = [
        [sg.Titlebar(C.APPLICATION_TITLE)],
        [sg.Text(C.YEAR_TAG)],
        [sg.OptionMenu(sorter.get_years(), default_value=C.ALL_YEARS_NAME, key=C.TIER_3_LIST_YEAR_KEY)],
        [sg.Output(size=C.DEFAULT_DIMENSIONS, font=(C.DEFAULT_FONT), key=C.TIER_3_LIST_OUTPUT_KEY)],
        [sg.Button(C.LIST_TIER_3_TAG)]
    ]

    # Genre entry tab:
    genre_entry_tab = [
        [sg.Titlebar(C.APPLICATION_TITLE)],
        [sg.Text(' - '.join(selected_ungenred_album), key=C.UNKNOWN_ALBUM_KEY)],
        [sg.Text(C.SET_GENRE_TAG)],
        [sg.Input(default_text='', key=C.GENRE_INPUT_KEY)],
        [sg.Button(C.CONFIRM_GENRE_TAG)]
    ]

    # Tab layout:
    layout = [
        [sg.TabGroup([[
            sg.Tab(C.ALBUM_LIST_TITLE, album_list_tab), 
            sg.Tab(C.TIER_3_TRACK_LIST_TITLE, tier_3_track_list_view_tab),
            sg.Tab(C.GENRE_ENTRY_TITLE, genre_entry_tab)
        ]])]
    ]

    # Open window:
    window = sg.Window(C.APPLICATION_TITLE, layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()

        # If user closes window:
        if event == sg.WIN_CLOSED:
            break

        elif event == C.LIST_ALBUMS_TAG:
            try:
                year_value = values[C.ALBUM_LIST_YEAR_KEY]
                if year_value == C.ALL_YEARS_NAME:
                    year = None
                else:
                    year = int(year_value)
                genre_value = values[C.ALBUM_LIST_GENRE_KEY]
                genre_keyword = genre_value if genre_value != C.ALL_GENRES_NAME else None
                album_list = sorter.get_album_list(year=year, genre_keyword=genre_keyword)
                window[C.ALBUM_LIST_OUTPUT_KEY].update(album_list)
            except ValueError:
                window[C.ALBUM_LIST_OUTPUT_KEY].update(C.YEAR_ERROR_MESSAGE)
            
        elif event == C.LIST_TIER_3_TAG:
            try:
                year_value = values[C.TIER_3_LIST_YEAR_KEY]
                if year_value == C.ALL_YEARS_NAME:
                    year = None
                else:
                    year = int(year_value)
                tier_3_list = sorter.get_tier_3_tracks(year)
                window[C.TIER_3_LIST_OUTPUT_KEY].update(tier_3_list)
            except ValueError:
                window[C.TIER_3_LIST_OUTPUT_KEY].update(C.YEAR_ERROR_MESSAGE)

        elif event == C.CONFIRM_GENRE_TAG:
            genre_input = values[C.GENRE_INPUT_KEY]
            if (len(selected_ungenred_album) == 2) & (genre_input != ""):
                sorter.add_genres(
                    artist_names=selected_ungenred_album[0],
                    album_name=selected_ungenred_album[1],
                    genres=genre_input
                )
                selected_ungenred_album = sorter.get_next_album_with_unknown_genre()
                window[C.UNKNOWN_ALBUM_KEY].update(' - '.join(selected_ungenred_album))

    # Close window when loop ends:
    window.close()

if __name__ == "__main__":
    configs = SparseConfigs()
    client = SpotifyClient(configs=configs)
    sorter = AlbumSorter(configs=configs, client=client)
    run(sorter=sorter)
    