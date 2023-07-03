import argparse
import copy
import random
from pathlib import Path
import sqlite3
import sys
import os

from rich import box
from rich.console import Console
from rich.table import Table
from typing import List, Union

import dice_db

DICE_NUMBER = 5  # You need this many dice to get a word from the word list
DICE_FACES = 6
DB = 'wordlist.db'
MIN_ROWS = 3  # One cannot have less than MIN_ROWS rows on display

parser = argparse.ArgumentParser()
parser.add_argument(
    '-n',
    '--numdice',
    type=int,
    default=5,
    help='How many dice rows you want to roll. Defaults to 5',
)
args = parser.parse_args()
rows = args.numdice
console = Console()


class Notifications:
    """Handles the posting of notification messages to the User Interface"""

    def __init__(self, msg=''):
        self.message = msg
        self.has_message = False

    def clear(self):
        """Removes any stored messages."""
        self.message = ''
        self.has_message = False

    def message_exists(self):
        """Returns True if there is a message to post. Returns False otherwise"""
        return not self.message == ''


class DiceRows:
    """A container for holding and manipulating the list of numbers representing
    dice faces.
    """

    def __init__(self, dice_per_row: int = DICE_NUMBER):
        self.dice_rows = self.make_dice_nums(rows, dice_per_row)

    def make_dice_nums(self, row_count: int, dice_per_row: int) -> List[List[int]]:
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

    def randomize_one(self, row: int) -> None:
        """Changes, in place, the numbers of the specified row.

        Args:
            row: The row of the list, containing the numbers to change.
        """
        self.dice_rows[row] = [random.randint(1, DICE_FACES) for _ in range(DICE_NUMBER)]

    def randomize_all(self) -> None:
        """Changes, in place, all the numbers of all the rows in the list."""
        for index, row in enumerate(self.dice_rows):
            self.randomize_one(index)

    def get_all_rows(self) -> List[List[int]]:
        """Returns the list containing all numbers"""
        return self.dice_rows

    def add_row(self) -> None:
        """Adds one more row of numbers to the current list of numbers."""
        self.dice_rows.append([random.randint(1, DICE_FACES) for _ in range(DICE_NUMBER)])

    def remove_row(self) -> None:
        """Removes the last row of numbers from the current list of numbers."""
        if len(self.dice_rows) > MIN_ROWS:
            self.dice_rows.pop()


def main():
    clear_lines()
    # create the word list database if it does not exist
    if not Path.exists(Path('wordlist.db')):
        conn = sqlite3.connect(DB)
        dice_db.create_wordlist_db(conn)

    notifs = Notifications()

    # show the first roll of dice
    dice_rows = DiceRows()
    dice_and_words = append_dice_words(dice_rows.get_all_rows())
    console.print(build_grid(dice_and_words))

    while True:
        # show options menu, any notifications, and input prompt
        console.print(get_options())
        if notifs.message_exists():
            console.print(notifs.message)
            notifs.clear()
        try:
            response = input('Enter an option (q to quit) → ')
        except (KeyboardInterrupt, EOFError):
            sys.exit('Goodbye!')

        clear_lines()
        match response.lower():
            # only allow an `r` followed by a valid row number
            case str() as s if s.startswith('r') and ''.join(s[1:]).isnumeric():
                num_part = int(''.join(s[1:]))
                if 1 <= num_part <= len(dice_rows.get_all_rows()):
                    dice_rows.randomize_one(num_part - 1)
                    dice_and_words = append_dice_words(dice_rows.get_all_rows())
            # reroll all the dice in all rows
            case 'r':
                dice_rows.randomize_all()
                dice_and_words = append_dice_words(dice_rows.get_all_rows())
            # add one more row of dice to the current rows
            case '+':
                dice_rows.add_row()
                dice_and_words = append_dice_words(dice_rows.get_all_rows())
            # remove the last row of dice from the current rows
            case '-':
                if len(dice_rows.get_all_rows()) == MIN_ROWS:
                    notifs.message = f"\n[red]Can't remove any further. {MIN_ROWS} rows is the minimum.\n"
                dice_rows.remove_row()
                dice_and_words = append_dice_words(dice_rows.get_all_rows())
            case 'p':
                console.print(build_grid(dice_and_words))
                words = ' '.join([x[-1] for x in dice_and_words])
                notifs.message = f'\n[bold][deep_sky_blue3]{words}\n'
                continue
            case 'q':
                print('Goodbye!')
                sys.exit()
        # show the current row state
        console.print(build_grid(dice_and_words))


def get_options():
    """Returns the options available to the user"""
    option_descriptions = {
        'r': 'reroll all dice',
        'rn': 'reroll only the nth row',
        'p': 'print words',
        '+/-': 'add or remove one row',
        'q': 'quit'
    }
    options = Table(show_header=False, box=box.ROUNDED, min_width=39)
    
    for option, desc in option_descriptions.items():
         options.add_row('[bold]{:>3}[/bold]: {}'.format(option, desc))
    return options


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


def build_grid(dice_and_words: List[List[Union[int, str]]]):
    """Renders and returns a grid of boxes that contain all dice rows,
    and the word that the dice in that row correspond to.

    Args:
        dice_rows: A 2D list of lists, that contains the dice numbers to be rendered.

    Returns:
        A grid of boxes that contain all dice rows, and the word that the dice in that row correspond to.
    """
    grid = Table.grid(collapse_padding=True, padding=0)

    for row_num, row in enumerate(dice_and_words):
        boxed_items = []
        for item in row:
            if isinstance(item, str):
                color_start = '[bold][deep_sky_blue3]'
                color_stop = '[/bold][/deep_sky_blue3]'
                boxed_item = Table(show_header=False, box=box.ROUNDED, min_width=14)
            else:
                color_start = ''
                color_stop = ''
                boxed_item = Table(show_header=False, box=box.ROUNDED)
            boxed_item.add_row(f'{color_start}{str(item)}{color_stop}')
            boxed_items.append(boxed_item)

        # fit the row label into its own border-less grid element
        row_label = Table.grid()
        row_label.add_column(justify='right', min_width=2)
        row_label.add_row('')
        row_label.add_row(f'[plum4]{str(row_num + 1)}')
        row_label.add_row('')
        boxed_items.append(row_label)

        grid.add_row(*boxed_items)

    return grid


def clear_lines() -> None:
    """Refreshes the terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
