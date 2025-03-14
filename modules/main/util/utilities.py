import datetime as dt
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
    try:
        return data[key]
    except KeyError:
        return orElse
    
def get_album_key(artist_names: str, album_name: str) -> str:
    """"""
    return f"{artist_names} - {album_name}"

def remove_suffix_if_exists(word: str, suffix: str):
    """
    Removes the suffix from a word if it exists.

    Args:
        word: The word to remove the suffix from.
        suffix: The suffix to remove.

    Returns:
        The word with the suffix removed, or the original word if the suffixwas not found.
    """

    if word.endswith(suffix):
        return word[:-len(suffix)]
    else:
        return word