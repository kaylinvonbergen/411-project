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

## Setup Instructions:
1. **...**
2. **...**

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
- **Example Request:**
    ```bash
    GET /api/health HTTP/1.1
    Host: localhost:5000
    ```
- **Example Response:**
    ```json
    {
       "status": "healthy"
    }
    ```
