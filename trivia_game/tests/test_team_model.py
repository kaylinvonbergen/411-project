import pytest
from unittest.mock import patch, MagicMock
from trivia_game.models.team_model import Team, create_team

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

@patch("trivia_game.models.team_model.requests.get")
def test_get_random_dog_image(mock_get):
    """Test fetching a random dog image."""
    # Mocking the successful API response
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": "https://images.dog.ceo/breeds/husky/husky.jpg"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    # Test the normal case (successful API request)
    assert Team.get_random_dog_image() == "https://images.dog.ceo/breeds/husky/husky.jpg"
    
    # Mocking an API failure (raising an exception)
    mock_get.side_effect = Exception("API Error")
    
    # Test the fallback behavior in case of an error
    assert Team.get_random_dog_image() == "https://images.dog.ceo/breeds/shiba/shiba-16.jpg"


@patch("trivia_game.models.team_model.requests.get")
def test_fetch_trivia_categories(mock_get):
    """Test fetching trivia categories."""
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

from trivia_game.models.team_model import Team
