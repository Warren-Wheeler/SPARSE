from modules.main.configs.sparse_configs import SparseConfigs
from modules.main.spotify.spotify_client import SpotifyClient
from modules.main.ranking.album_ranker import AlbumRanker
from modules.main.sorting.album_sorter import AlbumSorter
import modules.main.gui.sparse_ranker_popup as RankerPopup
import modules.main.gui.sparse_sorter_window as SorterWindow
from multiprocessing import Process
import time

configs = SparseConfigs()
client = SpotifyClient(configs=configs)
ranker = AlbumRanker(configs=configs, client=client)
sorter = AlbumSorter(configs=configs, client=client)

if __name__ == "__main__":
    p1 = Process(target=SorterWindow.run, args=(sorter,))
    p2 = Process(target=RankerPopup.run, args=(ranker,))

    p1.start()

    # Start p2 one second after p1 to ensure that the pop-up appears on top of the window.
    time.sleep(1)
    p2.start()

    p1.join()
    p2.join()

    print("Done!")