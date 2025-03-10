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

def extractYearFromDate(date: str) -> int:
    """Extract the year from a date string."""
    return int(date[:4])

def getSecondsSinceDatetime(t0: dt.datetime) -> float:
    """Get the number of seconds that have passed since a datetime."""
    now = dt.datetime.now()
    return (now-t0).total_seconds()