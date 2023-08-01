"""Generates a passphrase as a result of rolling 5, 6-sided dice."""
import copy
import random
import sqlite3
from typing import List, Union

from rich import box
from rich.table import Table

from . import dice_db

DICE_NUMBER = 5  # You need this many dice to get a word from the word list
DICE_FACES = 6
MIN_ROWS = 3  # One cannot have less than MIN_ROWS rows on display


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

    def __init__(self, rows: int = 5, dice_per_row: int = DICE_NUMBER):
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

    def __len__(self) -> int:
        """Returns the length of the 2D list of numbers"""
        return len(self.dice_rows)


def get_options():
    """Returns the options available to the user"""
    option_descriptions = {
        'r': 'reroll all dice',
        'rn': 'reroll only the nth row',
        'p': 'print words',
        '+/-': 'add or remove one row',
        'q': 'quit',
    }
    options = Table(show_header=False, box=box.ROUNDED, min_width=42)

    for option, desc in option_descriptions.items():
        options.add_row('[bold]{:>3}[/bold]: {}'.format(option, desc))
    return options


def append_dice_words(conn: sqlite3.Connection, dice_nums: List[List[Union[int, str]]]):
    """Appends, to each row of numbers, a word from the word list that corresponds to dice numbers in that row.

    Args:
        conn: The sqlite3 database connection to use for database queries.
        dice_nums: The list containing rows of numbers, whose words will be determined.

    Returns:
        The a new list that has words from the word list appended to each row of the original list of numbers.
    """
    nums_with_words = copy.deepcopy(dice_nums)

    with conn:
        for i, dice_row in enumerate(nums_with_words):
            # turn the list of ins into a single int
            single_number = int(''.join([str(x) for x in dice_row]))

            # find the corresponding word list word and append it to the dice row
            word = dice_db.get_word(conn, single_number)
            nums_with_words[i].append(word)
    return nums_with_words


def redact_contents(dice_and_words: List[List[Union[int, str]]]):
    """Returns a redacted list, which is a result of replacing numbers with `0`s,
    and words with `XXXXX`.
    This redacted list is only used when the user quits the program, as a somewhat pleasant
    UI touch.

    Args:
        dice_and_words: The list of numbers and words to be redacted.
    """
    redacted_list = dice_and_words
    for index, row in enumerate(dice_and_words):
        dice_and_words[index] = [0, 0, 0, 0, 0, 'XXXXX']

    return redacted_list


def build_grid(dice_and_words: List[List[Union[int, str]]], redact_row_labels=False):
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
        if not redact_row_labels:
            row_label.add_row(f'[plum4]{str(row_num + 1)}')
        else:
            row_label.add_row('[plum4]0')
        row_label.add_row('')
        boxed_items.append(row_label)

        grid.add_row(*boxed_items)

    return grid
