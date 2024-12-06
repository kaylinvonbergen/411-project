 class GameModel:

    def __init__(self):
        self.opponents: List[Team] = []

    def battle(self) -> str:
        logger.info("Answer the trivia question!")

        if len(self.combatants) < 2:
            logger.error("Not enough teams to start a Game.")
            raise ValueError("Two players must be in the game.")

        opponent_1 = self.opponents[0]
        opponent_2 = self.opponents[1]
