from trivia_game.models.team_model import * 
from trivia_game.utils.logger import *
from typing import List

from dataclasses import dataclass
import logging
import sqlite3
from typing import Any
import requests
import html
import random
import time

from trivia_game.utils.sql_utils import get_db_connection
from trivia_game.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


class GameModel:
    """
    A class to manage games between teams.

    Attributes:
        opponents (List[Team]): A list of current opponents.
        rounds (int): number of rounds played in the game
        session_token (str): the session token for opentdb
    """
    def __init__(self):
        """
        Initializes the GameModel object with an empty list of combatants, rounds = 0, and creates a session token
        """

        self.rounds=0
        self.opponents: List[Team] = []

        logger.info("Getting session token")
        url = "https://opentdb.com/api_token.php?command=request"
        time.sleep(5)
        response = requests.get(url)
        time.sleep(5)
        data = response.json()
        
        if data['response_code'] == 0: 
            logger.info("session token created!")
            self.session_token = data['token']
        else:
            logger.error("Failed to get session token :(")
            self.session_token = ""


    def display_score(self):
        """
        Displays current scores and category information
        """
        # Log current scores
        logger.info("Current score is:")
        logger.info(" %s: %s correct out of %s questions", self.opponents[0].team, self.opponents[0].current_score, self.rounds)
        logger.info(" %s: %s correct out of %s questions", self.opponents[1].team, self.opponents[1].current_score, self.rounds)

        # Fetch trivia stats from /api/trivia/stats
        try:
            logger.info("Fetching categories . . .")
            time.sleep(5)
            response = requests.get("https://opentdb.com/api_category.php")
            time.sleep(5)
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

            


    def get_result(self, opponent: Team, answer) -> bool:
        """
        Determines the correctness of a team based on their answer as compared to the correct answer

        Args:
		    opponent (Team): the opponent to judge
            answer (String): the correct answer to the question

        Returns:
		    boolean: True if correct, False otherwise 
        """
        teamanswer = input("Please enter your answer: ")
        result = (answer == teamanswer)

        return result

    def game(self) -> str:
        """
        Plays two rounds of trivia between two opponents

	    Returns:
		    boolean: whether the game finished

        Raises:
            ValueError: if there are less than two opponents.
            ValueError: if category list is empty.
            ValueError: if there are less than two opponents.
            ValueError: if no trivia questions were found.
            ValueError: error fetching trivia data.
        """

        

        if len(self.opponents) < 2:
            logger.error("Not enough teams to start a Game.")
            raise ValueError("Two teams must be in the game.")

        opponent_1 = self.opponents[0]
        opponent_2 = self.opponents[1]

        
        # Ensure each opponent has a favorite category
        if not opponent_1.favorite_category:
            raise ValueError(f"{opponent_1.team}'s favorite category is not set.")
        if not opponent_2.favorite_category:
            raise ValueError(f"{opponent_2.team}'s favorite category is not set.")   

        categories = [opponent_1.favorite_category, opponent_2.favorite_category]


        # Log the start of the game
        logger.info("Game started between opponent 1: %s and opponent 2: %s", opponent_1.team, opponent_2.team)

        for i, category in enumerate(categories): #two rounds
            logger.info("The category for round %d is: %s", i + 1, category)
            try:
                logger.info("Getting question %s of this round from Open Trivia", i)
                
                q_type="boolean" #first round is a true or false
                if i == 1: 
                    q_type = "multiple" #second round will be multiple choice
                
                if self.session_token == "":
                    
                    logger.info("%s question is being pulled without a session token", category)
                    time.sleep(5)
                    api_url =  f'https://opentdb.com/api.php?amount=1&category={category}&type={q_type}'
                    time.sleep(5)
                else:    
                    logger.info("%s question is being pulled with a session token", category)
                    time.sleep(5)
                    api_url = f'https://opentdb.com/api.php?amount=1&category={category}&type={q_type}&token={self.session_token}'
                    time.sleep(5)
                
                
                # Fetch the data from the API
                time.sleep(5)
                response = requests.get(api_url)
                time.sleep(5)
                response.raise_for_status() 

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
                
            except ValueError as ve:
                raise ValueError("Error fetching trivia data") from ve

            
            
            
            logger.info(f"TEAM 1: Question: {question}")
            score_1 = self.get_result(opponent_1, answer)
            logger.info("answer stored.")
            logger.info(f"TEAM 2: Question: {question}")
            score_2 = self.get_result(opponent_2, answer)
            logger.info("answer stored.")
            

            # Log scores
            logger.info("Result for %s: %.3f", opponent_1.team, score_1)
            logger.info("Result for %s: %.3f", opponent_2.team, score_2)

            logger.info("determining victory . . .")

            # Determine win/tie, update stats and log
            if score_1 and not score_2:
                winner = opponent_1
                loser = opponent_2
                logger.info("The winner is: %s", winner.team)
                winner.team_score += 1
            elif not score_1 and score_2:
                winner = opponent_2
                loser = opponent_1
                logger.info("The winner is: %s", winner.team)
                winner.team_score += 1
            else:
                if score_1:
                    result_s = "correct"
                    opponent_1.current_score += 1
                    opponent_2.current_score += 1
                else:
                    result_s = "incorrect" 
                    logger.info("There was a tie between %s & %s. Both teams were %s.", opponent_1, opponent_2, result_s )
            logger.info("updating data . . .")
            self.rounds += 1
            opponent_1.games_played += 1
            opponent_2.games_played += 1
            self.display_score()


        return True #game successfull

    def clear_opponents(self):
        """
        Clears the list of opponents in the game object
        """
        logger.info("Clearing the opponents list.")
        self.opponents.clear()

    

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

        if len(self.opponents) > 2:
            logger.error("Attempted to add opponent '%s' but opponents list is full", opponent.team)
            raise ValueError("Opponents list is full, cannot add more opponents.")

        # Log the addition of the opponent
        logger.info("Adding opponent '%s' to opponents list", opponent.team)

        self.opponents.append(opponent)

        # Log the current state of opponents
        logger.info("Current opponents list: %s", [opponent.team for opponent in self.opponents])
    

