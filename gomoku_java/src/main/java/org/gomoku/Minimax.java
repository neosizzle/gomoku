package org.gomoku;

import game.GameOuterClass;

import java.util.List;

public class Minimax {
    public static int minimaxEval(
            List<List<Object>> moveTree,
            GameOuterClass.GameState currState,
            int BOARD_SIZE,
            boolean isMax,
            int maxPiece,
            int currDepth,
            int alpha,
            int beta) {

        int ourPiece = maxPiece;  // maxPiece is our piece
        int enemyPiece = (ourPiece == 1) ? 2 : 1;

        int ourCaptures = (int) ((maxPiece == 1) ? currState.getP1Captures() : currState.getP2Captures());
        int enemyCaptures = (int) ((maxPiece == 1) ? currState.getP2Captures() : currState.getP1Captures());

        // Check if the current state exists in the move tree
        int stateNodeIndex = -1;
        for (int i = 0; i < moveTree.size(); i++) {
            List<Object> node = moveTree.get(i);
            if (node.get(1) == null) {
                continue;
            }
            GameOuterClass.GameState nodeState = (GameOuterClass.GameState) node.get(0);
            if (nodeState.getBoard().equals(currState.getBoard()) && ((List<?>) node.get(1)).size() > 0) {
                stateNodeIndex = i;
                break;
            }
        }

        // If no valid state found, perform static evaluation
        if (stateNodeIndex == -1) {
            return StaticEvaluation.staticEval(BOARD_SIZE, currState, ourPiece, enemyPiece, ourCaptures, enemyCaptures);
        }

        // Initialize idealScore based on whether we're maximizing or minimizing
        List<Object> moveTreeNode = moveTree.get(stateNodeIndex);
        List<GameOuterClass.GameState> moveTreeChildren = (List<GameOuterClass.GameState>) moveTreeNode.get(1);

        int idealScore;
        GameOuterClass.GameState selectedState;

        if (isMax) {
            idealScore = Integer.MIN_VALUE;
            for (GameOuterClass.GameState childState : moveTreeChildren) {
                int childScore = minimaxEval(moveTree, childState, BOARD_SIZE, false, maxPiece, currDepth + 1, alpha, beta);
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
                int childScore = minimaxEval(moveTree, childState, BOARD_SIZE, true, maxPiece, currDepth + 1, alpha, beta);
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
        return idealScore;
    }

    // Basic minimax function to select the best move from the current state
    public static GameOuterClass.GameState basicMinimax(GameOuterClass.GameState state, int boardSize, int currPiece, int maxPiece) {
        int depth = (state.getNumTurns() > 4) ? 3 : 2;
        // Generate move tree (you'll need a function for move generation in Java)
        MoveGeneration moveGeneration = new MoveGeneration(boardSize);
        List<List<Object>> moveTree = moveGeneration.generateMoveTree(state, boardSize, (byte) currPiece, depth);
        GameOuterClass.GameState rootNode = (GameOuterClass.GameState) moveTree.get(0).get(0);
        List<GameOuterClass.GameState> rootChildren = (List<GameOuterClass.GameState>) moveTree.get(0).get(1);

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

        if (maxScoreIdx >= 0 && maxScoreIdx < rootChildren.size()) {
            return rootChildren.get(maxScoreIdx);
        } else {
            return state;
        } // Return the best move (child state)
    }

    // You can use this as a helper to time your minimax method
    public static void measureDuration(Runnable task) {
        long startTime = System.nanoTime();
        task.run();
        long endTime = System.nanoTime();
        System.out.println("Execution time: " + (endTime - startTime) + " ns");
    }
}
