PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS categories;


CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

-- Insert trivia categories into the table
INSERT INTO categories (id, name) VALUES
(9, 'General Knowledge'),
(10, 'Entertainment: Books'),
(11, 'Entertainment: Film'),
(12, 'Entertainment: Music'),
(13, 'Entertainment: Musicals & Theatres'),
(14, 'Entertainment: Television'),
(15, 'Entertainment: Video Games'),
(16, 'Entertainment: Board Games'),
(17, 'Science & Nature'),
(18, 'Science: Computers'),
(19, 'Science: Mathematics'),
(20, 'Mythology'),
(21, 'Sports'),
(22, 'Geography'),
(23, 'History'),
(24, 'Politics'),
(25, 'Art'),
(26, 'Celebrities'),
(27, 'Animals'),
(28, 'Vehicles'),
(29, 'Entertainment: Comics'),
(30, 'Science: Gadgets'),
(31, 'Entertainment: Japanese Anime & Manga'),
(32, 'Entertainment: Cartoon & Animations');

CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team TEXT NOT NULL UNIQUE,
    favorite_category INTEGER,
    mascot TEXT,
    deleted BOOLEAN DEFAULT FALSE,
    current_score INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    FOREIGN KEY (favorite_category) REFERENCES categories(id)
);


