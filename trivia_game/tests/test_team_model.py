import pytest
from unittest.mock import patch, MagicMock
from trivia_game.trivia_game.models.team_model import (
    Team, get_random_dog_image, fetch_trivia_categories, create_team, delete_team, get_team_by_id, get_team_by_name, update_team_stats
)
from trivia_game.trivia_game.utils.sql_utils import get_db_connection


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
    """Test fetching a random dog image URL."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "https://images.dog.ceo/breeds/husky/husky.jpg"}
    mock_get.return_value = mock_response

    image_url = get_random_dog_image()
    assert image_url == "https://images.dog.ceo/breeds/husky/husky.jpg"

    # Test fallback on error
    mock_get.side_effect = Exception("API Error")
    fallback_url = get_random_dog_image()
    assert fallback_url == "https://images.dog.ceo/breeds/shiba/shiba-16.jpg"


@patch("trivia_game.trivia_game.models.team_model.requests.get")
def test_fetch_trivia_categories(mock_get):
    """Test fetching trivia categories from the OpenTDB API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "trivia_categories": [
            {"id": 9, "name": "General Knowledge"},
            {"id": 10, "name": "Entertainment: Books"}
        ]
    }
    mock_get.return_value = mock_response

    categories = fetch_trivia_categories()
    assert len(categories) == 2
    assert categories[0]["name"] == "General Knowledge"
    assert categories[1]["id"] == 10

    # Test API failure
    mock_get.side_effect = Exception("API Error")
    with pytest.raises(RuntimeError):
        fetch_trivia_categories()


@patch("trivia_game.trivia_game.models.team_model.get_db_connection")
def test_create_team(mock_db_connection):
    """Test creating a team in the database."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_db_connection.return_value = mock_conn

    create_team("Test Team", [9, 10])

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO teams (team, favorite_categories, mascot) VALUES (?, ?, ?)",
        ("Test Team", [9, 10], "https://images.dog.ceo/breeds/shiba/shiba-16.jpg")
    )
    mock_conn.commit.assert_called_once()


@patch("trivia_game.trivia_game.models.team_model.get_db_connection")
def test_delete_team(mock_db_connection):
    """Test deleting a team from the database."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (0,)
    mock_db_connection.return_value = mock_conn

    delete_team(1)

    mock_cursor.execute.assert_called_with("SELECT deleted FROM teams WHERE id = ?", (1,))
    mock_cursor.execute.assert_called_with("UPDATE teams SET deleted = TRUE WHERE id = ?", (1,))
    mock_conn.commit.assert_called_once()


@patch("trivia_game.trivia_game.models.team_model.get_db_connection")
def test_get_team_by_id(mock_db_connection, team):
    """Test retrieving a team by its ID."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (
        team.id, team.name, team.favorite_categories, team.mascot, 0
    )
    mock_db_connection.return_value = mock_conn

    retrieved_team = get_team_by_id(1)
    assert retrieved_team.id == team.id
    assert retrieved_team.name == team.name
    assert retrieved_team.favorite_categories == team.favorite_categories


@patch("trivia_game.trivia_game.models.team_model.get_db_connection")
def test_update_team_stats(mock_db_connection, team):
    """Test updating team stats after a game."""
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_cursor.fetchone.return_value = (0,)
    mock_db_connection.return_value = mock_conn

    update_team_stats(team.id, "win")
    mock_cursor.execute.assert_any_call(
        "UPDATE teams SET games_played = games_played + 1, total_score = total_score + 1 WHERE id = ?", (team.id,)
    )
    mock_conn.commit.assert_called_once()

    update_team_stats(team.id, "loss")
    mock_cursor.execute.assert_any_call(
        "UPDATE teams SET games_played = games_played + 1 WHERE id = ?", (team.id,)
    )
    mock_conn.commit.assert_called()


@patch("trivia_game.trivia_game.models.team_model.requests.get")
def test_update_favorite_category(mock_get, team):
    """Test updating the team's favorite categories."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "trivia_categories": [
            {"id": 9, "name": "General Knowledge"},
            {"id": 10, "name": "Entertainment: Books"}
        ]
    }
    mock_get.return_value = mock_response

    with patch("builtins.input", side_effect=["9", "-1"]):
        team.update_favorite_category()
        assert 9 in team.favorite_categories

    with patch("builtins.input", side_effect=["99", "-1"]):
        with pytest.raises(ValueError):
            team.update_favorite_category()


