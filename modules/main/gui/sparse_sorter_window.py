from modules.main.sorting.album_sorter import AlbumSorter
import modules.main.util.constants as C
import PySimpleGUI as sg
from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient
import modules.main.util.utilities as utilities

class SparseSorterWindow:
    """The main window for the Sparse Sorter application."""

    # The currently selected ungenred album. None until refreshed.
    __selected_ungenred_album = None 

    def __refresh_selected_album(self) -> None:
        """Refresh the selected ungenred album."""
        self.__selected_ungenred_album = self.__sorter.get_next_album_with_unknown_genre()
        if (self.__selected_ungenred_album != None):
            if (len(self.__selected_ungenred_album) == 2):
                album_key = utilities.get_album_key(
                    artist_names=self.__selected_ungenred_album[0], 
                    album_name=self.__selected_ungenred_album[1]
                )
                self.__window[C.UNKNOWN_ALBUM_KEY].update(album_key)
            else:
                self.__window[C.UNKNOWN_ALBUM_KEY].update(C.END_OF_LIST)
        else:
            self.__window[C.UNKNOWN_ALBUM_KEY].update(C.END_OF_LIST)


    def __init__(self, sorter: AlbumSorter):
        """Initialize the Sparse Sorter window."""
        self.__sorter = sorter

        # Album list tab:
        self.__album_list_tab = [
            [sg.Titlebar(C.APPLICATION_TITLE)],
            [sg.Text(C.YEAR_TAG)],
            [sg.OptionMenu(self.__sorter.get_years(), default_value=C.ALL_YEARS_NAME, key=C.ALBUM_LIST_YEAR_KEY)],
            [sg.Text(C.GENRE_TAG)],
            [sg.OptionMenu(self.__sorter.get_genre_keywords(), default_value=C.ALL_GENRES_NAME, key=C.ALBUM_LIST_GENRE_KEY)],
            [sg.Button(C.LIST_ALBUMS_TAG)],
            [sg.Output(size=C.DEFAULT_DIMENSIONS, font=(C.DEFAULT_FONT), key=C.ALBUM_LIST_OUTPUT_KEY)]
        ]

        # Tier 3 track list tab:
        self.__tier_3_track_list_view_tab = [
            [sg.Titlebar(C.APPLICATION_TITLE)],
            [sg.Text(C.YEAR_TAG)],
            [sg.OptionMenu(self.__sorter.get_years(), default_value=C.ALL_YEARS_NAME, key=C.TIER_3_LIST_YEAR_KEY)],
            [sg.Button(C.LIST_TIER_3_TAG)],
            [sg.Output(size=C.DEFAULT_DIMENSIONS, font=(C.DEFAULT_FONT), key=C.TIER_3_LIST_OUTPUT_KEY)]
        ]

        # Genre entry/Override entry tab:
        self.__entry_tab = [
            [sg.Titlebar(C.APPLICATION_TITLE)],
            # We will set this later using the refresh_selected_album function.
            [sg.Text("", key=C.UNKNOWN_ALBUM_KEY)], 
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
        self.__layout = [
            [sg.TabGroup([[
                sg.Tab(C.ALBUM_LIST_TITLE, self.__album_list_tab), 
                sg.Tab(C.TIER_3_TRACK_LIST_TITLE, self.__tier_3_track_list_view_tab),
                sg.Tab(C.ENTRY_TITLE, self.__entry_tab)
            ]])]
        ]


    def run(self) -> None:
        """Run the album sorter window."""

        # Open window:
        self.__window = sg.Window(title=C.APPLICATION_TITLE, layout=self.__layout, finalize=True)

        # Refresh selected ungenred album:
        self.__refresh_selected_album()

        # Event Loop to process events and get the values of the inputs:
        while True:
            event, values = self.__window.read()

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
                    if genre_value == C.ALL_GENRES_NAME:
                        genre = None
                    else:
                        genre = genre_value

                # Display a helpful error message if the year was invalid:
                except ValueError:
                    self.__window[C.ALBUM_LIST_OUTPUT_KEY].update(C.YEAR_ERROR_MESSAGE)

                album_list = self.__sorter.get_album_list(year=year, genre=genre)
                self.__window[C.ALBUM_LIST_OUTPUT_KEY].update(album_list)
                
            # If the user clicks the `list tier 3 tracks` button:
            elif event == C.LIST_TIER_3_TAG:

                # List the tier 3 tracks for the specified year:
                try:
                    year_value = values[C.TIER_3_LIST_YEAR_KEY]
                    if year_value == C.ALL_YEARS_NAME:
                        year = None
                    else:
                        year = int(year_value)
                    tier_3_list = self.__sorter.get_tier_3_tracks(year)
                    self.__window[C.TIER_3_LIST_OUTPUT_KEY].update(tier_3_list)

                # Display a helpful error message if the year was invalid.
                except ValueError:
                    self.__window[C.TIER_3_LIST_OUTPUT_KEY].update(C.YEAR_ERROR_MESSAGE)

            # If the user clicks the `confirm genre` button:
            elif event == C.CONFIRM_GENRE_TAG:

                # Save the current un-genred album to memory + disk and add the tier three tracks to genre-specific playlists 
                # based on the comma-separated list of genres currently entered into the genre input field.
                genre_input = values[C.GENRE_INPUT_KEY]
                if (self.__selected_ungenred_album != None) & (genre_input != ""):
                    if len(self.__selected_ungenred_album) == 2:

                        cleaned_genres = utilities.get_clean_genres_list(genres_string=genre_input)
                        validated_genres = []
                        for cleaned_genre in cleaned_genres:
                            validated_genres.append(cleaned_genre)
                            for potential_match in self.__sorter.get_similar_genres(genre=cleaned_genre):
                                sg.set_options(font=C.DEFAULT_FONT)
                                choice, _ = sg.Window(
                                    "Which Genre?", 
                                    [[sg.T(f"You typed `{cleaned_genre}`, but we found that `{potential_match}` already exists in the database. Did you actually mean `{potential_match}`?")], [sg.Yes(s=10), sg.No(s=10)]], 
                                    disable_close=True
                                ).read(close=True) 

                                if choice == "Yes":
                                    validated_genres.pop()
                                    validated_genres.append(potential_match)
                                    break

                        self.__sorter.assign_genres_to_album(
                            artist_names=self.__selected_ungenred_album[0],
                            album_name=self.__selected_ungenred_album[1],
                            genres_list=validated_genres
                        )
                        self.__refresh_selected_album()

            # If the user clicks the `confirm override` button:
            elif event == C.CONFIRM_OVERRIDE_TAG:

                # Make an entry in memory and disk to override the album currently entered into the artist names & album name 
                # input fields with the data from the album entered into the override uri input field.
                artists_input = values[C.ALBUM_ARTISTS_INPUT_KEY]
                name_input = values[C.ALBUM_NAME_INPUT_KEY]
                override_uri = values[C.OVERRIDE_URI_INPUT_KEY]

                # Only create the override if all inputs are valid.
                if artists_input and name_input and override_uri:

                    override = self.__sorter.add_override(album_key=album_key, override_uri=override_uri)

                    if override:
                        album_key = utilities.get_album_key(artists_input, name_input)
                        sg.Popup(f"{C.OVERRIDE_ADDED_MESSAGE}\n\n{album_key}:\n{override}")
                    else:
                        sg.Popup(C.OVERRIDE_NOT_ADDED_MESSAGE)


        # Close window when loop ends:
        self.__window.close()


if __name__ == "__main__":
    configs = SparseConfigs()
    client = SpotifyClient(configs=configs)
    sorter = AlbumSorter(configs=configs, client=client)
    window = SparseSorterWindow(sorter=sorter)
    window.run()
    