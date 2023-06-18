import sqlite3


def create_wordlist_db(db_connection: sqlite3.Connection, wordlist_file: str = "eff_large_wordlist.txt") -> None:
    """Creates the database of numbers and words as a result of parsing
    the provided text file.

    Paramters
    ---------
    db_connection: sqlite3.Connection
        The connection object that represents a connection to the word list database.

    wordlist_file: str
        The text file containing numbers and words, from which the word list database is built.
        Each row of the text file must be formatted such that there are two columns,
        the first of which contains numbers, and the second of which contains words.
        There must be whitespace in between the two columns as well.

    Returns
    -------
        None
    """
    conn = db_connection
    cur = conn.cursor()

    create_wordlist = """CREATE TABLE IF NOT EXISTS "wordlist" (
        "number" INTEGER NOT NULL UNIQUE,
        "word" TEXT NOT NULL
    )
    """
    cur.execute(create_wordlist)

    add_number_and_word = """INSERT INTO "wordlist" ("number", "word") VALUES(?, ?)"""

    with open(wordlist_file, "r", encoding="utf-8") as f:
        with conn:
            while True:
                line = f.readline()

                if line == "":  # end of file
                    break

                number, word = line.split()
                conn.execute(add_number_and_word, (int(number), word))


def get_word(db_connection: sqlite3.Connection, number: int) -> str:
    """Returns a word from the database that matches the provided number.

    Parameters
    ----------
    db_connection: sqlite3.Connection
        The connection object that represents a connection to the wordlist database.

    number: int
        The number used to extract a word from the wordlist database.

    Returns
    -------
    str
        The word associated with the provided `number`.
    """
    conn = db_connection
    cur = conn.cursor()
    fetch_word = """SELECT "word" FROM "wordlist" WHERE "number" = ?;"""
    return cur.execute(fetch_word, (number,)).fetchone()[0]
