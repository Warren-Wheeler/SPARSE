import modules.main.util.constants as C
import unittest
import modules.main.configs.sparse_configs_validation as validation


class TestSparseConfigsValidation(unittest.TestCase):


    def setUp(self):
        """Setup for unit tests."""
        self.configs_file_path = "test"


    def test_raise_exception_if_issues_exist(self):
        """Test raise_exception_if_issues_exist()."""

        # Single issue should raise SparseConfigsException.
        with self.assertRaises(validation.SparseConfigsException):
            validation.raise_exception_if_issues_exist(issues=["issue"], configs_file_path=self.configs_file_path)

        # Multiple issues should raise SparseConfigsException.
        with self.assertRaises(validation.SparseConfigsException):
            validation.raise_exception_if_issues_exist(issues=["issue1", "issue2", "issue3"], configs_file_path=self.configs_file_path)

        # Empty issues should raise no exception.
        try:
            validation.raise_exception_if_issues_exist(issues=[], configs_file_path=self.configs_file_path)
        except validation.SparseConfigsException:
            self.fail("raise_exception_if_issues_exist() raised SparseConfigsException unexpectedly.")


    def test_check_key(self):
        """Test check_key()."""

        # Mock configs & issues.
        configs = {
            "config1": 1,
            "config2": "2",
            "config3": "3.csv",
            "config4": ""
        }
        issues = []

        keys_expected_types_expected_suffixes_and_expectations = [
            # No issues should be added if the checked key exists in the configs and matches the expected type/expected suffix.
            ("config1", int, None, 0),
            # One issue should be added if the checked key exists in the configs and doesn't match the expected type.
            ("config2", int, None, 1),
            # One issue should be added if the checked key exists in the configs and doesn't match the expected suffix.
            ("config3", str, ".json", 2),
            # No issues should be added if the checked key exists in the configs and matches the expected type/expected suffix.
            ("config3", str, ".csv", 2),
            # One issue should be added if the checked key is an empty string.
            ("config4", str, None, 3),
            # One issue should be added if the checked key doesn't exist in the configs.
            ("config5", str, None, 4)
        ]

        for key, expected_type, expected_suffix, expectation in keys_expected_types_expected_suffixes_and_expectations:
            validation.check_key(
                configs=configs,
                key=key,
                expected_type=expected_type,
                expected_suffix=expected_suffix,
                issues=issues
            )
            self.assertEqual(len(issues), expectation)


    def test_validate(self):
        """Test validate()."""

        # Create mock configs.
        valid_configs = {
            "user": "test",
            "client_id": "test",
            "client_secret": "test",
            "tier_3_playlist_id": "test",
            "tier_2_playlist_id": "test",
            "tier_1_playlist_id": "test",
            "ranker_override_file_path": "./res/override.JSON",
            "ranker_output_file_path": "./res/albums.CSV",
            "ranked_album_genres_file_path": "./res/genres.json",
            "genre_playlists_file_path": "./res/playlists.json",
            "tier_3_yearly_threshold": 250,
            "album_length_threshold_min": 20
        }

        configs = valid_configs

        # Valid configs should pass validation.
        try:
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)
        except validation.SparseConfigsException:
            self.fail("validate() raised SparseConfigsException unexpectedly.")

        # Missing key should raise SparseConfigsException.
        del configs[C.CLIENT_ID_KEY]
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Mismatched key type should raise SparseConfigsException.
        configs = valid_configs
        configs[C.CLIENT_ID_KEY] = 0
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Empty string key should raise SparseConfigsException.
        configs = valid_configs
        configs[C.CLIENT_ID_KEY] = ""
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)
        configs = valid_configs
        configs[C.CLIENT_ID_KEY] = None
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Override file must be JSON.
        configs = valid_configs
        configs[C.RANKER_OVERRIDE_FILE_PATH_KEY] = "./res/override.csv"
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Output file must be CSV.
        configs = valid_configs
        configs[C.RANKER_OUTPUT_FILE_PATH_KEY] = "./res/albums.json"
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Override file must be JSON.
        configs = valid_configs
        configs[C.RANKED_ALBUM_GENRES_FILE_PATH_KEY] = "./res/genres.csv"
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Output file must be JSON.
        configs = valid_configs
        configs[C.GENRE_PLAYLISTS_FILE_PATH_KEY] = "./res/playlists.csv"
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Tier 3 yearly threshold must be greater than 0.
        configs = valid_configs
        configs[C.TIER_3_YEARLY_THRESHOLD_KEY] = -1
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)
        configs = valid_configs
        configs[C.TIER_3_YEARLY_THRESHOLD_KEY] = 0
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)

        # Album lenth threshold must be greater than 0.
        configs = valid_configs
        configs[C.ALBUM_LENGTH_THRESHOLD_MIN_KEY] = -1
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)
        configs = valid_configs
        configs[C.ALBUM_LENGTH_THRESHOLD_MIN_KEY] = 0
        with self.assertRaises(validation.SparseConfigsException):
            validation.validate(configs=configs, configs_file_path=self.configs_file_path)


if __name__ == '__main__':
    unittest.main()