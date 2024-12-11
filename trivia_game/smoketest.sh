#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5002/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."

  # Perform the health check using curl
  response=$(curl -s -X GET "$BASE_URL/health")

  # Use jq to parse the JSON and check if the status is "healthy"
  if echo "$response" | jq -e '.status == "healthy"' > /dev/null; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


# Function to initialize the database
init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    exit 1
  fi
}

##############################################
#
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'

  

  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}


##############################################
#
# Teams
#
##############################################


random_dog_smoke_test() {
  echo "Testing random-dog route..."

  # Send a GET request to the /random-dog endpoint
  response=$(curl -s -X GET "$BASE_URL/random-dog")

  # Check if the response contains a valid dog_image_url
  if echo "$response" | grep -q '"dog_image_url":'; then
    echo "Random dog image URL received successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Dog Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve random dog image."
    echo "Response: $response"
    exit 1
  fi
}


# Function to add a team (combatant)
create_team() {
  team=$1
  favorite_category=$2

  echo "Adding a team..."
  
  # Make the API call and store the response
  response=$(curl -s -X POST "$BASE_URL/create-team" -H "Content-Type: application/json" \
   -d "{\"team\":\"$team\", \"favorite_category\":$favorite_category}")
   
  # Check if the response contains the success status
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Team added successfully."
  else
    echo "Failed to add team."
    echo "Response: $response"
    exit 1
  fi
}


delete_team() {
  id=$1

  echo "Deleting team by ID ($id)..."

  response=$(curl -s -X DELETE "$BASE_URL/delete-team/$id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Team deleted successfully by ID ($id)."
  else
    echo "Failed to delete team by ID ($id)."
    exit 1
  fi

}


clear_teams() {
  echo "Clearing teams from database..."

  curl -s -X DELETE "$BASE_URL/clear-teams" | grep -q '"status": "success"'
}


get_team_by_name() {
  team=$1

  echo "Getting team by name ($team)..."
  response=$(curl -s -X GET "$BASE_URL/get-team-by-name/$team")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Team retrieved successfully by team ($team)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Team JSON (Name $team):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get team by name ($team)."
    exit 1
  fi
}

get_team_by_id() {
  id=$1

  echo "Retrieving team by ID ($id)..."

  response=$(curl -s "$BASE_URL/get-team-by-id/$id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Team retrieved successfully by ID ($id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Team JSON (ID $id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get team by ID ($id)."
    exit 1
  fi
}


update_team_stats() {
  team_id=$1
  result=$2

  echo "Testing update-team-stats for team ID ($team_id) with result ($result)..."

  # Send a POST request to the API to update the team stats
  response=$(curl -s -X POST "$BASE_URL/update-team-stats/$team_id" -H "Content-Type: application/json" -d "{\"result\":\"$result\"}")

  # Check if the response contains the success status
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Team stats updated successfully for team ID ($team_id) with result ($result)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Update Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to update team stats for team ID ($team_id)."
    echo "Response: $response"
    exit 1
  fi
}

# game stuff

# Function to perform a smoke test for the /api/add-opponent route
add_opponent() {
  team_id=$1  # The team_id to be added as an opponent

  echo "Testing /api/add-opponent with team_id ($team_id)..."

  # Prepare the JSON payload
  json_payload="{\"team_id\":$team_id}"

  # Send a POST request to the /api/add-opponent route
  response=$(curl -s -X POST "$BASE_URL/add-opponent" -H "Content-Type: application/json" -d "$json_payload")

  # Check if the response contains a success status
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Opponent added successfully for team ID ($team_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Add Opponent Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add opponent for team ID ($team_id)."
    echo "Response: $response"
    exit 1
  fi
}

clear_opponents() {
  echo "Testing clear_opponents method..."

  # Send a request to trigger the clear_opponents method (if it's exposed via an API)
  response=$(curl -s -X POST "$BASE_URL/clear-opponents")

  # Check if the opponents list is now empty (assuming there's a way to check the list, e.g., an endpoint)
  response=$(curl -s -X GET "$BASE_URL/get-opponents")

  if echo "$response" | grep -q '"opponents": \[\]'; then
    echo "Opponents list cleared successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Clear Opponents Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to clear opponents list."
    echo "Response: $response"
    exit 1
  fi
}



# Function to perform a smoke test for the /api/start-game route
start_game() {
  echo "Testing /api/start-game..."

  # Send a POST request to the /api/start-game route
  response=$(curl -s -X POST "$BASE_URL/start-game")

  # Check if the response contains a success status and the expected result message
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Game started successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Start Game Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to start the game."
    echo "Response: $response"
    exit 1
  fi
}



check_health
check_db
init_db
random_dog_smoke_test
create_user
login_user
create_team "peebo" 1
delete_team 1
clear_teams
create_team "gorp" 3
create_team "boing" 7
get_team_by_name "gorp"
get_team_by_id 1
update_team_stats 1 "win"
clear_opponents
add_opponent 1
add_opponent 2
start_game


