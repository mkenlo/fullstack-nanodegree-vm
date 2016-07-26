#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import string


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM matches")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players")
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO players(player_name) VALUES ($$%s$$)" % name.strip()
    cursor.execute(query)
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cursor = conn.cursor()

    query_count_matches = """SELECT COUNT(*) FROM matches 
    WHERE matches.winner=p.player_id or matches.loser=p.player_id"""

    query = """SELECT p.player_id, p.player_name, (COUNT(m.winner))::int as wins,
    (%s)::int as matches
    from players p left outer join matches m on p.player_id=m.winner
    group by p.player_id, p.player_name
    order by wins DESC""" % query_count_matches

    cursor.execute(query)
    result = cursor.fetchall()

    conn.commit()
    conn.close()
    if result:
        return result
    else:
        return []


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cursor = conn.cursor()
    # record match
    cursor.execute(
        "INSERT INTO matches(winner, loser) VALUES (%s,%s)", (winner, loser))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    pairings = list()
    if len(standings) % 2 == 0:
        i = 0
        while i < len(standings):
            player1 = standings[i]
            player2 = standings[i + 1]
            one_pairing = (
                player1[0], player1[1],
                player2[0], player2[1])
            pairings.append(one_pairing)
            i = i + 2

    return pairings
