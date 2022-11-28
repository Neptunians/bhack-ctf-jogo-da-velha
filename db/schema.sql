CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(32) NOT NULL UNIQUE,
    password  VARCHAR(100) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE games (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    game_key VARCHAR(36) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    winner CHAR(1) NOT NULL DEFAULT '?', 
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (winner IN ("X", "O", "?", "*"))
);

CREATE TABLE moves (
    game_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    value CHAR(1) NOT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (value IN ("X", "O"))
);

INSERT INTO users (username, password)
VALUES ('admin', 'YmhhY2t7ZmxhZ19wYXJhX3Rlc3Rlc30K');

CREATE USER 'ttt_app' IDENTIFIED by 'simples';
GRANT SELECT, INSERT ON ttt.* to ttt_app;
GRANT UPDATE ON ttt.games to ttt_app;

-- CLEAN EVERY 10 MINUTES
SET GLOBAL event_scheduler = ON;

DELIMITER $$

CREATE PROCEDURE DELETE_OLD_GAMES()
BEGIN
    SELECT 
        CURRENT_TIMESTAMP - INTERVAL 10 MINUTE
        INTO @timelimit
    FROM DUAL;

    DELETE FROM moves
    WHERE game_id in (
        SELECT id FROM games
        WHERE created < @timelimit
    );

    DELETE FROM games
    WHERE created < @timelimit;

    commit;
END $$
DELIMITER ;


CREATE EVENT DELETE_OLD_GAMES_EVT
ON SCHEDULE EVERY 2 MINUTE
DO
    CALL DELETE_OLD_GAMES();