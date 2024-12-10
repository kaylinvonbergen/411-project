import pytest
from unittest.mock import patch, MagicMock
from trivia_game.models.team_model import *
import re 
from contextlib import contextmanager



def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def team():
    """Fixture to provide a Team instance for testing."""
    return Team(
        id=1,
        team="Test Team",
        favorite_category=1,
        games_played=5,
        total_score=100,
        current_score=20,
        mascot="https://images.dog.ceo/breeds/shiba/shiba-16.jpg"
    )

@pytest.fixture
def mock_cursor(mocker):
    """Fixture to create a mock cursor and database connection."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []  
    mock_conn.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch('trivia_game.team_model.get_db_connection', mock_get_db_connection)

    return mock_cursor  # Return the mock cursor for test configuration




# Test for successful image fetch
@patch('requests.get')  # Mock 'requests.get'
def test_get_random_dog_image_success(mock_get):
    # Define the mock response data
    mock_response = {
        'message': 'https://dog.ceo/dog-api/images/random/dog.jpg'
    }

    # Set up the mock to return a response with a status code of 200 and the mock data
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_response

    # Call the function
    result = get_random_dog_image()

    # Assert that the returned URL matches the mock response
    assert result == mock_response['message']

# Test for failure (network error or exception)
@patch('requests.get')  # Mock 'requests.get'
def test_get_random_dog_image_failure(mock_get):
    # Simulate an error (e.g., network issue or bad status code)
    mock_get.side_effect = requests.RequestException("Network error")

    # Call the function (it should fallback to the default image URL)
    result = get_random_dog_image()

    # Assert that the fallback image URL is returned
    assert result == "https://images.dog.ceo/breeds/shiba/shiba-16.jpg"  # Correct fallback URL

@patch("requests.get")
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

    # Call the standalone function
    categories = fetch_trivia_categories()
    
    # Assertions
    assert len(categories) == 2, "Expected 2 categories"
    assert categories[0]["name"] == "Category 1", "Expected category name to be 'Category 1'"
    assert categories[1]["name"] == "Category 2", "Expected category name to be 'Category 2'"




@patch("trivia_game.models.team_model.get_random_dog_image")
@patch("trivia_game.models.team_model.get_db_connection")
def test_create_team(mock_get_db_connection, mock_get_random_dog_image):
    """Test creating a new team in the team model."""

    # Mock the dog image URL returned by get_random_dog_image
    mock_get_random_dog_image.return_value = "https://example.com/dog.jpg"

    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Call the function to create a new team
    create_team("Test Team", 1)

    # Ensure `execute` was called
    assert mock_cursor.execute.call_args is not None, "Expected `execute` to be called on the mock cursor."

    # Extract the actual SQL query
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Define the expected SQL query
    expected_query = normalize_whitespace("""
        INSERT INTO teams (team, favorite_category, mascot)
        VALUES (?, ?, ?)
    """)

    # Assert the SQL query matches
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract and verify the arguments
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Test Team", 1, "https://example.com/dog.jpg")
    assert actual_arguments == expected_arguments, (
        f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    )
