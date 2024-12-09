import pytest
from unittest.mock import patch, MagicMock
from trivia_game.trivia_game.models.team_model import Team, create_team

@pytest.fixture
def team():
    """Fixture to create a sample team for testing."""
    return Team(
        id=1,
        name="Test Team",
        favorite_categories=[9, 10],
        games_played=5,
        total_score=15,
        current_score=0,
        mascot="https://images.dog.ceo/breeds/shiba/shiba-16.jpg"
    )

@patch("trivia_game.trivia_game.models.team_model.requests.get")
def test_get_random_dog_image(mock_get):
    """Test fetching a random dog image."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "https://images.dog.ceo/breeds/husky/husky.jpg"}
    mock_get.return_value = mock_response

    assert Team.get_random_dog_image() == "https://images.dog.ceo/breeds/husky/husky.jpg"

    mock_get.side_effect = Exception("API Error")
    assert Team.get_random_dog_image() == "https://images.dog.ceo/breeds/shiba/shiba-16.jpg"

@patch("trivia_game.trivia_game.models.team_model.requests.get")
def test_fetch_trivia_categories(mock_get):
    """Test fetching trivia categories."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "trivia_categories": [
            {"id": 9, "name": "General Knowledge"},
            {"id": 10, "name": "Entertainment: Books"}
        ]
    }
    mock_get.return_value = mock_response

    categories = Team.fetch_trivia_categories()
    assert len(categories) == 2
    assert categories[0]["name"] == "General Knowledge"
    assert categories[1]["id"] == 10

@patch("trivia_game.trivia_game.models.team_model.get_db_connection")
def test_create_team(mock_db_connection):
    """Test creating a team."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_db_connection.return_value = mock_conn

    create_team("Test Team", [9, 10])

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO teams (team, favorite_categories, mascot) VALUES (?, ?, ?)",
        ("Test Team", '[9, 10]', "https://images.dog.ceo/breeds/shiba/shiba-16.jpg")
    )
    mock_conn.commit.assert_called_once()
