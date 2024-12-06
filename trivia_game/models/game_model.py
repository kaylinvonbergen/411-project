 class GameModel:
    """
    A class to manage games between teams.

    Attributes:
        opponents (List[Team]): A list of current opponents.
    """
    
    '''
    API call
    https://opentdb.com/api.php?amount=1&difficulty=easy&type=multiple
    which generates 1 trivia question in general knowledge, easy difficulty, multiple choice, default encoding.
    '''

    def __init__(self):
        """
        Initializes the GameModel object with an empty list of combatants
        """
        self.opponents: List[Team] = []

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

        # Log the start of the game
        logger.info("Game started between %s and %s", opponent_1.name, opponent_2.name)

        # API CALLS GO HERE, REPLACE ANSWER, DETERMINE HOW WE CALL API.. UTILS?
        answer = "answer"

        #Determine if the teams entered the correct answer (store true or false below)
        score_1 = get_result(opponent_1, answer)
        score_2 = get_result(opponent_2, answer)

        # Log this
        logger.info("Score for %s: %.3f", opponent_1.name, score_1)
        logger.info("Score for %s: %.3f", opponent_2.name, score_2)

        # Determine win/tie, update stats and log
        if score_1 and not score_2:
            winner = opponent_1
            loser = opponent_2
            logger.info("The winner is: %s", winner.name)
            update_team_stats(winner.id, 'win')
            update_team_stats(loser.id, 'loss')
        else if not score_1 and score_2:
            winner = opponent_2
            loser = opponent_1
            logger.info("The winner is: %s", winner.name)
            update_team_stats(winner.id, 'win')
            update_team_stats(loser.id, 'loss')
        else if :
            if score_1:
                result_s = "correct"
                update_team_stats(opponent_1.id, 'win')
                update_team_stats(opponent_2.id, 'win')
            else:
                result_s = "incorrect" 
                update_team_stats(opponent_1.id, 'loss')
                update_team_stats(opponent_2.id, 'loss')
            logger.info("There was a tie between %s & %s. Both teams were %s." opponent_1, opponent_2, result_s )


        return winner.name #???

    def clear_opponents(self):
        """
        Clears the list of opponents in the game object
        """
        logger.info("Clearing the opponents list.")
        self.oponents.clear()

    def get_result(self, opponent: Team, answer) -> float:
        """
        Determines the correctness of a team based on their answer as compared to the correct answer

        Args:
		    opponent (Team): the opponent to judge

        Returns:
		    boolean: True if correct, False otherwise 
        """
        result = False #to be returned.
        
        # logic to take in input & change result to true or false based on if they got it right

        # Log the calculated score
        logger.info("Result for %s: %.3f", opponent.name, result)

        return result

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
