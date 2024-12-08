from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any
import requests

from utils.sql_utils import get_db_connection
from utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Team:
    """
     
    Represents a team and its associated attributes, inlcuding id, team, cuisine, price, and difficulty

    Attributes:
    id (int): The id of the team 
    name (str): The string name of the team 
    favorite_categories (int list): list of id's for team's favorite categories
    games_played (int): number of games the team has played 
    total_score (int): cummulative team score
    current_score (int): team's score in current game 
    mascot (str): url to team mascot 
  
    """

    id: int
    team: str
    favorite_categories: list[int]
    games_played: int
    total_score: int
    current_score: int
    mascot: str

def get_random_dog_image() -> str:
    """
    Fetch a random dog image URL from the Dog CEO API.
    
    Raises: 
        RequestException: if there is an error fetching the dog image"""
    

    try:
        # Fetch that dog! ( fetch random dog image from api )
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return data['message']  # Return the URL of the dog image
    

    except requests.exceptions.RequestException as e:
        logger.error("Error fetching dog image: %s", e)
        return "https://images.dog.ceo/breeds/shiba/shiba-16.jpg"  # Fallback in case of error


def create_team(team: str, favorite_categories: list[int]) -> None:
    """
    Adds a new team with specified details to the database 

    Args:
    team (str): The string team of the team 
    favorite_categories (int list): list of id's for team's favorite categories

    Raises:
        ValueError: If another team with this team already exists 
        sqlite3.Error: If any database error occurs.
    """
    try:
        # Get a random dog image URL for the mascot
        mascot_image_url = get_random_dog_image()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teams (team, favorite_categories, mascot)
                VALUES (?, ?, ?)
            """, (team, favorite_categories, mascot_image_url))
            conn.commit()

            logger.info("Team successfully added to the database: %s", team)

    except sqlite3.IntegrityError:
        logger.error("Duplicate team team: %s", team)
        raise ValueError(f"Team with team '{team}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def delete_team(team_id: int) -> None:
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
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM teams WHERE id = ?", (team_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Team with ID %s has already been deleted", team_id)
                    raise ValueError(f"Team with ID {team_id} has been deleted")
            except TypeError:
                logger.info("Team with ID %s not found", team_id)
                raise ValueError(f"Team with ID {team_id} not found")

            cursor.execute("UPDATE teams SET deleted = TRUE WHERE id = ?", (team_id,))
            conn.commit()

            logger.info("Team with ID %s marked as deleted.", team_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
    

def get_team_by_id(team_id: int) -> Team:
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
            cursor.execute("SELECT id, team, favorite_categories, mascot, deleted FROM teams WHERE id = ?", (team_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Team with ID %s has been deleted", team_id)
                    raise ValueError(f"Team with ID {team_id} has been deleted")
                return Team(id=row[0], team=row[1], favorite_categories=row[2], mascot=row[3])
            else:
                logger.info("Team with ID %s not found", team_id)
                raise ValueError(f"Team with ID {team_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_team_by_name(team_name: str) -> Team:
    """
    Retrieves a team from the database based on the given team name

    Args:
        team_name (str): The team of the team to be retrieved 

    Returns:
        Team: The team class instance asscoiated with the 'team_id' given

    Raises: 
        ValueError: If the team is marked as deleted or no team exists with the given name 
        sqlite3.Error: If any database error occurs.

    """

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, team, cuisine, price, difficulty, deleted FROM teams WHERE team = ?", (team_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Team with name %s has been deleted", team_name)
                    raise ValueError(f"Team with name {team_name} has been deleted")
                return Team(id=row[0], team=row[1], favorite_categories=row[2], mascot=row[3])
            else:
                logger.info("Team with name %s not found", team_name)
                raise ValueError(f"Team with name {team_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e



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

