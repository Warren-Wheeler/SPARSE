from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient
from modules.main.ranking.album_ranker import AlbumRanker
from modules.main.sorting.album_sorter import AlbumSorter
from modules.main.gui.sparse_ranker_popup import SparseRankerPopup
from modules.main.gui.sparse_sorter_window import SparseSorterWindow
from multiprocessing import Process
import time

configs = SparseConfigs()
client = SpotifyClient(configs=configs)
ranker = AlbumRanker(configs=configs, client=client)
ranker_popup = SparseRankerPopup(ranker=ranker)
sorter = AlbumSorter(configs=configs, client=client)
sorter_window = SparseSorterWindow(sorter=sorter)

if __name__ == "__main__":
    p1 = Process(target=sorter_window.run)
    p2 = Process(target=ranker_popup.run)

    p1.start()

    # Start p2 one second after p1 to ensure that the pop-up appears on top of the window.
    time.sleep(1)
    p2.start()

    p1.join()
    p2.join()

    print("Done!")