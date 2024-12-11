from flask import Flask
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
import sqlite3
from werkzeug.exceptions import BadRequest, Unauthorized


from config import ProductionConfig
from trivia_game.models.password_model import *
from trivia_game.models.team_model import *
from trivia_game.models.game_model import GameModel
from trivia_game.utils.sql_utils import check_database_connection, check_table_exists

load_dotenv()

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    
    game_model = GameModel()
    
    

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)


    @app.route('/api/db-check', methods=['GET'])
    def db_check() -> Response:
        """
        Route to check if the database connection and teams table are functional.

        Returns:
            JSON response indicating the database health status.
        Raises:
            404 error if there is an issue with the database.
        """
        try:
            app.logger.info("Checking database connection...")
            check_database_connection()
            app.logger.info("Database connection is OK.")
            app.logger.info("Checking if teams table exists...")
            check_table_exists("teams")
            app.logger.info("teams table exists.")
            return make_response(jsonify({'database_status': 'healthy'}), 200)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 404)
        
    @app.route('/api/init-db', methods=['POST'])
    def init_db():
        """
        Initialize or recreate database tables.

        This route initializes the database tables defined in the SQLAlchemy models.
        If the tables already exist, they are dropped and recreated to ensure a clean
        slate. Use this with caution as all existing data will be deleted.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.

        Logs:
            Logs the status of the database initialization process.
        """
        try:
            with app.app_context():
                app.logger.info("Dropping all existing tables.")
                db.drop_all()  # Drop all existing tables
                app.logger.info("Creating all tables from models.")
                db.create_all()  # Recreate all tables
            app.logger.info("Database initialized successfully.")
            return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
        except Exception as e:
            app.logger.error("Failed to initialize database: %s", str(e))
            return jsonify({"status": "error", "message": "Failed to initialize database."}), 500

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
                dog_image_url = Team.get_random_dog_image()
                return jsonify({"dog_image_url": dog_image_url})
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            

    @app.route('/api/create-team', methods=['POST'])
    def add_team() -> Response:
        """
        Route to add a new team to the database.

        Expected JSON Input:
            - team (str): The name of the team.
            - favorite_category (int): The ID of the team's favorite category.

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
            app.logger.info("Received data: %s", data)  # Log the data

            # Extract and validate required fields
            team = data.get('team')
            favorite_category = data.get('favorite_category')

            if not team or not isinstance(favorite_category, int):
                return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

            # Call the create_team function to add the team to the database
            app.logger.info('Adding team: %s, %s', team, favorite_category)
            create_team(team, favorite_category)

            app.logger.info("Team added: %s", team)
            return make_response(jsonify({'status': 'success', 'team': team}), 201)
        
        except ValueError as e:
            app.logger.error("Failed to add team: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 400)
        
        except Exception as e:
            app.logger.error("Failed to add team: %s", str(e))
            return make_response(jsonify({'error': 'Internal server error'}), 500)




    @app.route('/api/delete-team/<int:id>', methods=['DELETE'])
    def delete_team_route(id: int) -> Response:
        """
        Route to mark a team as deleted in the database.

        Expected URL Parameter:
            - id (int): The unique ID of the team to be deleted.

        Returns:
            JSON response indicating the success or failure of the operation.
        Raises:
            400 error if the team has already been deleted or doesn't exist.
            500 error if there is an issue with the database operation.
        """
        
        try:
            app.logger.info(f"Deleting team by ID: {id}")
            # Call the delete_team function to mark the team as deleted in the database
            delete_team(id)

            app.logger.info(f"Team with ID {id} marked as deleted.")
            return make_response(jsonify({'status': 'success'}), 200)

        except Exception as e:
            app.logger.error(f"Failed to delete team with ID {id}: {str(e)}")
            return make_response(jsonify({'error': 'Internal server error'}), 500)


    @app.route('/api/clear-teams', methods=['DELETE'])
    def clear_catalog() -> Response:
        """
        Route to clear all teams (recreates the table).

        Returns:
            JSON response indicating success of the operation or error message.
        """
        try:
            app.logger.info("Clearing the teams")
            clear_teams()
            return make_response(jsonify({'status': 'success'}), 200)
        except Exception as e:
            app.logger.error(f"Error clearing catalog: {e}")
            return make_response(jsonify({'error': str(e)}), 500)    

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

                team = Team.get_team_by_id(team_id)  # Fetch team by ID
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

                team = Team.get_team_by_name(team_name)  # Fetch team by name
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
                Team.update_team_stats(team_id, result)
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



    @app.route('/api/add-opponent', methods=['POST'])
    def add_opponent():
        """Route to add an opponent to the game."""
        try:
            data = request.get_json()
            team_id = data.get('team_id')

            if not team_id:
                return make_response(jsonify({'error': 'Team ID is required'}), 400)

            team = Team.get_team_by_id(team_id)
            game_model.prep_opponent(team)

            return make_response(jsonify({'status': 'success', 'team': team.name}), 200)
        except ValueError as e:
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Error adding opponent: {e}")
            return make_response(jsonify({'error': 'Failed to add opponent'}), 500)





    @app.route('/api/start-game', methods=['POST'])
    def start_game():
        """Route to start a game."""
        try:
            result = game_model.game()
            return make_response(jsonify({'status': 'success', 'result': 'Game completed successfully'}), 200)
        except ValueError as e:
            return make_response(jsonify({'error': str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Error starting game: {e}")
            return make_response(jsonify({'error': 'Failed to start game'}), 500)


    @app.route('/api/get-opponents', methods=['GET'])
    def get_opponents():
        """Route to retrieve the list of opponents."""
        try:
            opponents = game_model.get_opponents()
            opponents_list = [opponent.to_dict() for opponent in opponents]
            return make_response(jsonify({'status': 'success', 'opponents': opponents_list}), 200)
        except Exception as e:
            app.logger.error(f"Error retrieving opponents: {e}")
            return make_response(jsonify({'error': 'Failed to retrieve opponents'}), 500)


    @app.route('/api/clear-opponents', methods=['POST'])
    def clear_opponents():
        """Route to clear the list of opponents."""
        try:
            game_model.clear_opponents()
            return make_response(jsonify({'status': 'success', 'message': 'Opponents cleared'}), 200)
        except Exception as e:
            app.logger.error(f"Error clearing opponents: {e}")
            return make_response(jsonify({'error': 'Failed to clear opponents'}), 500)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5002)