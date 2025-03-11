import unittest
import modules.main.spotify.spotify_utilities as spotify_utilities


class TestSpotifyUtilities(unittest.TestCase):
    def setUp(self):
        self.spotify_artist_1 = {
            "name": "Kendrick Lamar"
        }
        self.spotify_artist_2 = {
            "name": "Charli xcx"
        }
        self.spotify_artist_3 = {
            "name": "Tame Impala"
        }
        self.spotify_artist_4 = {
            "name": "James Blake"
        }
        self.spotify_artist_5 = {
            "name": ""
        }
        self.spotify_album_1 = {
            "artists": [self.spotify_artist_1]
        }
        self.spotify_album_2 = {
            "artists": [self.spotify_artist_1, self.spotify_artist_2]
        }
        self.spotify_album_3 = {
            "artists": [self.spotify_artist_3, self.spotify_artist_4]
        }
        self.spotify_album_4 = {
            "artists": [self.spotify_artist_5]
        }
        self.spotify_album_5 = {
            "artists": []
        }
        self.spotify_track_1 = {
            "name": "!!!!!!!",
            "duration_ms": 13000
        }
        self.spotify_track_2 = {
            "name": "U-Love",
            "duration_ms": 60000
        }
        self.spotify_track_3 = {
            "name": "Not Like Us",
            "duration_ms": 274000
        }
        self.spotify_track_4 = {
            "name": "Stairway to Heaven - Remaster",
            "duration_ms": 482000
        }
        self.spotify_track_5 = {
            "name": "",
            "duration_ms": 0
        }
        self.spotify_album_tracks = [
            self.spotify_track_1, 
            self.spotify_track_2, 
            self.spotify_track_3, 
            self.spotify_track_4, 
            self.spotify_track_5
        ]

    def test_is_valid_tier(self):
        """Test is_valid_tier()."""

        # Only tiers 1, 2 and 3 should be valid.
        tiers_and_expectations = [
            (-100, False),
            (-1, False),
            (0, False),
            (1, True),
            (2, True),
            (3, True),
            (4, False),
            (100, False)
        ]
        for tier, expectation in tiers_and_expectations:
            self.assertEqual(spotify_utilities.is_valid_tier(tier=tier), expectation)

    def test_get_track_key(self):
        """Test get_track_key()"""

        # Valid tiers should produce expected output.
        names_valid_tiers_and_expectations = [
            ("name1", 1, "name1_1"),
            ("name2", 2, "name2_2"),
            ("name3", 3, "name3_3")
        ]
        for name, tier, expectation in names_valid_tiers_and_expectations:
            self.assertEqual(spotify_utilities.get_track_key(name=name, tier=tier), expectation)

        # Empty names and invalid tiers should raise a SparsePlaylistTierException.
        names_valid_tiers_and_expectations = [
            ("", 1, "name1_1"),
            (None, 2, "name2_2"),
            ("name1", -1, "name1_1"),
            ("name2", 0, "name2_2"),
            ("name3", 4, "name3_3"),
        ]
        for name, tier, expectation in names_valid_tiers_and_expectations:
            with self.assertRaises(spotify_utilities.SparsePlaylistTierException):
                spotify_utilities.get_track_key(name=name, tier=tier)

        # Empty name string should raise a SparsePlaylistTierException.
        with self.assertRaises(spotify_utilities.SparsePlaylistTierException):
            spotify_utilities.get_track_key(name="", tier=2)
        with self.assertRaises(spotify_utilities.SparsePlaylistTierException):
            spotify_utilities.get_track_key(name=None, tier=2)

    def test_get_tier_key(self):
        """Test get_tier_key()."""

        # Valid tiers should produce expected output.
        tiers_and_expectations = [
            (1, "tier_1_tracks"),
            (2, "tier_2_tracks"),
            (3, "tier_3_tracks")
        ]
        for tier, expectation in tiers_and_expectations:
            self.assertEqual(spotify_utilities.get_tier_key(tier=tier), expectation)

        # Invalid tiers should raise SparsePlaylistTierException.
        invalid_tiers = [-100, -1, 0, 4, 100]
        for tier in invalid_tiers:
            with self.assertRaises(spotify_utilities.SparsePlaylistTierException):
                spotify_utilities.get_tier_key(tier=tier)

    def test_get_artist_name(self):
        """Test get_artist_name()."""

        # Artists with names should match expected name.
        artists_and_expectations = [
            (self.spotify_artist_1, "Kendrick Lamar"),
            (self.spotify_artist_2, "Charli xcx"),
            (self.spotify_artist_3, "Tame Impala"),
            (self.spotify_artist_4, "James Blake"),
            (self.spotify_artist_5, ""),
        ]
        for artist, expectation in artists_and_expectations:
            self.assertEqual(spotify_utilities.get_artist_name(artist), expectation)

        # Artists without names should raise SparsePlaylistTierException.
        for artist, _ in artists_and_expectations:
            del artist["name"]
            with self.assertRaises(KeyError):
                spotify_utilities.get_artist_name(artist)

    def test_get_album_artist_names(self):
        """Test get_album_artist_names()."""

        # Albums with artists should match expected artists.
        albums_and_expectations = [
            (self.spotify_album_1, "Kendrick Lamar"),
            (self.spotify_album_2, "Kendrick Lamar, Charli xcx"),
            (self.spotify_album_3, "Tame Impala, James Blake"),
            (self.spotify_album_4, ""), # Artist has empty string name.
            (self.spotify_album_5, "") # No artists.
        ]
        for album, expectation in albums_and_expectations:
            self.assertEqual(spotify_utilities.get_album_artist_names(album), expectation)

        # Albums without artists should raise SparsePlaylistTierException.
        for album, _ in albums_and_expectations:
            del album["artists"]
            with self.assertRaises(KeyError):
                spotify_utilities.get_album_artist_names(album)

    def test_get_track_score(self):
        """Test get_track_score()."""

        # Albums with artists should match expected artists.
        tracks_and_expectations = [
            (self.spotify_track_1, 0),
            (self.spotify_track_2, 0.5),
            (self.spotify_track_3, 1),
            (self.spotify_track_4, 2),
            (self.spotify_track_5, 0)
        ]
        for track, expectation in tracks_and_expectations:
            self.assertEqual(spotify_utilities.get_track_score(track), expectation)

        # Tracks without a duration should raise SparsePlaylistTierException.
        for track, _ in tracks_and_expectations:
            del track["duration_ms"]
            with self.assertRaises(KeyError):
                spotify_utilities.get_track_score(track)

    def test_get_track_name(self):
        """Test get_track_name()."""
        
        # Tracks with names should match expected name.
        tracks_and_expectations = [
            (self.spotify_track_1, "!!!!!!!"),
            (self.spotify_track_2, "U-Love"),
            (self.spotify_track_3, "Not Like Us"),
            (self.spotify_track_4, "Stairway to Heaven - Remaster"),
            (self.spotify_track_5, "")
        ]
        for track, expectation in tracks_and_expectations:
            self.assertEqual(spotify_utilities.get_track_name(track), expectation)

        # Tracks without names should raise SparsePlaylistTierException.
        for track, _ in tracks_and_expectations:
            del track["name"]
            with self.assertRaises(KeyError):
                spotify_utilities.get_track_name(track)

    def test_get_track_names(self):
        """Test get_track_names()."""
        self.assertEqual(
            spotify_utilities.get_track_names(spotify_album_tracks=self.spotify_album_tracks),
            ["!!!!!!!", "U-Love", "Not Like Us", "Stairway to Heaven - Remaster", ""]
        )

    def test_get_album_highest_possible_score(self):
        """Test get_album_highest_possible_score()."""
        self.assertEqual(
            spotify_utilities.get_album_highest_possible_score(spotify_album_tracks=self.spotify_album_tracks), 
            10.5 # Mock album has two 0pt tracks, one 0.5pt track, one 1pt track and one 2pt track. 3.5 in total, multiplied by 3 if all were tier 3.
        )

if __name__ == '__main__':
    unittest.main()