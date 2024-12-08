DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS users;

CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL UNIQUE,
    FOREIGN KEY (favorite_game_category) REFERENCES categories(id)
    mascot TEXT,
    deleted BOOLEAN DEFAULT FALSE,
    current_score INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    
    
);


