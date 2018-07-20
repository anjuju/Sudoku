import argparse
from tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

# define global variables

BOARDS = ['debug', 'easy', 'hard', 'error'] #available sudoku boards
MARGIN = 20     # pixels around the board
SIDE = 50       # width of board cell

WIDTH = HEIGHT = MARGIN*2 + SIDE*9

class SudokuError(Exception):
    """
    An application specific error
    """
    pass

def parse_arguments():
    """
    Parses arguments of the form:
        sudoku.py <board name>
    Where `board name` must be in the `BOARDS` list
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--board",
                            help = "Desired board name",
                            type = str,
                            choices = BOARDS,
                            required=True)
    
    # creates dictionary of keys = argument flag (board) and value = argument (user input)
    args = arg_parser.parse_args()
    return args.board  # returns board name user passed in (debug, easy, hard, error)

class SudokuUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """

    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)

        self.row, self.col = 0, 0

        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku - %s" % board_name)
        self.pack(fill=BOTH, expand=1) # Frame attribute - fills entire space
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)

        clear_button = Button(self, text="Clear Answers", command = self.__clear_answers, font=('Arial', 14, 'bold'))
        clear_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        # event binding  <Button-1> - mouse click (built in names)
        self.canvas.bind("<Button-1>", self.__cell_clicked) # pass x & y location of cursor
        self.canvas.bind("<Key>", self.__key_pressed) # binds key user pressed

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"
            strength = 3 if i % 3 == 0 else 1
        # vertical lines
            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=strength)
        # horizontal lines 
            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color, width=strength)

    def __draw_puzzle(self):    
        self.canvas.delete("numbers")   # clears out previous numbers
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]     # actually redrawing puzzle every time user inputs number (updates info in puzzle)
                if answer != 0: # 0 is blank space
                    x = MARGIN + j * SIDE + SIDE / 2        # creates "cells"
                    y = MARGIN + i * SIDE + SIDE / 2
                    original = self.game.start_puzzle[i][j]  # want to compare to "blank" puzzle
                    color = "black" if answer == original else "sea green" # green for user-filled answers
                    self.canvas.create_text(
                        x, y, text=answer, tags="numbers", fill=color, font=('Arial', 16, 'bold')
                        )

    def __clear_answers(self):
        self.game.start()       # resets puzzle to original state
        self.canvas.delete("victory")
        self.canvas.delete("winner")
        self.__draw_puzzle()

    def __cell_clicked(self, event): # always takes event parameter, always called when user clicks mouse
        if self.game.game_over:
            return

        x, y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN): # on the game board
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE     # row and col are local var in __cell_clicked
            
            # if cell was selected already - deselect it
            #if (row, col) == (self.row, self.col):
             #   self.row, self.col = -1, -1
            if self.game.puzzle[row][col] ==0 or self.game.puzzle[row][col] != self.game.start_puzzle[row][col]:   # can only click on "blank spaces"
                self.row, self.col = row, col
    

        self.__draw_cursor()

    def __draw_cursor(self): 
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:         # put in focus
            x0 = MARGIN + self.col * SIDE + 1       # calculates dimensions of cell
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="aquamarine", tags="cursor")       # draw rectangle around focused cell

    def __draw_error(self):
        if self.row >= 0 and self.col >= 0:         # put in focus
            x0 = MARGIN + self.col * SIDE + 1       # calculates dimensions of cell
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red", width=3, tags="error")       # draw rectangle around focused cell

    def __key_pressed(self, event):
        if self.game.game_over:
            return
        if self.row >= 0 and self.col >= 0 and event.char in "1234567890":
            # if pressed key from keyboard, returns char codes/ordinal values, not straight integers
            # compares ord("0") to that of character pressed
            self.game.puzzle[self.row][self.col] = int(event.char)  # assigns user-inputted number to puzzle
            if self.check_error(int(event.char)):
                self.__draw_puzzle()
                self.__draw_error()
            else:
                self.col, self.row = -1, -1
                self.__draw_puzzle()        # redrawing puzzle with updated number
                self.__draw_cursor()        # deletes blue outline of cursor
                if self.game.check_win():
                    self.__draw_victory()

    def check_error(self, num):
        if num != 0:
            if self.game.puzzle[self.row].count(num) > 1:    # looks at each number in that specific row
                return True
            if [self.game.puzzle[row][self.col] for row in range(9)].count(num) > 1:  # looks at each column
                return True
            for i in [0,3,6]:
                if self.row in range(i,i+3):
                    rr = range(i,i+3)
                if self.col in range(i,i+3):
                    cc = range(i,i+3)
            if [
                    self.game.puzzle[r][c]
                    for r in rr
                    for c in cc
                    ].count(num) > 1:
                return True
        self.canvas.delete("error")
        return False

    def __draw_victory(self):
        # create an oval
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange")
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE / 2
        self.canvas.create_text(
            x, y,
            text="You win!", tags="winner",
            fill="white", font=("Arial", 32))

class SudokuBoard(object):
    """
    Sudoku Board representation
    """
    
    def __init__(self, board_file):
        self.board = self.__create_board(board_file) # parsing out the board_file by making a matrix

    def __create_board(self, board_file): # private function
        # Summary: iterates over each line and integer in file
        # and create matrix representing the Sudoku board

        # create an initial matrix, or a list of a list
        board = []

        # iterate over each line
        for line in board_file:
            line = line.strip() # remove leading and trailng whitespace
            
            if len(line) != 9:  # error if len of line != 9
                board = []
                raise SudokuError("Each line in the sudoku puzzle must be 9 chars long")

            # create a list for that line
            board.append([])

            for c in line:  
                if not c.isdigit():
                    raise SudokuError("Valid characters for a sudoku puzzle must be in 0-9")

                board[-1].append(int(c))  #add latest list for the line
                
        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")

        # Return the constructed board
        return board      

class SudokuGame(object): # maintains state of the game and board
    """
    A Sudoku game, in charge of storing the state of the board and checking
    whether the puzzle is completed.
    """
    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])
                # this is just the board from the board_file
                # created a copy to be able to clear the board when user wants to start over
                # and be able to check the inputted answers against start board
                # preserves start puzzle

    def check_win(self):
        for row in range(9):
            if not self.__check_row(row):
                return False
        for column in range(9):
            if not self.__check_column(column):
                return False
        for row in range(3):
            for column in range(3):
                if not self.__check_square(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))  # not indexable nor ordered - because sudoku is unordered
                                                # returns True or False

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row]) # takes each row, makes it a set and compares to set(1-9)

    def __check_column(self, column):
        return self.__check_block([self.puzzle[row][column] for row in range(9)]) # makes list of each entry in a "column"

    def __check_square(self, row, column):
        return self.__check_block(
            [
                self.puzzle[r][c]
                for r in range(row*3, (row+1)*3)
                for c in range(column*3, (column+1)*3)
                ]
            )


if __name__ == '__main__':
    board_name = parse_arguments()

    with open('C:/Users/angel/OneDrive/Documents/Python/Tkinter/Sudoku/%s.Sudoku' % board_name, 'r') as boards_file:
        game = SudokuGame(boards_file)  # instantiating new game
        game.start()

        root = Tk()             # parent widget
        SudokuUI(root, game)
        root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
        root.mainloop()
