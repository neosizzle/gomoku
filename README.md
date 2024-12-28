# /dev/log for gomoku
A game AI that specializes in playing the game gomoku Ninuki-renju / Pente variants using minimax algorithm and heuristics. Comes with a game client. Special thanks to [Hans Wong](https://github.com/HansWongDH) for collabortating on this project

## Requirements
Python 3 and Java 17

## Instructions
1. `make backend` to run the move suggestion server
2. `make frontend` to run the static UI server
3. Go to `localhost:5000` on your browser to play the game

## Demo
![gomoku-demo](https://hackmd.io/_uploads/rkwq_R2Byl.gif)


## Game rules
- Two players take turns placing stones of their color (white or black, black moves first )on an intersection of the board, and the game ends when one player manages to align five stones. An alignment of 5 or more can win.
- The board is a 19x19 Goban, without limit to the number of stones.
- Capture (As in the Ninuki-renju or Pente variants) : You can remove a pair of your opponent’s stones from the board by flanking them with your own stones. This rule adds a win condition : If you manage to capture ten of your opponent’s stones, you win the game.
- A player who manages to line up five stones wins only if the opponent cannot break this line by capturing a pair.
- No double-threes : It is forbidden to play a move that introduces two free-three alignments, which would guarantee a win by alignment

## Design
This system will be isolated into a frontend(game) and the backend(algo server) The frontend will be using python Flask framework and the backend will be written in python to carry out the initial algorithm POC. It will be moved to java for the final release since performance optimization is a requirement in the release. the communication medium will be using [GRPC](grpc.io) due to its support for cross-compatibility and simplicity

The system flow will be as follows

![image](https://hackmd.io/_uploads/HkQtH9Jykl.png)

The schema will be designed as follows

![image](https://hackmd.io/_uploads/H1QeU51k1g.png)


## Installation and execution of examples
`bash install-deps.sh`

## Static evaluation 
one of the components needed for the minimax algorithm is the static evaluation function. This function checkes the cuerent board state snd determines a score. The score will indicate how likely a player is going to win.

The score will be judged based on multiple criteria which correlates to the winning condition: **captures** and **consecutive pieces**. To evaluate the capture score, it is quite direct, We can scale the players current capture with a arbitrary multiplier and deduct it from the opponents players captures.

Consecutive pieces however require us to analyze the board and estimate the likelihood of a player's chances of getting 5 consecutive pieces.

Initially we thought of using a flood fill approach where we would scan the pieces as clusters. The depth of a cluster would increase as they go out and if the depth reaches a maximum level then we can conclude that the game has ended and we have a winner. This is paired with a scoring matrix that keeps track of each cell's individual scores which will be summed at the end.

![image](https://hackmd.io/_uploads/rJYa5fPl1e.png)

The issue with the above approach Is that when we have a linear combination with a gap in between however the combination is valid if the gap is filled, We would yield different scores compared to a combination without any gaps
![image](https://hackmd.io/_uploads/S1iF6GDekx.png)

![image](https://hackmd.io/_uploads/r1djpMvx1e.png)

To resolve this, we analyze the board directionally, from all directions to found the number of consecutive pieces for each row , column and diagonal, and evaluate them based on the gap size between each piece and the gap piece (empty or enemy), which gives us a more intuitive score.

![image](https://hackmd.io/_uploads/HkHyMXvgkg.png)

## Move generation
This would be the process of generating possible moves of an arbitrary amount of turns for both players. The naive approach would be to alternatively fill in the blank cells alternating between the first and the second player; however this can be only done up to 2 turns.

Which generates 120410 moves for this example of a 19x19 board
![image](https://hackmd.io/_uploads/SJMjr4weye.png)

However, we are not able to go up to 3 turns due to memory constraints. 

## Heuristic 1 (optimal moves are made around existing pieces in the board)
Since we want to maximize the minimum advantages, it makes sense to play defensively around existing pieces rather than attacking from empty spaces out of no where. Hence, we only will generate moves that are a 2 cell radius from other pieces, which brings us down to 6849 moves for 2 turns and 609959 moves for 3 turns.

![image](https://hackmd.io/_uploads/SyC5LEwxkx.png)

## Heuristic 2 (Threat search space)
The original search space of the algorithm is to branch out for every possible cell around any piece. While this explores the most exaustive options, performace is still an issue and we cant go more than 3 level depth. 

[This](https://www.researchgate.net/publication/2252447_Go-Moku_and_Threat-Space_Search) is a study by L.V.Allis
on using another search space method for gomoku; and it focuses on only branching out when a threat is formed or blocked.

A threat can be defined as an arrangement of pieces in particular sequences; called threat sequences. The threat sequences are self defined such as the free three, free four, closed three, closed four etc.


![image](https://hackmd.io/_uploads/SykK3-TNJx.png)
> Some threat sequences from the study

Note that the default exaustive search will be used if no threats are found in the current board state.

Once the threat search space is implemented, and we managed to trim down the entire move tree from 40k nodes to 2k nodes on depth 3, and for depth 4 the nodes is not more than 30k for the board configuration below 

![image](https://hackmd.io/_uploads/SkebpW6VJg.png)

## OS optimizations

1. We used a thread pool to run the root node evaluations concurrently, utilizing CPU resources better for scenarios with more root children
![image](https://hackmd.io/_uploads/rJH0KRhBye.png)
> Left is multi threaded, right is single threaded

2. Since we have a multithreaded application now, we apply CPU pinning to those worker threads so they wont be interrupted by other tasks in the same core
```
Function minimax evals took 119 milliseconds
Function minimax evals took 2 milliseconds
Function minimax evals took 62 milliseconds
Function minimax evals took 246 milliseconds
Function minimax evals took 174 milliseconds
Function minimax evals took 261 milliseconds
Function minimax evals took 104 milliseconds
Function minimax evals took 234 milliseconds
Function minimax evals took 249 milliseconds
Function minimax evals took 185 milliseconds
Function minimax evals took 147 milliseconds
Function minimax evals took 142 milliseconds
Function minimax evals took 189 milliseconds
Function minimax evals took 247 milliseconds
Function minimax evals took 876 milliseconds
Function minimax evals took 478 milliseconds
Function minimax evals took 336 milliseconds
Function minimax evals took 459 milliseconds
Function minimax evals took 900 milliseconds
Function minimax evals took 2 seconds
Function minimax evals took 4 milliseconds
```
> Before CPU pinning

![image](https://hackmd.io/_uploads/H1bsc0hr1e.png)
> After CPU pinning for the same moveset

## Suggested improvements
- Historical heuristic
- Opening book
- Countermove heuristic
- State retainment
- JVM tuning
