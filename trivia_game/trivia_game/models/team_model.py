from contextlib import contextmanager
from unittest.mock import MagicMock, patch
import pytest
import sqlite3
import requests
from trivia_game.models.team_model import (
    Team,
    create_team, 
    delete_team, 
    get_team_by_id, 
    get_team_by_name,
    get_random_dog_image,
    update_team_stats,
    fetch_trivia_categories
)

def normalize_whitespace(sql):
    return " ".join(sql.split())

@pytest.fixture
def mock_cursor(mocker):
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

    mocker.patch("trivia_game.models.team_model.get_db_connection", mock_get_db_connection)

    return mock_cursor



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

    # Ensure execute was called
    assert mock_cursor.execute.call_args is not None, "Expected execute to be called on the mock cursor."

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

@patch("trivia_game.models.team_model.get_db_connection")
@patch("trivia_game.models.team_model.get_random_dog_image")
def test_create_team_duplicate(mock_get_random_dog_image, mock_get_db_connection):
    """Test handling of duplicate team creation."""
    # Mock the dog image URL returned by get_random_dog_image
    mock_get_random_dog_image.return_value = "https://example.com/dog.jpg"

    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Simulate a duplicate team insertion by raising sqlite3.IntegrityError
    mock_cursor.execute.side_effect = sqlite3.IntegrityError

    # Attempt to create a duplicate team and check for the raised ValueError
    with pytest.raises(ValueError) as excinfo:
        create_team("Test Team", 1)

    # Verify the error message
    assert str(excinfo.value) == "Team with name 'Test Team' already exists"

    # Ensure `execute` was called with the expected SQL query
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    expected_query = normalize_whitespace("""
        INSERT INTO teams (team, favorite_category, mascot)
        VALUES (?, ?, ?)
    """)
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract and verify the arguments passed to `execute`
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Test Team", 1, "https://example.com/dog.jpg")
    assert actual_arguments == expected_arguments, (
        f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    )

@patch("trivia_game.models.team_model.get_db_connection")
def test_delete_team(mock_get_db_connection):
    """Test soft deleting a team from the catalog by team ID."""
    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Simulate fetching the deleted status of a team
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (False,)

    # Call the function to delete a team
    team_id = 1
    delete_team(team_id)

    # Ensure `execute` was called with the correct SQL to check deletion status
    check_query = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    expected_check_query = normalize_whitespace("SELECT deleted FROM teams WHERE id = ?")
    assert check_query == expected_check_query, "The SQL query for checking deletion status did not match."

    # Ensure `execute` was called with the correct SQL to mark as deleted
    delete_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])
    expected_delete_query = normalize_whitespace("UPDATE teams SET deleted = TRUE WHERE id = ?")
    assert delete_query == expected_delete_query, "The SQL query for marking as deleted did not match."

    # Verify the arguments passed to the update query
    delete_arguments = mock_cursor.execute.call_args_list[1][0][1]
    assert delete_arguments == (team_id,), f"Expected arguments {(team_id,)}, got {delete_arguments}."

    # Ensure commit was called
    assert mock_conn.commit.called, "Expected `commit` to be called on the connection."

@patch("trivia_game.models.team_model.get_db_connection")
def test_delete_team_bad_id(mock_get_db_connection):
    """Test error when trying to delete a non-existent team."""
    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Simulate no team found for the given ID
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None

    # Call the function to delete a non-existent team and check for the raised ValueError
    team_id = 99
    with pytest.raises(ValueError) as excinfo:
        delete_team(team_id)

    assert str(excinfo.value) == f"Team with ID {team_id} not found", "Expected ValueError for non-existent team ID."

@patch("trivia_game.models.team_model.get_db_connection")
def test_delete_team_already_deleted(mock_get_db_connection):
    """Test error when trying to delete a team that's already marked as deleted."""
    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Simulate fetching a team that's already marked as deleted
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (True,)

    # Call the function to delete an already deleted team and check for the raised ValueError
    team_id = 2
    with pytest.raises(ValueError) as excinfo:
        delete_team(team_id)

    assert str(excinfo.value) == f"Team with ID {team_id} has been deleted", "Expected ValueError for already deleted team."


def test_get_team_by_id(mock_cursor):
    mock_cursor.fetchone.return_value = (7, "Team A", 1, "https://example.com/dog.jpg", False, 200, 100, 10)

    # Call the function and check the result
    result = get_team_by_id(7)

    # Expected result based on the simulated fetchone return value
    expected_result = Team(7, "Team A", 1, 100, 10, 200,"https://example.com/dog.jpg")

    # Ensure the result matches the expected output
    assert result == expected_result, f"Expected {expected_result}, got {result}"

    # Ensure the SQL query was executed correctly
    expected_query = normalize_whitespace("SELECT id, team, favorite_category, mascot, deleted, current_score, games_played, total_score FROM teams WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (7,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


@patch("trivia_game.models.team_model.get_db_connection")
def test_get_team_by_id_bad_id(mock_get_db_connection):
    # Mock the database connection and cursor
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = None  # Simulate no record found

    # Expect a ValueError when attempting to fetch a non-existent team
    with pytest.raises(ValueError):
        get_team_by_id(999)




@patch("trivia_game.models.team_model.get_db_connection")
def test_get_team_by_name(mock_get_db_connection):
    """Test retrieving a team by its name."""
    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Simulate fetching a team by name
    team_name = "Test Team"
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = (1, "Test Team", 1, "https://example.com/dog.jpg", False, 10, 50, 5)

    team = get_team_by_name(team_name)

    # Verify the returned team attributes
    assert team.id == 1
    assert team.team == "Test Team"
    assert team.favorite_category == 1
    assert team.current_score == 10
    assert team.games_played == 50
    assert team.total_score == 5
    assert team.mascot == "https://example.com/dog.jpg"

    # Ensure the correct SQL was executed
    query = normalize_whitespace(mock_cursor.execute.call_args[0][0])
    expected_query = normalize_whitespace("SELECT id, team, favorite_category, mascot, deleted, current_score, games_played, total_score FROM teams WHERE team = ?")
    assert query == expected_query, "The SQL query did not match the expected structure."

@patch("trivia_game.models.team_model.get_db_connection")
def test_get_team_by_id_bad_name(mock_get_db_connection):
    """Test error when retrieving a non-existent team by name."""
    # Mock the database connection and cursor
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Set up the context manager behavior
    mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    # Simulate no team found for the given name
    team_name = "Nonexistent Team"
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError) as excinfo:
        get_team_by_name(team_name)

    assert str(excinfo.value) == f"Team with name {team_name} not found", "Expected ValueError for non-existent team name."

def test_update_team_stats_win(mock_cursor):
    """Test updating team stats for a win."""

    # Simulate that the team exists and is not deleted (team_id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_team_stats function with a sample team ID and result
    team_id = 1
    update_team_stats(team_id, "win")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE teams SET games_played = games_played + 1, total_score = total_score + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query matches the expected structure
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (team ID)
    expected_arguments = (team_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_update_team_stats_loss(mock_cursor):
    """Test updating team stats for a loss."""

    # Simulate that the team exists and is not deleted (team_id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_team_stats function with a sample team ID and result
    team_id = 1
    update_team_stats(team_id, "loss")

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE teams SET games_played = games_played + 1 WHERE id = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query matches the expected structure
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (team ID)
    expected_arguments = (team_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_team_stats_deleted_team(mock_cursor):
    """Test error when trying to update stats for a deleted team."""

    # Simulate that the team exists but is marked as deleted (team_id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted team
    with pytest.raises(ValueError, match="Team with ID 1 has been deleted"):
        update_team_stats(1, "win")

    # Ensure that no SQL query for updating stats was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM teams WHERE id = ?", (1,))


def test_update_team_stats_nonexistent_team(mock_cursor):
    """Test error when trying to update stats for a non-existent team."""

    # Simulate that the team does not exist (no row returned)
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to update a non-existent team
    with pytest.raises(ValueError, match="Team with ID 99 not found"):
        update_team_stats(99, "win")

    # Ensure that the SQL query to check existence was executed correctly
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM teams WHERE id = ?", (99,))

def test_update_team_stats_invalid_result(mock_cursor):
    """Test error when providing an invalid game result."""

    # Simulate that the team exists and is not deleted (team_id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Expect a ValueError for an invalid game result
    with pytest.raises(ValueError, match="Invalid result: draw. Expected 'win' or 'loss'."):
        update_team_stats(1, "draw")

    # Ensure that no SQL query for updating stats was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM teams WHERE id = ?", (1,))


def test_update_team_stats_database_error(mock_cursor):
    """Test handling of a database error during stats update."""

    # Simulate that the team exists and is not deleted (team_id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Simulate a database error during execution
    mock_cursor.execute.side_effect = sqlite3.Error("Database error")

    # Expect a sqlite3.Error when attempting to update team stats
    with pytest.raises(sqlite3.Error, match="Database error"):
        update_team_stats(1, "win")

    # Ensure that the SQL query to check deletion status was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM teams WHERE id = ?", (1,))
