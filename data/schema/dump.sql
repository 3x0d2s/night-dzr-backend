
-- Таблица: Teams
CREATE TABLE IF NOT EXISTS Teams (
    id BIGINT UNIQUE, 
    name VARCHAR(32) NOT NULL,
	games_played INTEGER NOT NULL,
	win_games INTEGER NOT NULL
);

-- Таблица: Users
CREATE TABLE IF NOT EXISTS Users (
    id BIGINT UNIQUE, 
    name VARCHAR(32) NOT NULL,
	surname VARCHAR(32) NOT NULL,
	patronymic VARCHAR(32) NOT NULL,
	email VARCHAR(128) NOT NULL,
	phone_number VARCHAR(11) NOT NULL,
	password VARCHAR(32) NOT NULL,
	games_played INTEGER NOT NULL,
	win_games INTEGER NOT NULL,
	is_organizer BOOLEAN NOT NULL DEFAULT(false),
	team_id BIGINT DEFAULT(NULL),
	FOREIGN KEY (team_id) REFERENCES Teams(id) ON DELETE SET DEFAULT
);

-- Таблица: Tasks
CREATE TABLE IF NOT EXISTS Tasks (
    id BIGINT UNIQUE, 
    level INTEGER NOT NULL,
	mystery_of_place TEXT NOT NULL,
	place TEXT NOT NULL,
	answer VARCHAR(16) NOT NULL,
	author_id BIGINT DEFAULT(NULL),
	FOREIGN KEY (author_id) REFERENCES Users(id) ON DELETE SET DEFAULT
);

-- Таблица: Games
CREATE TABLE IF NOT EXISTS Games (
    id BIGINT UNIQUE, 
    date_start TIMESTAMP NOT NULL,
	date_end TIMESTAMP NOT NULL,
	name VARCHAR(64) NOT NULL
);

-- Таблица: GamesTasks
CREATE TABLE IF NOT EXISTS GamesTasks (
    id BIGINT UNIQUE, 
    game_id BIGINT NOT NULL,
	task_id BIGINT NOT NULL,
	FOREIGN KEY (game_id) REFERENCES Games(id) ON DELETE CASCADE,
	FOREIGN KEY (task_id) REFERENCES Tasks(id) ON DELETE CASCADE
);

-- Таблица: GamesTeams
CREATE TABLE IF NOT EXISTS GamesTeams (
    id BIGINT UNIQUE, 
    game_id BIGINT NOT NULL,
	team_id BIGINT NOT NULL,
	FOREIGN KEY (game_id) REFERENCES Games(id) ON DELETE CASCADE,
	FOREIGN KEY (team_id) REFERENCES Teams(id) ON DELETE CASCADE
);