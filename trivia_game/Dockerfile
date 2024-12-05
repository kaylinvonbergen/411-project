# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the env file to the container
COPY .env /app/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite3
RUN apt-get update && apt-get install -y sqlite3

# Add a shell script that loads the .env file and handles database creation
COPY ./sql/create_db.sh /app/sql/create_db.sh
COPY ./sql/create_team_table.sql /app/sql/create_team_table.sql
RUN chmod +x /app/sql/create_db.sh

# Define a volume for persisting the database
VOLUME ["/app/db"]

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run the entrypoint script when the container launches
CMD ["/app/entrypoint.sh"]