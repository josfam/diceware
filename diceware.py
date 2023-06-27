import argparse
import copy
import random
from pathlib import Path
import sqlite3
import sys
import os
import re

from rich import box
from rich.console import Console
from rich.table import Table
from typing import List, Union

import dice_db

DICE_NUMBER = 5  # You need this many dice to get a word from the word list
DICE_FACES = 6
DB = 'wordlist.db'


class DiceRows:
    def __init__(self, dice_rows: List[List[int]]):
        self.dice_rows = dice_rows

    def randomize_one(self, row: int) -> None:
        self.dice_rows[row] = []
        for _ in range(5):
            self.dice_rows[row].append(random.randint(1, DICE_FACES))

    def randomize_all(self) -> None:
        for row in self.dice_rows:
            self.randomize_one(0)

    def get_all_rows(self):
        return self.dice_rows


parser = argparse.ArgumentParser()
parser.add_argument(
    '-n',
    '--numdice',
    type=int,
    default=3,
    help='How many dice rows you want to roll. Defaults to 3',
)
args = parser.parse_args()
rows = args.numdice
console = Console()


def main():
    clear_lines()
    # create the word list database if it does not exist
    if not Path.exists(Path('wordlist.db')):
        conn = sqlite3.connect(DB)
        dice_db.create_wordlist_db(conn)

    # build the options menu
    options = Table(show_header=False, box=box.ROUNDED, min_width=39)
    options.add_row('', '[bold]r[/bold]: reroll all dice')
    options.add_row('→', '[bold]r[blue]n[/blue][/bold]: reroll just row [blue][bold]n')
    options.add_row('', '[bold]q[/bold]: quit')

    # show the first roll of dice
    dice_numbers = make_dice_nums(rows, DICE_NUMBER)
    dice_rows = DiceRows(dice_numbers)
    console.print(get_dice_and_words(dice_numbers))

    while True:
        # show options menu and input line
        console.print(options)
        try:
            response = input('  → ')
        except (KeyboardInterrupt, EOFError):
            sys.exit('Goodbye!')

        match response.lower():
            # only allow an `r` followed by a valid row number
            case str() as s if s.startswith('r') and ''.join(s[1:]).isnumeric():
                num_part = int(''.join(s[1:]))
                if 1 <= num_part <= len(dice_numbers):
                    clear_lines()
                    dice_rows.randomize_one(num_part - 1)
                    console.print(get_dice_and_words(dice_numbers))
                else:
                    clear_lines()
                    console.print(get_dice_and_words(dice_numbers))
            # reroll all the dice in all rows
            case 'r':
                clear_lines()
                dice_numbers = make_dice_nums(rows, DICE_NUMBER)
                dice_rows = DiceRows(dice_numbers)
                console.print(get_dice_and_words(dice_numbers))
            case 'q':
                print('Goodbye!')
                sys.exit()
            # don't change any of the dice or words
            case _:
                clear_lines()
                console.print(get_dice_and_words(dice_numbers))


def make_dice_nums(row_count: int, dice_per_row: int) -> List[List[int]]:
    """Returns random dice numbers, as a 2D list, with `row_count` rows, and
    `dice_per_row` columns.

    Args:
        row_count: How many rows of dice numbers to return.
        dice_per_row: How many dice are in a single row.

    Returns:
        Dice numbers, inside a 2D list of lists.
    """
    dice_numbers = []
    for _ in range(row_count):
        dice_row = []
        for _ in range(dice_per_row):
            dice_row.append(random.randint(1, DICE_FACES))
        dice_numbers.append(dice_row)
    return dice_numbers


def append_dice_words(dice_nums: List[List[Union[int, str]]]):
    """Appends, to each row of numbers, a word from the word list that corresponds to dice numbers in that row.

    Args:
        dice_nums: The list containing rows of numbers, whose words will be determined.

    Returns:
        The a new list that has words from the word list appended to each row of the original list of numbers.
    """
    nums_with_words = copy.deepcopy(dice_nums)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    with conn:
        for i, dice_row in enumerate(nums_with_words):
            # turn the list of ins into a single int
            single_number = int(''.join([str(x) for x in dice_row]))

            # find the corresponding word list word and append it to the dice row
            word = dice_db.get_word(conn, single_number)
            nums_with_words[i].append(word)
    return nums_with_words


def get_dice_and_words(dice_rows: List[List[int]]):
    """Renders and returns a grid of boxes that contain all dice rows,
    and the word that the dice in that row correspond to.

    Args:
        dice_rows: A 2D list of lists, that contains the dice numbers to be rendered.

    Returns:
        A grid of boxes that contain all dice rows, and the word that the dice in that row correspond to.
    """
    conn = sqlite3.connect(DB)
    grid = Table.grid(collapse_padding=True, padding=0)

    for row in dice_rows:
        dice_nums_combined = []
        die_faces = []
        for die in row:
            dice_nums_combined.append(str(die))
            die_face = Table(show_header=False, box=box.ROUNDED)
            die_face.add_row(str(die))
            die_faces.append(die_face)

        # fetch the word that corresponds to this number, and add it to the row
        combined_num = int(''.join(dice_nums_combined))
        word_face = Table(show_header=False, box=box.ROUNDED, min_width=14)
        word = dice_db.get_word(conn, combined_num)
        word_face.add_row(word)
        die_faces.append(word_face)
        grid.add_row(*die_faces)
    return grid


def clear_lines() -> None:
    """Refreshes the terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
