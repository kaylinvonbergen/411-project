from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any

from utils.sql_utils import get_db_connection
from utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Team:
    """
     
    Represents a team and its associated attributes, inlcuding id, meal, cuisine, price, and difficulty

    Attributes:
    id (int): The id of the team 
    name (str): The string name of the team 
    favorite_categories (int list): list of id's for team's favorite categories
    games_played (int): number of games the team has played 
    total_score (int): cummulative team score
    current_score (int): team's score in current game 
  
    """

    id: int
    name: str
    favorite_categories: list[int]
    games_played: int
    total_score: int
    current_score: int

def create_team(name: str, favorite_categories: list[int]) -> None:
    """
    Adds a new team with specified details to the database 

    Args:
    name (str): The string name of the team 
    favorite_categories (int list): list of id's for team's favorite categories

    Raises:
        ValueError: If another team with this name already exists 
        sqlite3.Error: If any database error occurs.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teams (name, favorite_categories)
                VALUES (?, ?)
            """, (name, favorite_categories))
            conn.commit()

            logger.info("Team successfully added to the database: %s", name)

    except sqlite3.IntegrityError:
        logger.error("Duplicate team name: %s", name)
        raise ValueError(f"Team with name '{name}' already exists")

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



def update_meal_stats(team_id: int, result: str) -> None:
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

