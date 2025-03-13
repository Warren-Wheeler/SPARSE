# SPARSE (Spotify Python Album Ranking and Sorting Engine)

## Overview
SPARSE is a Python-based application that fetches, ranks, and sorts albums from Spotify. It allows users to categorize albums based on genre, manage playlists, and apply ranking algorithms to determine the best albums based on track scores.

## Features
- Fetch albums and tracks from Spotify using the Spotify API.
- Rank albums based on track scores and tiered playlist placements.
- Sort albums by genre and year.
- Manage playlist overrides and track updates.
- GUI interface for easy interaction and album management.

## Installation

### Prerequisites
- Python 3.x
- Spotify Developer Account
- Required Python packages (install using the command below)

### Setup
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd sparse-album-ranker
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your Spotify credentials:
   - Update `config.json` with your Spotify `client_id` and `client_secret`.
   
## Usage

### Running SPARSE
```bash
python sparse.py
```

### Running just the Ranker
```bash
python -m modules.main.ranking.album_ranker
```

### Running just the Sorter
```bash
python -m modules.main.sorting.album_sorter
```

### Updating Genres & Overrides
- Use the GUI to assign genres to albums.
- Use the GUI to assign custom album ranking overrides.

## File Structure
```
modules/
  ├── main/
  │   ├── configs/              # Configuration management
  │   ├── ranking/              # Album ranking logic
  │   |   ├── album_ranker.py   # Ranker script
  │   ├── sorting/              # Album sorting logic
  │   |   ├── album_sorter.py   # Sorter script
  │   ├── spotify/              # Spotify API interactions
  │   ├── util/                 # Utility functions
sparse.py                       # Main program
```

## Contributing
Feel free to submit issues or pull requests to improve the functionality and add new features.

## License
This project is licensed under the GNU GPLv3 License (GPL-3.0).
