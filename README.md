# Crossword-puzzle
AI to generate crossword puzzles
## Background
The process of generating a crossword puzzle can be approached as a constraint satisfaction problem. In this approach, we model the puzzle's structure and constraints, then seek a solution that satisfies those constraints. Here's a breakdown of the process:
#### Define Variables: 
Each sequence of squares in the crossword grid represents a variable. These variables are defined by their starting position (row and column), direction (across or down), and length.

#### Define Unary Constraints:
The length of each word imposes unary constraints. Each word must match the specified length of its corresponding variable.

#### Define Binary Constraints: 
Binary constraints arise from the overlaps between neighboring variables. These overlaps indicate common squares where characters in different words must match. Each pair of neighboring variables defines an overlap, represented by the indices of characters that must match.

#### Additional Constraints:
To ensure diversity in the puzzle, additional constraints require that all words must be different.

#### Solve the Constraint Satisfaction Problem:
We employ algorithms like AC3 for constraint propagation and backtracking search to find a satisfying assignment where each variable is assigned a different word from a given vocabulary list. The assignment must adhere to all unary and binary constraints.

#### Generate the Puzzle:
Once a satisfying assignment is found, it represents a valid crossword puzzle solution.

## Specification
For more information about the project specifications, please refer to the [Harvard CS50AI](https://cs50.harvard.edu/ai/) website.
Please avoid directly copying the source code as it is provided for reference purposes only.
