from trivia_game.trivia_game.models.team_model import * 
from trivia_game.trivia_game.utils.logger import *
from typing import List

from dataclasses import dataclass
import logging
import os
import sqlite3
from typing import Any
import requests
import html
import random


from trivia_game.trivia_game.utils.sql_utils import get_db_connection
from trivia_game.trivia_game.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class GameModel:
    """
    A class to manage games between teams.

    Attributes:
        opponents (List[Team]): A list of current opponents.
    """
    
    
    rounds = 0 

    def __init__(self):
        """
        Initializes the GameModel object with an empty list of combatants
        """
        logger.info("Getting session token")
        url = "https://opentdb.com/api_token.php?command=request"
        self.opponents: List[Team] = []
        self.session_token: str = ""
        response = requests.get(url)
        data = response.json()
        
        if data['response_code'] == 0:  # Token generated successfully
            session_token = data['token']
        else:
            logger.error("Failed to get session token :(")
            raise Exception(f"Error fetching session key: {data['response_message']}")


def display_score(self):
    """
    Displays current scores and logs trivia stats.
    """
    # Log current scores
    logger.info("Current score is:")
    logger.info(" %s: %s points", self.opponents[0].name, self.opponents[0].current_score)
    logger.info(" %s: %s points", self.opponents[1].name, self.opponents[1].current_score)

    # Fetch trivia stats from /api/trivia/stats
    try:
        response = requests.get("https://opentdb.com/api_category.php")
        response.raise_for_status()  # Check for HTTP errors
        categories = response.json().get('trivia_categories', [])
        
        # Convert stats to a string and log
        if categories:
            stats_string = ", ".join([f"{category['name']} (ID: {category['id']})" for category in categories])
            logger.info("Available Trivia Categories: %s", stats_string)
        else:
            logger.warning("No trivia categories available to log.")

    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch trivia stats: %s", str(e))

        


    def get_result(self, opponent: Team, answer) -> float:
        """
        Determines the correctness of a team based on their answer as compared to the correct answer

        Args:
		    opponent (Team): the opponent to judge
            answer (String): the correct answer to the question

        Returns:
		    boolean: True if correct, False otherwise 
        """
        teamanswer = input("Please enter your answer: ")
        result = answer == teamanswer

        return result

    def game(self) -> str:

        """
        Determines the result of a game/[round?] between two opponents

	    Returns:
		    str: the name of the winning opponent

        Raises:
            ValueError: if there are less than two opponents.
        """

        logger.info("Answer the trivia question!")

        if len(self.opponents) < 2:
            logger.error("Not enough teams to start a Game.")
            raise ValueError("Two teams must be in the game.")

        opponent_1 = self.opponents[0]
        opponent_2 = self.opponents[1]
        favorite_categories = []
        if len(opponent_1.favorite_categories) == 0:
            raise ValueError("Favorite categories list is empty.")
        category += random.randint(min(opponent_1.favorite_categories), max(opponent_1.favorite_categories))        

        if len(opponent_2.favorite_categories) == 0:
            raise ValueError("Favorite categories list is empty.")
        category += random.randint(min(opponent_2.favorite_categories), max(opponent_2.favorite_categories))        


        # Log the start of the game
        logger.info("Game started between %s and %s", opponent_1.name, opponent_2.name)
        logger.info("Getting question 1 of this round from Open Trivia")

        for i in range(0,1):
            category = favorite_categories[i]
            try:
                logger.info("Getting question %s of this round from Open Trivia", i)
                if i == 0:
                    api_url = f'https://opentdb.com/api.php?amount=1&category={category}&type=multiple&token={self.session_token}'
                if i == 1: 
                    api_url = f'https://opentdb.com/api.php?amount=1&category={category}&type=boolean&token={self.session_token}'
                # Fetch the data from the API
                response = requests.get(api_url)
                response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

                # Parse the JSON response
                data = response.json()

                # Check if the response contains valid questions
                if data['response_code'] != 0:
                    raise ValueError("No trivia questions available for the specified category.")
                
                # Extract and decode the question and answer
                question_data = data['results'][0]
                question = html.unescape(question_data['question'])
                answer = html.unescape(question_data['correct_answer'])

                
            
            except requests.exceptions.RequestException as e:
                logger.error("Error fetching trivia data")
                raise ValueError("Error fetching trivia data")
                return None, None
                
            except ValueError as ve:
                raise ValueError("Error fetching trivia data")
                return None, None
            
            
            
            logger.info(f"TEAM 1: Question: {question}")
            score_1 = get_result(opponent_1, answer)
            logger.info(f"TEAM 2: Question: {question}")
            score_2 = get_result(opponent_2, answer)
            

            # Log this
            logger.info("Score for %s: %.3f", opponent_1.name, score_1)
            logger.info("Score for %s: %.3f", opponent_2.name, score_2)

            # Determine win/tie, update stats and log
            if score_1 and not score_2:
                winner = opponent_1
                loser = opponent_2
                logger.info("The winner is: %s", winner.name)
                winner.team_score += 1
            elif not score_1 and score_2:
                winner = opponent_2
                loser = opponent_1
                logger.info("The winner is: %s", winner.name)
                winner.team_score += 1
            else:
                if score_1:
                    result_s = "correct"
                    opponent_1.team_score += 1
                    opponent_2.team_score += 1
                else:
                    result_s = "incorrect" 
                    logger.info("There was a tie between %s & %s. Both teams were %s.", opponent_1, opponent_2, result_s )
            rounds +=1
            display_score()

        opponent_1.games_played += 1
        opponent_2.games_played += 1
        return True #game successfull

    def clear_opponents(self):
        """
        Clears the list of opponents in the game object
        """
        logger.info("Clearing the opponents list.")
        self.oponents.clear()

    

    def get_opponents(self) -> List[Team]:
        """
        Returns list of opponents for a given game
        """
        logger.info("Retrieving current list of opponents.")
        return self.opponents

    def prep_opponent(self, opponent: Team):
        """
        Adds an opponent to the opponents list of the game

	    Args:
		    opponent (Team): the team to be added to the opponents list

        Raises:
            ValueError: If there are already two opponents in the opponent list
        """

        if len(self.opponents) >= 2:
            logger.error("Attempted to add opponent '%s' but opponents list is full", opponent.meal)
            raise ValueError("Opponents list is full, cannot add more opponents.")

        # Log the addition of the opponent
        logger.info("Adding opponent '%s' to opponents list", opponent.name)

        self.opponents.append(opponent)

        # Log the current state of opponents
        logger.info("Current opponents list: %s", [opponent.name for opponent in self.opponents])
    

