DROP TABLE IF EXISTS teams;
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL UNIQUE,
    current_score INTEGER DEFAULT 0,
    favorite_game_category INTEGER,
    deleted BOOLEAN DEFAULT FALSE
    FOREIGN KEY (favorite_game_category) REFERENCES categories(id)
);