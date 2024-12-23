# Trivia Game Application

## High Level Description:
The Trivia Game Application is a web-based platform designed to facilitate trivia competitions between teams. By leveraging the Open Trivia Database (OpenTDB) API, the application allows teams to compete in trivia games, customize their experience with favorite categories, and track their performance on a leaderboard. With features such as team management, dynamic question fetching, and score tracking, the application provides an engaging and interactive trivia experience.

---

## Features:

- **Team Management**:
  - Create a team with attributes such as name, mascot, and favorite trivia categories.
  - Update or remove favorite categories for a team.
  - Soft delete teams while preserving their historical data.
  
- **Game Management**:
  - Create and manage trivia games with questions tailored to team preferences.
  - Conduct trivia rounds and determine winners.
  - Track scores and display performance on a leaderboard.
  
- **Trivia Data Integration**:
  - Fetch trivia categories and questions dynamically from OpenTDB.
  - Avoid repeated questions during a game using session tokens.

---

## API Routes:

#### Route: /api/health
- **Request Type:** `GET`
- **Purpose:** Verify the service is running and healthy.
- **Request Parameters:** None
- **Response Format:**
    - Success Response Example:
        - Code: 200
        - Content:
            ```json
            {
               "status": "healthy"
            }
            ```
    - Example Request:
      ```bash
      GET /api/health HTTP/1.1
      Host: localhost:5000
      ```
    - Example Response:
      ```json
      {
         "status": "healthy"
      }
      ```
      
#### Route: /api/create-user
- **Request Type:** `POST`
- **Purpose:** Create a new user account with a username and password.
- **Request Body:**
    - `username` (String): The desired username for the user.
    - `password` (String): The password for the user.
- **Response Format:**
    - Success Response Example:
        - Code: 201
        - Content:
            ```json
            {
               "status": "user added",
               "username": "example_user"
            }
            ```
    - Failure Response Example:
        - Code: 400
        - Content:
            ```json
            {
               "error": "Invalid input, both username and password are required"
            }
            ```
        - Code: 500
        - Content:
            ```json
            {
               "error": "Internal server error"
            }
            ```
- **Example Request:**
    ```bash
    curl -X POST http://localhost:5000/api/create-user -H "Content-Type: application/json" -d '{
        "username": "example_user",
        "password": "securepassword"
    }'
    ```
- **Example Response:**
    ```json
    {
       "status": "user added",
       "username": "example_user"
    }
    ```
#### Route: /api/delete-user
- **Request Type:** `DELETE`
- **Purpose:** Users can delete their account by providing their username.
- **Request Body:**
    - `username` (String): The username of the account to be deleted.
- **Response Format:**
    - Success Response Example:
        - Code: 200
        - Content:
            ```json
            {
              "status": "user deleted",
              "username": "example_user"
            }
            ```
        - Example Request:
            ```json
            {
               "username": "example_user"
            }
            ```
        - Example Response:
            ```json
            {
                "status": "user deleted",
                "username": "example_user"
            }
            ```

#### Route: /api/login
- **Request Type:** `POST`
- **Purpose:** Log in a user by validating their username and password.
- **Request Body:**
    - `username` (String): The username of the user.
    - `password` (String): The password of the user.
- **Response Format:**
    - Success Response Example:
        - Code: 200
        - Content:
            ```json
            {
               "message": "User example_user logged in successfully."
            }
            ```
    - Failure Response Example:
        - Code: 400
        - Content:
            ```json
            {
               "error": "Invalid request payload. 'username' and 'password' are required."
            }
            ```
        - Code: 401
        - Content:
            ```json
            {
               "error": "Invalid username or password."
            }
            ```
        - Code: 500
        - Content:
            ```json
            {
               "error": "An unexpected error occurred."
            }
            ```
- **Example Request:**
    ```bash
    curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d '{
        "username": "example_user",
        "password": "securepassword"
    }'
    ```
- **Example Response:**
    ```json
    {
       "message": "User example_user logged in successfully."
    }
    ```

## RUNNING TESTS:

to run UNITS TESTS    build + run tests-dockerfile

to run SMOKETESTS     DO NOT RUN IN DOCKER, run outside after running python app.py in another terminal. You will also have to interact with the python app to see answer question functionality :)
