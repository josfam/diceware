# diceware
Generate secure passphrases by rolling dice on the terminal, using the [EFF](https://www.eff.org/)'s [word list.](https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt).


## Inspiration for the project

Inspiration for this project came from hearing about diceware, which is a way to generate
\
secure passphrases by rolling dice.
\
\
The concept materialized for me when I used [this website—d20key](https://d20key.com/#/), created
\
by [Carey Parker—of Firewalls Don't Stop Dragons fame](https://firewallsdontstopdragons.com/podcast/)—et al, to get familiar with dice  ware in general.
\
\
Matter of fact, this project tries to mimic—as closely as possible—the d20key site's functionality,
\
albeit using 5-sided dice.
\
\
In my day-to-day, I do use a password manager to create these passphrases for me,
\
but the diceware method is a good way to get passphrases if one does not have a password manager.
## How to run the program
### 1. Clone this repository
Run 
```
git clone https://github.com/josfam/diceware.git
```
in your terminal window to get the files.
### 2. Install poetry on your computer
> #### On linux/Mac (or WSL for Windows):
- Run [the installation script found under the "Linux, macOS, Windows (WSL)" section on the Poetry site](https://python-poetry.org/docs/#installing-with-the-official-installer)
> #### On a Windows computer (Powershell):
- Run [the installation script found under the "Windows (Powershell)" section on the Poetry site](https://python-poetry.org/docs/#installing-with-the-official-installer)
### 3. Navigate to the project folder
Make sure to open the project folder from your terminal.
### 4. Activate the poetry virtual environment
Run:
```
poetry shell
```
to enter into the poetry virtual environment:
### 5. Install project dependencies
Run:
```
poetry install
```
to install the dependencies necessary for the program
### 6. Run the program
> #### On linux/Mac (or WSL for Windows):
```
python3 app.py
```
> #### On Windows:
```
python app.py
```
