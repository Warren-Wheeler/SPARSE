from modules.main.ranking.album_ranker import AlbumRanker
import PySimpleGUI as sg
from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient


def run(ranker: AlbumRanker):

    sg.popup_no_titlebar(
        "SPARSE will start fetching your music and ranking it in the background once you close this popup. Another popup " + \
        "will appear when ranking is complete. Until ranking is complete, the sorter window will show data from the most " + \
        "recent completed ranking run."
    )
    ranker.run()
    sg.popup_no_titlebar(
        "SPARSE ranking is complete. New results will now appear in the sorter window."
    )

if __name__ == "__main__":
    configs = SparseConfigs()
    client = SpotifyClient(configs=configs)
    ranker = AlbumRanker(configs=configs, client=client)
    run(ranker=ranker)