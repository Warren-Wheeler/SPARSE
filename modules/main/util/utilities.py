import datetime as dt
from difflib import SequenceMatcher
import json


def read_json_file(file_path: str) -> dict:
    """
    Read a JSON file and returns the data as a Python dictionary.

    Parameters:
        file_path (str): The path to the file.

    Returns:
        dict: The data from the JSON file as a Python dictionary. If no file is found or if the JSON is malformed, throw a detailed exception.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Error: Invalid JSON format in {file_path}")


def extract_year_from_date(date: str) -> int:
    """Extract the year from a date string. Strips whitespace."""
    try:
        return int(date.lstrip()[:4])
    except ValueError:
        raise ValueError(f"Error: Invalid date format {date}.")


def get_seconds_since_datetime(t0: dt.datetime) -> float:
    """Get the number of seconds that have passed since a datetime."""
    now = dt.datetime.now()
    return (now-t0).total_seconds()


def get(data: dict, key: any, orElse: any = None):
    """Get a key from a dict. Return the `orElse` value if the requested key is missing."""
    try:
        return data[key]
    except KeyError:
        return orElse
    

def get_album_key(artist_names: str, album_name: str) -> str:
    """Get the album key for an album."""
    return f"{artist_names} - {album_name}"
    

def get_clean_genres_list(genres_string: str) -> list:
    """Get a list of stripped, capitalized genres from a comma-separated list."""
    return list(map(lambda genre: genre.strip().title(), genres_string.split(',')))


def get_string_similarity(s1: str, s2: str) -> float:
    """
    Get the similarity between two strings.

    Args:
        s1: The first string.
        s2: The second string.

    Returns:
        The similarity between the two strings, as a float between 0 and 1.
    """
    return SequenceMatcher(None, s1, s2).ratio()
