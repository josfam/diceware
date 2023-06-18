import argparse
import random
from pathlib import Path
import sqlite3
import sys

from rich import box
from rich.console import Console
from rich.table import Table

import dice_db

DICE_NUMBER = 5  # You need this many dice to get a word from the word list
DICE_FACES = 6
DB = 'wordlist.db'

parser = argparse.ArgumentParser()
parser.add_argument(
    '-n',
    '--numdice',
    type=int,
    default=3,
    help='How many dice rows you want to roll. Defaults to 3',
)
args = parser.parse_args()
dice_rows = args.numdice
console = Console()


def main():
    grid = Table.grid(collapse_padding=True, padding=0)

    # create the word list database if it does not already exist
    if not Path.exists(Path('wordlist.db')):
        conn = sqlite3.connect(DB)
        dice_db.create_wordlist_db(conn)

    conn = sqlite3.connect(DB)
    for _ in range(dice_rows):
        # store the every 5 dice rolled, and the 5-digit number that resulted
        dice_group = []
        five_digit_num = []

        for _ in range(DICE_NUMBER):
            die = Table(show_header=False, box=box.ROUNDED, pad_edge=True, leading=1)
            face = str(random.randint(1, DICE_FACES))
            die.add_row(face)
            dice_group.append(die)
            five_digit_num.append(face)

        # add the word made from the dice to the same row as the dice
        word_face = Table(show_header=False, box=box.ROUNDED, pad_edge=True, min_width=15, row_styles=['bold'])
        word_face.add_row(dice_db.get_word(conn, int(''.join(five_digit_num))))
        dice_group.append(word_face)
        grid.add_row(*dice_group)

    console.print(grid)


if __name__ == '__main__':
    main()
