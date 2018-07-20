"""
This is evaluates the amount of each number on the start board.
"""

board_name = ["easy", "hard"]


for board in board_name:
    with open('C:/Users/angel/OneDrive/Documents/Python/Tkinter/Sudoku/%s.Sudoku' % board, 'r') as boards_file:
        print(board, ":")
      
        overall = 0
        
        for i in range(1,10):
            total = 0
            boards_file.seek(0)
            
            for line in boards_file:
                line = line.strip()
             
                for n in line:
                    if eval(n) == i:
                        total += 1
                        overall += 1

            print(i, ":", total)
        print("overall:", overall)
    
