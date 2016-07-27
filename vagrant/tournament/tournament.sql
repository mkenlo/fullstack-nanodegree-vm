
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

DROP TABLE IF EXISTS players;
CREATE TABLE players
(
  player_id SERIAL NOT NULL,
  player_name text NOT NULL,
  CONSTRAINT player_pkey PRIMARY KEY (player_id)
);

DROP TABLE IF EXISTS matches;
CREATE TABLE matches
(
  match_id SERIAL NOT NULL,
  winner integer NOT NULL REFERENCES players(player_id),
  loser integer NOT NULL REFERENCES players(player_id),
  CONSTRAINT match_pkey PRIMARY KEY (match_id)
);


