from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any
import requests

from trivia_game.utils.sql_utils import get_db_connection
from trivia_game.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Team:
    """
        
        Represents a team and its associated attributes, inlcuding id, team, and favorite category

        Attributes:
        id (int): The id of the team 
        team (str): The string name of the team 
        favorite_category (int): The ID of the team's favorite category
        games_played (int): number of games the team has played 
        total_score (int): cummulative team score
        current_score (int): team's score in current game 
        mascot (str): url to team mascot 
    
    """

    id: int
    team: str
    favorite_category: int
    games_played: int
    total_score: int
    current_score: int
    mascot: str



def get_random_dog_image() -> str:
    """
        Fetch a random dog image URL from the Dog CEO API.
        
        Raises: 
            RequestException: if there is an error fetching the dog image
    """
        

    try:
            # Fetch that dog! ( fetch random dog image from api )
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data['message']  # Return the URL of the dog image
        

    except Exception as e:
        logger.error("Error fetching dog image: %s", e)
        return "https://images.dog.ceo/breeds/shiba/shiba-16.jpg"  # Fallback in case of error


def fetch_trivia_categories() -> list[dict[str, Any]]:
    """
    Fetch an exhaustive list of trivia categories from the OpenTDB API.

    Returns:
        list[dict[str, Any]]: A list of categories, each with an 'id' and 'name'.

    Raises:
        RuntimeError: If there is an error fetching categories from the API.
    """
    try:
        logger.info("Fetching trivia categories from the OpenTDB API.")
        response = requests.get("https://opentdb.com/api_category.php")
        response.raise_for_status()
        data = response.json()
        logger.info("Successfully fetched trivia categories.")
        return data.get("trivia_categories", [])
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch trivia categories: %s", str(e))
        raise RuntimeError(f"Failed to fetch trivia categories: {e}")
                
def update_favorite_category(Team) -> None:
        """
        Prompt the user to select a single favorite category for the team.
        Updates the `favorite_category` attribute.
        """
        try:
            categories = fetch_trivia_categories()
            if not categories:
                logger.warning("No categories available to choose from.")
                print("No categories available.")
                return

            # Display the categories
            logger.info("Displaying available trivia categories to the user.")
            print("Available Categories:")
            for category in categories:
                print(f"ID: {category['id']} - Name: {category['name']}")

            # User selects a favorite category
            while True:
                try:
                    category_id = int(input("Enter the ID of your favorite category: "))
                    category_ids = {cat["id"] for cat in categories}
                    if category_id not in category_ids:
                        print(f"Invalid category ID {category_id}. Please try again.")
                        logger.warning("User entered an invalid category ID: %s", category_id)
                        continue

                    # Update the favorite category
                    Team.favorite_category = category_id
                    print(f"Favorite category updated to ID {category_id}.")
                    logger.info("Favorite category updated to ID %s.", category_id)
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid category ID.")
                    logger.warning("User entered an invalid input (non-integer).")

        except RuntimeError as e:
            print("Error fetching trivia categories.")
            logger.error("Error in fetching categories: %s", str(e))

def create_team(team: str, favorite_category: int) -> None:
    """
    Adds a new team with specified details to the database.

    Args:
    team (str): The string name of the team.
    favorite_category (int): The ID of the team's favorite category.

    Raises:
        ValueError: If another team with this name already exists.
        sqlite3.Error: If any database error occurs.
    """
    try:
        mascot_image_url = get_random_dog_image()

        with get_db_connection() as conn:
            logger.info("Database connection established successfully.")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teams (team, favorite_category, mascot)
                VALUES (?, ?, ?)
            """, (team, favorite_category, mascot_image_url))
            conn.commit()
            logger.info("Team successfully added to the database: %s", team)

    except sqlite3.IntegrityError:
        logger.error("Duplicate team: %s", team)
        raise ValueError(f"Team with name '{team}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def clear_teams() -> None:
    """
    Recreates the teams table, effectively deleting all teams.

    Raises:
        sqlite3.Error: If any database error occurs.
    """
    try:
        print("SQL_CREATE_TABLE_PATH:", os.getenv("SQL_CREATE_TABLE_PATH"))
        with open(os.getenv("SQL_CREATE_TABLE_PATH", "sql/create_team_table.sql"), "r") as fh:
            create_table_script = fh.read()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(create_table_script)
            conn.commit()

            logger.info("Teams cleared successfully.")

    except sqlite3.Error as e:
        logger.error("Database error while clearing teams: %s", str(e))
        raise e    


def delete_team(id: int) -> None:
        """
        Marks a team as deleted in the database, sets 'deleted' flag to True

        Args:
            team_id (int): The unique id of the team to be deleted

        Raises:
            ValueError: if the team has either already been deleted or a team with the 'team_id' does not exist 
            sqlite3.Error: If any database error occurs.
        """
        try:
            with get_db_connection() as conn:
                logger.info("Database connection established successfully.")
                cursor = conn.cursor()
                cursor.execute("SELECT deleted FROM teams WHERE id = ?", (id,))
                try:
                    deleted = cursor.fetchone()[0]
                    if deleted:
                        logger.info("Team with ID %s has already been deleted", id)
                        raise ValueError(f"Team with ID {id} has been deleted")
                except TypeError:
                    logger.info("Team with ID %s not found", id)
                    raise ValueError(f"Team with ID {id} not found")

                cursor.execute("UPDATE teams SET deleted = TRUE WHERE id = ?", (id,))
                conn.commit()

                logger.info("Team with ID %s marked as deleted.", id)

        except sqlite3.Error as e:
            logger.error("Database error: %s", str(e))
            raise e
        
@staticmethod
def get_team_by_id(team_id: int):
        """
        Retrieves a team from the database by its team id 

        Args:
            team_id (int): The unique id of the team to be retrieved 

        Returns: 
            Team: The team class instance asscoiated with the 'team_id' given

        Raises: 
            ValueError: If the team is marked as deleted or no team exists with the given 'team_id'
            sqlite3.Error: If any database error occurs.

        """

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, team, favorite_category, mascot, deleted, current_score, games_played, total_score FROM teams WHERE id = ?", (team_id,))
                row = cursor.fetchone()

                if row:
                    if row[4]:
                        logger.info("Team with id %s has been deleted", id)
                        raise ValueError(f"Team with name {id} has been deleted")
                    return Team(
                    id=row[0], 
                    team=row[1], 
                    favorite_category=row[2], 
                    mascot=row[3],  
                    current_score=row[5], 
                    games_played=row[6], 
                    total_score=row[7]
                )
                else:
                    logger.info("Team with ID %s not found", team_id)
                    raise ValueError(f"Team with ID {team_id} not found")

        except sqlite3.Error as e:
            logger.error("Database error: %s", str(e))
            raise e

@staticmethod
def get_team_by_name(team: str):
        """
        Retrieves a team from the database based on the given team name

        Args:
            team (str): The team of the team to be retrieved 

        Returns:
            Team: The team class instance asscoiated with the 'team_id' given

        Raises: 
            ValueError: If the team is marked as deleted or no team exists with the given name 
            sqlite3.Error: If any database error occurs.

        """

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, team, favorite_category, mascot, deleted, current_score, games_played, total_score FROM teams WHERE team = ?", (team,))
                row = cursor.fetchone()

                if row:
                    if row[4]:
                        logger.info("Team with name %s has been deleted", team)
                        raise ValueError(f"Team with name {team} has been deleted")
                    return Team(
                    id=row[0], 
                    team=row[1], 
                    favorite_category=row[2], 
                    mascot=row[3],  
                    current_score=row[5], 
                    games_played=row[6], 
                    total_score=row[7]
                )
                else:
                    logger.info("Team with name %s not found", team)
                    raise ValueError(f"Team with name {team} not found")

        except sqlite3.Error as e:
            logger.error("Database error: %s", str(e))
            raise e


@staticmethod
def update_team_stats(team_id: int, result: str) -> None:
        """
        Updates the statistics of a given team based on game results 

        Args: 
            team_id (int): The unique id of the team to be updated 
            result (str): The result of the game (either 'win' or 'loss')

        Raises:
            ValueError: If the team is marked as deleted, if there is no team with the given id, 
                or the result is not 'win' or 'loss' 
            sqlite3.Error: If any database error occurs.



        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT deleted FROM teams WHERE id = ?", (team_id,))
                try:
                    deleted = cursor.fetchone()[0]
                    if deleted:
                        logger.info("Team with ID %s has been deleted", team_id)
                        raise ValueError(f"Team with ID {team_id} has been deleted")
                except TypeError:
                    logger.info("Team with ID %s not found", team_id)
                    raise ValueError(f"Team with ID {team_id} not found")

                if result == 'win':
                    cursor.execute("UPDATE teams SET games_played = games_played + 1, total_score = total_score + 1 WHERE id = ?", (team_id,))
                elif result == 'loss':
                    cursor.execute("UPDATE teams SET games_played = games_played + 1 WHERE id = ?", (team_id,))
                else:
                    raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

                conn.commit()

        except sqlite3.Error as e:
            logger.error("Database error: %s", str(e))
            raise e
