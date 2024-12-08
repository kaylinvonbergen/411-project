from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
import sqlite3
from werkzeug.exceptions import BadRequest, Unauthorized
from .config import ProductionConfig



from trivia_game.models.password_model import *
from trivia_game.models.team_model import *
from trivia_game.models.game_model import GameModel
from trivia_game.db import db

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables
  ##########################################################
    #
    # User management
    #
    ##########################################################

    @app.route('/api/create-user', methods=['POST'])
    def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/delete-user', methods=['DELETE'])
    def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)


            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

        

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500
        

    
    ##########################################################
    #
    # Teams
    #
    ##########################################################


@app.route('/random-dog')
def random_dog():
    try:
        # Call the model function to get a random dog image URL
        dog_image_url = get_random_dog_image()
        return jsonify({"dog_image_url": dog_image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/create-team', methods=['POST'])
def add_team() -> Response:
    """
    Route to add a new team to the database.

    Expected JSON Input:
        - team (str): The name of the team.
        - favorite_categories (list[int]): List of category IDs for the team's favorite categories.

    Returns:
        JSON response indicating the success of the team addition.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue adding the team to the database.
    """
    app.logger.info('Creating new team')
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Extract and validate required fields
        team = data.get('team')
        favorite_categories = data.get('favorite_categories')

        if not team or not isinstance(favorite_categories, list) or not all(isinstance(cat, int) for cat in favorite_categories):
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Call the create_team function to add the team to the database
        app.logger.info('Adding team: %s, %s', team, favorite_categories)
        create_team(team, favorite_categories)

        app.logger.info("Team added: %s", team)
        return make_response(jsonify({'status': 'success', 'team': team}), 201)
    
    except ValueError as e:
        app.logger.error("Failed to add team: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 400)
    
    except Exception as e:
        app.logger.error("Failed to add team: %s", str(e))
        return make_response(jsonify({'error': 'Internal server error'}), 500)



@app.route('/api/delete-team/<int:team_id>', methods=['DELETE'])
def delete_team_route(team_id: int) -> Response:
    """
    Route to delete a team by its ID. This performs a soft delete by marking it as deleted.

    Path Parameter:
        - team_id (int): The ID of the team to delete.

    Returns:
        JSON response indicating success of the operation or error message.
    """
    try:
        app.logger.info(f"Deleting team by ID: {team_id}")

        # Call the delete_team function to perform the soft delete
        delete_team(team_id)
        return make_response(jsonify({'status': 'success'}), 200)
    
    except ValueError as e:
        app.logger.error(f"Error deleting team: {e}")
        return make_response(jsonify({'error': str(e)}), 400)
    
    except Exception as e:
        app.logger.error(f"Error deleting team: {e}")
        return make_response(jsonify({'error': 'Internal server error'}), 500)
    

@app.route('/api/get-team-by-id/<int:team_id>', methods=['GET'])
def get_team_by_id_route(team_id: int) -> Response:
    """
    Route to get a team by its ID.

    Path Parameter:
        - team_id (int): The ID of the team.

    Returns:
        JSON response with the team details or error message.
    """
    try:
        app.logger.info(f"Retrieving team by ID: {team_id}")

        team = get_team_by_id(team_id)  # Fetch team by ID
        return make_response(jsonify({'status': 'success', 'team': team.to_dict()}), 200)
    
    except ValueError as e:
        app.logger.error(f"Error retrieving team by ID: {e}")
        return make_response(jsonify({'error': str(e)}), 400)
    
    except Exception as e:
        app.logger.error(f"Error retrieving team by ID: {e}")
        return make_response(jsonify({'error': 'Internal server error'}), 500)



@app.route('/api/get-team-by-name/<string:team_name>', methods=['GET'])
def get_team_by_name_route(team_name: str) -> Response:
    """
    Route to get a team by its name.

    Path Parameter:
        - team_name (str): The name of the team.

    Returns:
        JSON response with the team details or error message.
    """
    try:
        app.logger.info(f"Retrieving team by name: {team_name}")

        if not team_name:
            return make_response(jsonify({'error': 'Team name is required'}), 400)

        team = get_team_by_name(team_name)  # Fetch team by name
        return make_response(jsonify({'status': 'success', 'team': team.to_dict()}), 200)
    
    except ValueError as e:
        app.logger.error(f"Error retrieving team by name: {e}")
        return make_response(jsonify({'error': str(e)}), 400)
    
    except Exception as e:
        app.logger.error(f"Error retrieving team by name: {e}")
        return make_response(jsonify({'error': 'Internal server error'}), 500)




@app.route('/api/update-team-stats/<int:team_id>', methods=['POST'])
def update_team_stats_route(team_id: int) -> Response:
    """
    Route to update the statistics of a team based on game results.

    Path Parameter:
        - team_id (int): The ID of the team.

    JSON Body:
        - result (str): The result of the game, either 'win' or 'loss'.

    Returns:
        JSON response indicating success or error message.
    """
    try:
        # Get the JSON data from the request
        data = request.get_json()

        # Extract result and validate
        result = data.get('result')

        if result not in ['win', 'loss']:
            return make_response(jsonify({'error': "Invalid result. Must be 'win' or 'loss'."}), 400)

        app.logger.info(f"Updating stats for team ID: {team_id} with result: {result}")

        # Call the update_team_stats function to update the stats
        update_team_stats(team_id, result)
        return make_response(jsonify({'status': 'success', 'team_id': team_id, 'result': result}), 200)

    except ValueError as e:
        app.logger.error(f"Error updating team stats: {e}")
        return make_response(jsonify({'error': str(e)}), 400)

    except Exception as e:
        app.logger.error(f"Error updating team stats: {e}")
        return make_response(jsonify({'error': 'Internal server error'}), 500)

    
    ##########################################################
    #
    # Game
    #
    ##########################################################

    from trivia_game.models.game_model import GameModel


game_model = GameModel()

@app.route('/api/add-opponent', methods=['POST'])
def add_opponent():
    """
    Route to add an opponent to the game.

    Expected JSON Input:
        - team_id (int): The ID of the team to add as an opponent.

    Returns:
        JSON response indicating success or error message.
    """
    try:
        data = request.get_json()
        team_id = data.get('team_id')

        if not team_id:
            return make_response(jsonify({'error': 'Team ID is required'}), 400)

        # Fetch the team object using its ID
        team = get_team_by_id(team_id)  # Assuming get_team_by_id is defined elsewhere

        # Add the team as an opponent
        game_model.prep_opponent(team)
        return make_response(jsonify({'status': 'success', 'team': team.name}), 200)
    
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route('/api/start-game', methods=['POST'])
def start_game():
    """
    Route to start a game between two opponents.

    Returns:
        JSON response with the game's result or an error message.
    """
    try:
        result = game_model.game()  # Run the game logic

        return make_response(jsonify({'status': 'success', 'result': 'Game completed successfully'}), 200)
    
    except ValueError as e:
        return make_response(jsonify({'error': str(e)}), 400)
    except Exception as e:
        return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route('/api/get-opponents', methods=['GET'])
def get_opponents():
    """
    Route to get the list of opponents in the current game.

    Returns:
        JSON response with the list of opponents or an error message.
    """
    try:
        opponents = game_model.get_opponents()
        opponents_list = [opponent.to_dict() for opponent in opponents]  # Assuming Team objects have a `to_dict` method
        return make_response(jsonify({'status': 'success', 'opponents': opponents_list}), 200)
    
    except Exception as e:
        return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route('/api/clear-opponents', methods=['POST'])
def clear_opponents():
    """
    Route to clear the opponents in the current game.

    Returns:
        JSON response indicating success or an error message.
    """
    try:
        game_model.clear_opponents()
        return make_response(jsonify({'status': 'success', 'message': 'Opponents cleared'}), 200)
    
    except Exception as e:
        return make_response(jsonify({'error': 'Internal server error'}), 500)
    


if __name__ == "__main__":
    app.run(debug=True)

