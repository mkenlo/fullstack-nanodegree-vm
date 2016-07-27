#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import string


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    database_name = "tournament"
    try:
        db = psycopg2.connect("dbname={}".format(database_name))
        cursor = db.cursor()
        return db, cursor
    except:
        print("<Oups!! Error occured while connecting to the database>")


def deleteMatches():
    """Remove all the match records from the database."""
    db, cursor=connect()
    cursor.execute("DELETE FROM matches;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db, cursor=connect()
    cursor.execute("DELETE FROM players;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db, cursor=connect()
    cursor.execute("SELECT COUNT(*) FROM players;")
    result=cursor.fetchone()
    db.commit()
    db.close()
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db, cursor=connect()
    query="INSERT INTO players(player_name) VALUES (%s);"
    cursor.execute(query, (name.strip(),))
    db.commit()
    db.close()


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
    db, cursor=connect()

    query="""SELECT p.player_id, p.player_name, (COUNT(m.winner))::int as wins,
    (SELECT COUNT(*) FROM matches
    WHERE matches.winner=p.player_id or matches.loser=p.player_id)::int as matches
    from players p left outer join matches m on p.player_id=m.winner
    group by p.player_id, p.player_name
    order by wins DESC"""
   
    cursor.execute(query)
    result=cursor.fetchall()

    db.commit()
    db.close()
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
    db, cursor=connect()
    # record match
    cursor.execute(
        "INSERT INTO matches(winner, loser) VALUES (%s,%s)", (winner, loser))
    db.commit()
    db.close()


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
    standings=playerStandings()
    pairings=list()

    if len(standings) % 2 == 0:
        i=0
        while i < len(standings):
            player1=standings[i]
            player2=standings[i + 1]
            one_pairing=(
                player1[0], player1[1],
                player2[0], player2[1])
            pairings.append(one_pairing)
            i=i + 2

    return pairings
