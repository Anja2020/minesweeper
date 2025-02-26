import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.cells == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        empty = []
        copy_knowledge = self.knowledge.copy()
        for sentence in copy_knowledge:
            sentence.mark_mine(cell)
            if len(sentence.cells) == 0:
                empty.append(sentence)
        for sentence in empty:
            self.knowledge.remove(sentence)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        empty = []
        copy_knowledge = self.knowledge.copy()
        for sentence in copy_knowledge:
            sentence.mark_safe(cell)
            if len(sentence.cells) == 0:
                empty.append(sentence)
        for sentence in empty:
            self.knowledge.remove(sentence)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # find out neighbors
        i, j = cell
        neighbor_cells = set()
        for row in range(i - 1, i + 2):
            for col in range(j - 1, j + 2):
                if 0 <= row < self.height and 0 <= col < self.width and (row, col) != cell:
                    neighbor_cells.add((row, col))

        # remove already clicked cells from neigbors
        cells = set()
        for neighbor in neighbor_cells:
            if neighbor not in (self.moves_made or self.mines or self.safes):
                cells.add(neighbor)
            elif neighbor in self.mines:
                count -= 1

        # check if all neighbors are safe
        if count == 0:
            for neighbor in cells:
                self.safes.add(neighbor)
                self.mark_safe(neighbor)
        # check if all neighbors are mines
        elif len(cells) == count:
            for neighbor in cells:
                self.mines.add(neighbor)
                self.mark_mine(neighbor)
        
        # add new sentence to knowledge
        new_sentence = Sentence(cells, count)
        self.knowledge.append(new_sentence)

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        self.mark_mines_safes()

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        self.draw_interferences()
        


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_cells = self.safes.difference(self.moves_made)
        if not safe_cells:
            return None
        else:
            return safe_cells.pop()

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        cells = []
        for row in range(0, self.height):
            for col in range(0, self.width):
                cell = (row, col)
                if cell not in self.moves_made and cell not in self.mines:
                    cells.append(cell)
        if cells:
            return random.choice(cells)
        else:
            return None

    def mark_mines_safes(self):
        copy_knowledge = self.knowledge.copy()
        for sentence in copy_knowledge:
            # all cells of the sentence are mines
            if len(sentence.cells) == sentence.count:
                copy_cells = sentence.cells.copy()
                for cell in copy_cells:
                    self.mark_mine(cell)
            # all cells of the sentence are safe
            elif sentence.count == 0:
                copy_cells = sentence.cells.copy()
                for cell in copy_cells:
                    self.mark_safe(cell)


    def draw_interferences(self):
        drawn = True
        
        while drawn:
            # comparing each sentence with each other in the knowledge base
            copy_knowledge = self.knowledge.copy()
            
            drawn = False
            for sentence1 in copy_knowledge:
                for sentence2 in copy_knowledge:
                    # check if sentences are disjunct and cells of sentence1 is subset of cells of sentence2
                    if sentence1 != sentence2 and len(sentence1.cells) != 0 and len(sentence2.cells) != 0:
                        if sentence1.cells.issubset(sentence2.cells):
                            sentence2.cells = sentence2.cells.difference(sentence1.cells)
                            sentence2.count = sentence2.count - sentence1.count
                            drawn = True
            
            self.mark_mines_safes()
