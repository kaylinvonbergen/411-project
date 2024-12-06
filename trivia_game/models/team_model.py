
class Team:
    team_counter = 1  # Class-level attribute to generate unique IDs

    def __init__(self, team_name, members):
        """
        Initialize a new Team instance.
        """
        self.team_id = Team.team_counter
        Team.team_counter += 1  # Increment counter for unique team IDs
        self.team_name = team_name
        self.members = members  # List of strings
        self.favorite_categories = []  # Start with no favorite categories
        self.games_played = []  # List of game IDs
        self.total_score = 0  # Initialize total score to 0

    def add_favorite(self, category):
        """
        Add a favorite category to the team.
        """
        if category not in self.favorite_categories:
            self.favorite_categories.append(category)
            return f"Category '{category}' added to favorites."
        return f"Category '{category}' is already a favorite."

    def remove_favorite(self, category):
        """
        Remove a favorite category from the team.
        """
        if category in self.favorite_categories:
            self.favorite_categories.remove(category)
            return f"Category '{category}' removed from favorites."
        return f"Category '{category}' is not in the favorites list."

    def update_score(self, score):
        """
        Update the team's total score.
        """
        self.total_score += score
        return f"Team score updated. Total score: {self.total_score}"

    def record_game(self, game_id):
        """
        Add a game ID to the list of games played.
        """
        self.games_played.append(game_id)
        return f"Game ID '{game_id}' recorded."

    def __str__(self):
        """
        String representation of the Team object.
        """
        return (
            f"Team ID: {self.team_id}\n"
            f"Team Name: {self.team_name}\n"
            f"Members: {', '.join(self.members)}\n"
            f"Favorite Categories: {', '.join(self.favorite_categories)}\n"
            f"Games Played: {', '.join(map(str, self.games_played))}\n"
            f"Total Score: {self.total_score}\n"
        )
