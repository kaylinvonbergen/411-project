DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS users;

CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL UNIQUE,
    current_score INTEGER DEFAULT 0,
    favorite_game_category INTEGER,
    deleted BOOLEAN DEFAULT FALSE,
    password_hash TEXT NOT NULL,
    FOREIGN KEY (favorite_game_category) REFERENCES categories(id)
);


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL,
    password_hash TEXT NOT NULL
);