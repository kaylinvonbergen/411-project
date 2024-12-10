import pytest
from unittest.mock import patch, MagicMock
from trivia_game.trivia_game.models.team_model import Team
import requests

@pytest.fixture
def team():
    """Fixture to provide a Team instance for testing."""
    return Team(
        id=1,
        team="Test Team",
        favorite_categories=[1, 2, 3],
        games_played=5,
        total_score=100,
        current_score=20,
        mascot="https://images.dog.ceo/breeds/shiba/shiba-16.jpg"
    )

@pytest.fixture
def mock_get_db_connection(mocker):
    """Mock the get_db_connection function for testing."""
    return mocker.patch("trivia_game.trivia_game.utils.sql_utils.get_db_connection")

@pytest.fixture
def mock_logger(mocker):
    """Mock the logger to avoid actual logging during tests."""
    return mocker.patch("trivia_game.trivia_game.utils.logger.logger")

##################################################
# Test Static Methods
##################################################

@patch("requests.get")
def test_get_random_dog_image_success(mock_get):
    """Test get_random_dog_image successfully fetches an image URL."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "https://example.com/dog.jpg"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    dog_image = Team.get_random_dog_image()
    assert dog_image == "https://example.com/dog.jpg", "Dog image URL is incorrect"

@patch("requests.get")
def test_get_random_dog_image_failure(mock_get):
    """Test get_random_dog_image returns fallback on failure."""
    mock_get.side_effect = requests.exceptions.RequestException()

    dog_image = Team.get_random_dog_image()
    assert dog_image == "https://images.dog.ceo/breeds/shiba/shiba-16.jpg", "Fallback image URL should be returned"

@patch("requests.get")
def test_fetch_trivia_categories_success(mock_get):
    """Test fetch_trivia_categories successfully fetches categories."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "trivia_categories": [
            {"id": 1, "name": "Category 1"},
            {"id": 2, "name": "Category 2"}
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    categories = Team.fetch_trivia_categories()
    assert len(categories) == 2, "Expected 2 categories"
    assert categories[0]["name"] == "Category 1"

@patch("requests.get")
def test_fetch_trivia_categories_failure(mock_get):
    """Test fetch_trivia_categories raises error on failure."""
    mock_get.side_effect = requests.exceptions.RequestException()

    with pytest.raises(RuntimeError, match="Failed to fetch trivia categories"):
        Team.fetch_trivia_categories()

##################################################
# Test Instance Methods
##################################################

@patch("trivia_game.trivia_game.models.team.Team.fetch_trivia_categories")
def test_update_favorite_category(mock_fetch, team):
    """Test update_favorite_category adds valid categories."""
    mock_fetch.return_value = [{"id": 1, "name": "Category 1"}]
    input_values = iter(["1", "-1"])
    with patch("builtins.input", side_effect=input_values):
        team.update_favorite_category()
    assert 1 in team.favorite_categories

##################################################
# Test Database Interaction
##################################################

def test_create_team_success(mock_get_db_connection):
    """Test create_team adds a new team to the database."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    Team.create_team("New Team", [1, 2, 3])
    mock_cursor.execute.assert_called_once_with(
        """
        INSERT INTO teams (team, favorite_categories, mascot)
        VALUES (?, ?, ?)
        """,
        ("New Team", "[1, 2, 3]", "https://images.dog.ceo/breeds/shiba/shiba-16.jpg")
    )

def test_delete_team_success(mock_get_db_connection):
    """Test delete_team marks a team as deleted in the database."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_cursor.fetchone.return_value = [False]

    Team.delete_team(1)
    mock_cursor.execute.assert_any_call("SELECT deleted FROM teams WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call("UPDATE teams SET deleted = TRUE WHERE id = ?", (1,))

def test_get_team_by_id_success(mock_get_db_connection):
    """Test get_team_by_id retrieves a team successfully."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_cursor.fetchone.return_value = (1, "Test Team", "[1, 2, 3]", "https://example.com/mascot.jpg", False)

    team0 = Team.get_team_by_id(1)
    assert team0.team == "Test Team", "Team name does not match"
    assert team0.favorite_categories == [1, 2, 3], "Favorite categories do not match"

def test_get_team_by_id_not_found(mock_get_db_connection):
    """Test get_team_by_id raises error if team not found."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Team with ID 1 not found"):
        Team.get_team_by_id(1)

##################################################
# Test Utility Functions
##################################################

def test_update_team_stats_success(mock_get_db_connection):
    """Test update_team_stats updates stats for a team."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn
    mock_cursor.fetchone.return_value = [False]

    Team.update_team_stats(1, "win")
    mock_cursor.execute.assert_any_call("SELECT deleted FROM teams WHERE id = ?", (1,))
    mock_cursor.execute.assert_any_call(
        "UPDATE teams SET games_played = games_played + 1, total_score = total_score + 1 WHERE id = ?", (1,)
    )
