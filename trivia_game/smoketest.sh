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
# Meals
#
##############################################

# Function to add a team (combatant)
create_team() {
  echo "Adding a team..."
  response=$(curl -s -X POST "$BASE_URL/create-team" -H "Content-Type: application/json" \
    -d '{"team":"TeamName", "favorite_categories":[1, 2, 3]}')
  
  # Print the full response to debug
  echo "Response: $response"
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Team added successfully."
  else
    echo "Failed to add team."
    echo "Error Response JSON:"
    echo "$response" | jq .  # Print the full error response
    exit 1
  fi
}




check_health
init_db
create_user
login_user
create_team


