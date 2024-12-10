import pytest
from unittest.mock import MagicMock, patch
from trivia_game.models.team_model import Team
from trivia_game.models.game_model import GameModel


@pytest.fixture
def mock_team():
    """Fixture to create a mock Team instance."""
    return Team(
        id=1,
        team="Team A",
        favorite_categories=[9, 10],
        games_played=0,
        total_score=0,
        current_score=0,
        mascot="https://example.com/mascot.png"
    )


@pytest.fixture
def game_model():
    """Fixture to create a GameModel instance."""
    return GameModel()


@pytest.fixture
def mock_requests_get(mocker):
    """Mock the requests.get function."""
    return mocker.patch("requests.get")


def test_game_model_initialization(mock_requests_get):
    """Test initialization of GameModel with successful session token retrieval."""
    mock_requests_get.return_value.json.return_value = {
        "response_code": 0,
        "token": "test_token"
    }

    game = GameModel()
    assert game.session_token == "test_token", "Session token was not set correctly."


def test_game_model_failed_token(mock_requests_get):
    """Test initialization of GameModel when session token request fails."""
    mock_requests_get.return_value.json.return_value = {
        "response_code": 1,
        "token": ""
    }

    game = GameModel()
    assert game.session_token == "", "Session token should be empty on failure."


def test_prep_opponent(game_model, mock_team):
    """Test adding an opponent to the GameModel."""
    game_model.prep_opponent(mock_team)
    assert len(game_model.opponents) == 1
    assert game_model.opponents[0] == mock_team, "Opponent was not added correctly."


def test_prep_opponent_limit(game_model, mock_team):
    """Test adding more than two opponents raises a ValueError."""
    game_model.prep_opponent(mock_team)
    game_model.prep_opponent(mock_team)
    with pytest.raises(ValueError, match="Opponents list is full, cannot add more opponents."):
        game_model.prep_opponent(mock_team)


def test_clear_opponents(game_model, mock_team):
    """Test clearing the opponents list."""
    game_model.prep_opponent(mock_team)
    game_model.clear_opponents()
    assert len(game_model.opponents) == 0, "Opponents list was not cleared."


def test_display_score(game_model, mock_team, mock_requests_get):
    """Test display_score logs scores and fetches trivia stats."""
    mock_requests_get.return_value.json.return_value = {
        "trivia_categories": [
            {"id": 9, "name": "General Knowledge"},
            {"id": 10, "name": "Entertainment: Books"}
        ]
    }

    mock_team.current_score = 5
    game_model.rounds = 10
    game_model.prep_opponent(mock_team)
    game_model.prep_opponent(mock_team)

    with patch("logging.Logger.info") as mock_logger_info:
        game_model.display_score()
        assert mock_logger_info.call_count > 0, "Logger.info was not called."


def test_display_score_no_categories(mock_requests_get, game_model, mock_team):
    """Test display_score when no trivia categories are available."""
    mock_requests_get.return_value.json.return_value = {"trivia_categories": []}

    game_model.prep_opponent(mock_team)
    game_model.prep_opponent(mock_team)

def test_game_not_enough_opponents(game_model):
    """Test starting a game with fewer than two opponents raises ValueError."""
    with pytest.raises(ValueError, match="Two teams must be in the game."):
        game_model.game()


def test_game_success(mock_requests_get, game_model, mock_team):
    """Test successful game execution."""
    game_model.prep_opponent(mock_team)
    opponent_2 = Team(
        id=2,
        team="Team B",
        favorite_categories=[11, 12],
        games_played=0,
        total_score=0,
        current_score=0,
        mascot="https://example.com/mascot2.png"
    )
    game_model.prep_opponent(opponent_2)

    mock_requests_get.return_value.json.return_value = {
        "response_code": 0,
        "results": [
            {
                "question": "What is 2+2?",
                "correct_answer": "4"
            }
        ]
    }

    with patch("builtins.input", return_value="4"), patch("logging.Logger.info"):
        result = game_model.game()
        assert result is True, "Game did not complete successfully."
