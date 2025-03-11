import modules.main.util.constants as constants


class SparseConfigsException(Exception):
    """An exception that is thrown when there is a problem with validating the configs file."""
    pass

def raise_exception_if_issues_exist(issues: list, configs_file_path: str) -> None:
    """Throw an exception if there are issues with the config file."""
    if issues:
        issuesString = f"The following issues were found with the Album Ranker config file ({configs_file_path}):"
        for issue in issues: issuesString += f"\n\t{issue}"
        raise SparseConfigsException(issuesString)
    
def check_key(configs: dict, key: str, expected_type: type, issues: list) -> None:
    """
    Check a key to make sure it exists in the configs and matches the expected type. If a key is
    missing or doesn't match the expected type, append a detailed message about it to the issues list.
    """
    if key not in configs:
        issues.append(f"No `{key}` detected in Album Ranker configs.")
    elif not isinstance(configs[key], expected_type):
        issues.append(f"`{key}` in Album Ranker configs must be a `{expected_type.__name__}`.")
    elif isinstance(configs[key], str) and not configs[key]:
        issues.append(f"`{key}` in Album Ranker configs must not be empty.")

def validate(configs: dict, configs_file_path: str) -> None:
    """
    Validates the parsed configs. Throws a detailed exception if there are issues with the configs.

    Args:
        configs (dict): The parsed configs.
        configs_file_path (str): The path to the configs file.
    """
    issues = []

    # Check the config dict to make sure the expected keys exist and have the expected type.
    keys_and_types = [
        (constants.CLIENT_ID_KEY, str),
        (constants.CLIENT_SECRET_KEY, str),
        (constants.TIER_3_PLAYLIST_ID_KEY, str),
        (constants.TIER_2_PLAYLIST_ID_KEY, str),
        (constants.TIER_1_PLAYLIST_ID_KEY, str),
        (constants.OVERRIDE_FILE_PATH_KEY, str),
        (constants.RANKER_OUTPUT_PATH_KEY, str),
        (constants.TIER_3_YEARLY_THRESHOLD_KEY, int),
        (constants.ALBUM_LENGTH_THRESHOLD_MIN_KEY, int)
    ]
    
    for key, expected_type in keys_and_types:
        check_key(configs, key, expected_type, issues)
    raise_exception_if_issues_exist(issues=issues, configs_file_path=configs_file_path)

    # Extra validation:
    if not configs[constants.OVERRIDE_FILE_PATH_KEY].lower().endswith(constants.JSON_EXTENSION): 
        issues.append(f"Album Ranker override file must be a {constants.JSON_EXTENSION} file. Please check configs ({configs_file_path}).") 
    if not configs[constants.RANKER_OUTPUT_PATH_KEY].lower().endswith(constants.CSV_EXTENSION): 
        issues.append(f"Album Ranker output file must be a {constants.CSV_EXTENSION} file. Please check configs ({configs_file_path}).") 
    if (configs[constants.TIER_3_YEARLY_THRESHOLD_KEY] <= 0):
        issues.append("Tier 3 yearly threshold must be greater than 0. Please check configs ({configs_file_path}).")
    if (configs[constants.ALBUM_LENGTH_THRESHOLD_MIN_KEY] <= 0):
        issues.append("Album length threshold must be greater than 0. Please check configs ({configs_file_path}).")
    raise_exception_if_issues_exist(issues=issues, configs_file_path=configs_file_path)
