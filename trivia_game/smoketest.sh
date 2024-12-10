#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

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










check_health

