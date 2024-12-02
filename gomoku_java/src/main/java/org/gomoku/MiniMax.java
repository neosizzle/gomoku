package org.gomoku;

import java.util.List;

public class Minimax {

    static int alpha = (int) Double.NEGATIVE_INFINITY;
    static int beta = (int) Double.POSITIVE_INFINITY;

    public static int minimaxEval(
            List<List<GameOuterClass.GameState>> moveTree,
            GameOuterClass.GameState currState,
            int boardSize,
            boolean isMax,
            int maxPiece,
            int currDepth,
            int alpha,
            int beta
    ) {
        int ourPiece = maxPiece;  // maxPiece is our piece
        int enemyPiece = (ourPiece == 1) ? 2 : 1;

        int ourCaptures = (int) ((maxPiece == 1) ? currState.getP1Captures() : currState.getP2Captures());
        int enemyCaptures = (int) ((maxPiece == 1) ? currState.getP2Captures() : currState.getP1Captures());

        // Check if the current state exists in the move tree
        int stateNodeIndex = -1;
        for (int i = 0; i < moveTree.size(); i++) {
            List<GameOuterClass.GameState> node = moveTree.get(i);
            if (node.get(1) == null) continue;
            if (node.get(0).getBoard().equals(currState.getBoard())) {
                stateNodeIndex = i;
                break;
            }
        }

        // If no valid state found, perform static evaluation
        if (stateNodeIndex == -1) {
            return StaticEvaluation.staticEval(boardSize, currState, ourPiece, enemyPiece, ourCaptures, enemyCaptures);
        }

        // Initialize ideal_score based on whether we're maximizing or minimizing
        GameOuterClass.GameState moveTreeNode = moveTree.get(stateNodeIndex).get(0);
        GameOuterClass.GameState moveTreeChildren = moveTree.get(stateNodeIndex).get(1);

        int idealScore;
        GameOuterClass.GameState selectedState = null;

        if (isMax) {
            idealScore = Integer.MIN_VALUE;
            for (GameOuterClass.GameState childState : moveTreeChildren) {
                int childScore = minimaxEval(moveTree, childState, boardSize, false, maxPiece, currDepth + 1, alpha, beta);
                if (childScore > idealScore) {
                    selectedState = childState;
                }
                idealScore = Math.max(idealScore, childScore);
                alpha = Math.max(alpha, idealScore);
                if (beta <= alpha) {
                    break;
                }
            }
        } else {
            idealScore = Integer.MAX_VALUE;
            for (GameOuterClass.GameState childState : moveTreeChildren) {
                int childScore = minimaxEval(moveTree, childState, boardSize, true, maxPiece, currDepth + 1, alpha, beta);
                if (childScore < idealScore) {
                    selectedState = childState;
                }
                idealScore = Math.min(idealScore, childScore);
                beta = Math.min(beta, idealScore);
                if (beta <= alpha) {
                    break;
                }
            }
        }

        return idealScore;  // Return ideal score of the current state
    }

    // Basic minimax function to select the best move from the current state
    public static GameOuterClass.GameState basicMinimax(GameOuterClass.GameState state, int boardSize, int currPiece, int maxPiece) {
        int depth = (state.getNumTurns() > 4) ? 3 : 2;
        // Generate move tree (you'll need a function for move generation in Java)
        List<List<GameOuterClass.GameState>> moveTree = MoveGeneration.generateMoveTree(state, boardSize, currPiece, depth);
        GameOuterClass.GameState rootNode = moveTree.get(0).get(0);
        List<GameOuterClass.GameState> rootChildren = moveTree.get(0).get(1);

        int maxScore = Integer.MIN_VALUE;
        int maxScoreIdx = -1;

        // Iterate through root's children and evaluate them
        for (int i = 0; i < rootChildren.size(); i++) {
            GameOuterClass.GameState child = rootChildren.get(i);
            int childScore = minimaxEval(moveTree, child, boardSize, currPiece != maxPiece, maxPiece, 0, Integer.MIN_VALUE, Integer.MAX_VALUE);
            if (childScore > maxScore) {
                maxScore = childScore;
                maxScoreIdx = i;
            }
        }

        return rootChildren.get(maxScoreIdx);  // Return the best move (child state)
    }

    // You can use this as a helper to time your minimax method
    public static void measureDuration(Runnable task) {
        long startTime = System.nanoTime();
        task.run();
        long endTime = System.nanoTime();
        System.out.println("Execution time: " + (endTime - startTime) + " ns");
    }
}
