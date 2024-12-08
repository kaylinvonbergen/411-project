import unittest
from unittest.mock import patch, MagicMock
from trivia_game.models.game_model import GameModel
from trivia_game.models.team_model import Team

class TestGameModel(unittest.TestCase):
    @patch("requests.get")
    def test_initialization_success(self, mock_get):
        # Mock API response for session token
        mock_get.return_value = MagicMock(
            json=lambda: {"response_code": 0, "token": "test_token"}
        )

        # Initialize GameModel
        game = GameModel()

        # Assert session token is set
        self.assertEqual(game.session_token, "test_token")

    @patch("requests.get")
    def test_initialization_failure(self, mock_get):
        # Mock API response for failure
        mock_get.return_value = MagicMock(
            json=lambda: {"response_code": 1, "response_message": "Error fetching token"}
        )

        # Assert exception is raised
        with self.assertRaises(Exception):
            GameModel()

    def test_add_opponents(self):
        game = GameModel()
        team1 = Team(name="Team A", current_score=0)
        team2 = Team(name="Team B", current_score=0)

        # Add two opponents
        game.prep_opponent(team1)
        game.prep_opponent(team2)

        # Assert opponents were added
        self.assertEqual(len(game.opponents), 2)

        # Assert exception for adding a third opponent
        with self.assertRaises(ValueError):
            game.prep_opponent(Team(name="Team C", current_score=0))

    @patch("requests.get")
    @patch("logging.Logger.info")
    def test_display_score(self, mock_logger, mock_get):
        # Mock trivia stats response
        mock_get.return_value = MagicMock(
            json=lambda: {"trivia_categories": [{"id": 9, "name": "General Knowledge"}]}
        )

        game = GameModel()
        team1 = Team(name="Team A", current_score=10)
        team2 = Team(name="Team B", current_score=20)
        game.opponents = [team1, team2]

        # Call display_score
        game.display_score()

        # Assert scores and stats were logged
        mock_logger.assert_any_call("Current score is:")
        mock_logger.assert_any_call(" %s: %s points", "Team A", 10)
        mock_logger.assert_any_call(" %s: %s points", "Team B", 20)
        mock_logger.assert_any_call("Available Trivia Categories: General Knowledge (ID: 9)")

    @patch("requests.get")
    @patch("builtins.input", side_effect=["correct_answer", "wrong_answer"])
    def test_game_logic(self, mock_input, mock_get):
        # Mock trivia API response
        mock_get.return_value = MagicMock(
            json=lambda: {
                "response_code": 0,
                "results": [
                    {
                        "question": "Sample question?",
                        "correct_answer": "correct_answer",
                        "incorrect_answers": ["wrong_answer"],
                    }
                ],
            }
        )

        game = GameModel()
        team1 = Team(name="Team A", current_score=0)
        team2 = Team(name="Team B", current_score=0)
        team1.favorite_categories = [9]
        team2.favorite_categories = [9]
        game.opponents = [team1, team2]

        # Run game
        result = game.game()

        # Assert game success
        self.assertTrue(result)
        self.assertEqual(team1.team_score, 1)
        self.assertEqual(team2.team_score, 0)

    def test_clear_opponents(self):
        game = GameModel()
        team1 = Team(name="Team A", current_score=0)
        team2 = Team(name="Team B", current_score=0)
        game.opponents = [team1, team2]

        # Clear opponents
        game.clear_opponents()

        # Assert opponents list is empty
        self.assertEqual(len(game.opponents), 0)

