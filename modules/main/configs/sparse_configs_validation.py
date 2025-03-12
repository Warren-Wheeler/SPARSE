import modules.main.util.constants as C


class SparseConfigsException(Exception):
    """An exception that is thrown when there is a problem with validating the configs file."""
    pass

def raise_exception_if_issues_exist(issues: list, configs_file_path: str) -> None:
    """Throw an exception if there are issues with the config file."""
    if issues:
        issuesString = f"The following issues were found with the Album Ranker config file ({configs_file_path}):"
        for issue in issues: issuesString += f"\n\t{issue}"
        raise SparseConfigsException(issuesString)
    
def check_key(
    configs: dict, 
    key: str, 
    expected_type: type, 
    expected_suffix: str, 
    issues: list
) -> None:
    """
    Check a key to make sure it exists in the configs, matches the expected type and ends with the expected suffix. If a key is
    missing or doesn't match the expected type, append a detailed message about it to the issues list.

    Args:
        configs (dict): The Sparse configs.
        key (str): The key we're checking.
        expected_type (type): The type the key should be.
        expected_suffix (str): The string the key should end with.
        issues (list): The list of issues found in the configs.
    """
    if key not in configs:
        issues.append(f"No `{key}` detected in Sparse configs.")
    elif not isinstance(configs[key], expected_type):
        issues.append(f"`{key}` in Sparse configs must be a `{expected_type.__name__}`.")
    elif isinstance(configs[key], str) and not configs[key]:
        issues.append(f"`{key}` in Sparse configs must not be empty.")
    elif expected_suffix and not f"{configs[key]}".lower().endswith(expected_suffix):
        issues.append(f"`{key}` in Sparse configs did not end with expected suffix `{expected_suffix}`.")

def validate(configs: dict, configs_file_path: str) -> None:
    """
    Validates the parsed configs. Throws a detailed exception if there are issues with the configs.

    Args:
        configs (dict): The parsed configs.
        configs_file_path (str): The path to the configs file.
    """
    issues = []

    # Check the config dict to make sure the expected keys exist, have the expected type and have the expected suffix.
    keys_types_and_suffixes = [
        (C.ALBUM_LENGTH_THRESHOLD_MIN_KEY, int, None),
        (C.CLIENT_ID_KEY, str, None),
        (C.CLIENT_SECRET_KEY, str, None),
        (C.GENRE_PLAYLISTS_FILE_PATH_KEY, str, C.JSON_EXTENSION),
        (C.RANKED_ALBUM_GENRES_FILE_PATH_KEY, str, C.JSON_EXTENSION),
        (C.RANKER_OVERRIDE_FILE_PATH_KEY, str, C.JSON_EXTENSION),
        (C.RANKER_OUTPUT_FILE_PATH_KEY, str, C.CSV_EXTENSION),
        (C.TIER_1_PLAYLIST_ID_KEY, str, None),
        (C.TIER_2_PLAYLIST_ID_KEY, str, None),
        (C.TIER_3_PLAYLIST_ID_KEY, str, None),
        (C.TIER_3_YEARLY_THRESHOLD_KEY, int, None),
        (C.USER_KEY, str, None)
    ]
    
    for key, expected_type, expected_suffix in keys_types_and_suffixes:
        check_key(
            configs=configs, 
            key=key, 
            expected_type=expected_type, 
            expected_suffix=expected_suffix,
            issues=issues
        )
    raise_exception_if_issues_exist(issues=issues, configs_file_path=configs_file_path)

    # Extra validation:
    if (configs[C.TIER_3_YEARLY_THRESHOLD_KEY] <= 0):
        issues.append("Tier 3 yearly threshold must be greater than 0. Please check configs ({configs_file_path}).")
    if (configs[C.ALBUM_LENGTH_THRESHOLD_MIN_KEY] <= 0):
        issues.append("Album length threshold must be greater than 0. Please check configs ({configs_file_path}).")
    raise_exception_if_issues_exist(issues=issues, configs_file_path=configs_file_path)
