import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:

            #get the length of the variable
            length = var.length

            #filter out values in the domain that do not match the length constraint 
            inconsistent_values = [word for word in self.domains[var] if len(word) != length]
            for word in inconsistent_values:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        
        #flag to track if any revision was made
        revised = False
       
       #get the overlap between variables x and y
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return revised #no overlap between variables
        
        #get the indices of the overlapping positions in both variables
        i, j = overlap

        #iterate over each value in the domain of variable x
        for val_x in self.domains[x].copy():
            #Check if there is a value in the domain of variable y that satisfies the constraint
            if any(val_x[i] == val_y[j] for val_y in self.domains[y]):
                continue  # No conflict, move to the next value in domain of x
            else:
                self.domains[x].remove(val_x)  # Remove conflicting value from domain of x
                revised = True  # Set flag to indicate a revision was made
        
        return revised  # Return True if a revision was made, False otherwise
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            queue = []
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    if self.crossword.overlaps[var1, var2] is not None:
                        queue.append((var1, var2))

        while len(queue) > 0:
            x, y = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                   return False
            for neighbour in self.crossword.neighbors(x):
                if neighbour != y:
                    queue.append((neighbour, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in assignment.keys():
            if assignment[variable] is None:
                return False
        return True    

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        assigned_words = set()
        assigned_position = set()

        for variable,word in assignment.items():
            if len(word) != variable.length:
                return False
            if  word in assigned_position:
                return False
            assigned_words.add(word)
        
        #check for conflicts with neighboring variable
        for variable in assignment:
            for neighbour in self.crossword.neighbors(variable):
                if neighbour in assignment:
                    i, j = self.crossword.overlaps[variable, neighbour]
                    if assignment[variable][i] != assignment[neighbour][j]:
                        return False
                    
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        word_dict ={}

        #get the neighbors of var
        neighbors = self.crossword.neighbors(var)
        
        #iterate over the word in the domain of var
        for word in self.domains[var]:
            eliminated = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                i, j = self.crossword.overlaps[var,neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word[i] != neighbor_word[j]:
                        eliminated += 1
                word_dict[word] = eliminated
        
        # Sort word_dict based on the count of eliminated words
        sorted_dict = sorted(word_dict.items(), key=lambda item:item[1])                
        
        # Return list of words sorted by the count of eliminated words
        return [word for word, _ in sorted_dict]
    

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # get unassigned variable
        unassigned_vars = [var for var in self.crossword.variables if var not in assignment]
        
        # Sort unassigned variables by the number of remaining values in their domain
        unassigned_vars.sort(key=lambda var:(len(self.domains[var]), -len(self.crossword.neighbors(var))))

        #return the first variable from the sorted list
        return unassigned_vars[0] if unassigned_vars else None
    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
         #check if assignment is complete
        if len(assignment) == len(self.crossword.variables):
            return assignment
        
        #select an assigned variable
        unassigned = self.select_unassigned_variable(assignment)
        
        for value in self.domains[unassigned]:
            # making assignment copy, with updated variable value
            assignment_copy = assignment.copy()
            assignment_copy[unassigned] = value
            # checking for consistency, getting result of that new assignment backtrack
            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)
                if result is not None:
                    return result
        return None
def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
