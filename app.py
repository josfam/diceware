import argparse
import os
import sqlite3
import sys
from pathlib import Path
from typing import List, Union

from rich.console import Console
from rich.table import Table

import dice_db

from diceware import *

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

from diceware import *


def main():
    clear_lines()
    # create the word list database if it does not exist
    if not Path.exists(Path('wordlist.db')):
        conn = sqlite3.connect(DB)
        dice_db.create_wordlist_db(conn)

    notifs = Notifications()

    # show the first roll of dice
    dice_rows = DiceRows(rows=rows)
    dice_and_words = append_dice_words(dice_rows.get_all_rows())
    console.print(build_grid(dice_and_words))
    options = get_options()

    while True:
        # show options menu, any notifications, and input prompt
        console.print(options)
        if notifs.message_exists():
            console.print(notifs.message)
            notifs.clear()
        try:
            response = input('Enter an option (q to quit) → ')
        except (KeyboardInterrupt, EOFError):
            clear_lines()
            console.print(build_grid(redact_contents(dice_and_words), redact_row_labels=True))
            console.print(options)
            sys.exit('Goodbye!')

        clear_lines()
        match response.lower():
            # only allow an `r` followed by a valid row number
            case str() as s if s.startswith('r') and ''.join(s[1:]).isnumeric():
                num_part = int(''.join(s[1:]))
                if 1 <= num_part <= len(dice_rows.get_all_rows()):
                    dice_rows.randomize_one(num_part - 1)
                    dice_and_words = append_dice_words(dice_rows.get_all_rows())
                else:
                    message = "[red]\nThere is no such row. Please try again\n"
                    notifs.message = message
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
                console.print(build_grid(redact_contents(dice_and_words), redact_row_labels=True))
                console.print(options)
                print('Goodbye!')
                sys.exit()
            # show a notification for an invalid choice
            case _:
                notifs.message = f"\n[red]Invalid choice. Please try again.\n"

        # show the current row state
        console.print(build_grid(dice_and_words))


def clear_lines() -> None:
    """Refreshes the terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    main()
