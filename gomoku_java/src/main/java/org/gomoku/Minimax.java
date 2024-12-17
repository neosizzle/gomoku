package org.gomoku;

import game.GameOuterClass;
import org.gomoku.TimeFormatter;

import java.util.List;

public class Minimax {
    public static int minimaxEval(
            List<GomokuUtils.GameStateNode> moveTree,
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
            GomokuUtils.GameStateNode node = moveTree.get(i);
            if (node.children() == null) {
                continue;
            }
            GameOuterClass.GameState nodeState = (GameOuterClass.GameState) node.state();
            if (nodeState.getBoard().equals(currState.getBoard()) && !node.children().isEmpty()) {
                stateNodeIndex = i;
                break;
            }
        }

        // If no valid state found, perform static evaluation
        if (stateNodeIndex == -1) {
            // System.out.println("curr depth static " + currDepth + " ismax? " + isMax);
            return StaticEvaluation.staticEval(BOARD_SIZE, currState, ourPiece, enemyPiece, ourCaptures, enemyCaptures);
        }

        // System.out.println(" ".repeat(currDepth * 2) + "CALLED, is max: " + isMax);
        // GomokuUtils gomokuUtils = new GomokuUtils(BOARD_SIZE);
        // gomokuUtils.prettyPrintBoardIndent(currState.getBoard().toByteArray(), currDepth);
        // System.out.println("");

        // Initialize idealScore based on whether we're maximizing or minimizing
        GomokuUtils.GameStateNode moveTreeNode = moveTree.get(stateNodeIndex);
        List<GameOuterClass.GameState> moveTreeChildren = moveTreeNode.children();

        int idealScore;
        GameOuterClass.GameState selectedState = null;

        if (isMax) {
            idealScore = Integer.MIN_VALUE;
            for (GameOuterClass.GameState childState : moveTreeChildren) {
                int childScore = minimaxEval(moveTree, childState, BOARD_SIZE, false, maxPiece, currDepth + 1, alpha, beta);
                if (childScore > idealScore) {
                    // System.out.println(" ".repeat(currDepth * 2) + "SELECTED, score: " + childScore);
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
                    // System.out.println(" ".repeat(currDepth * 2) + "SELECTED, score: " + childScore);
                    selectedState = childState;
                }
                idealScore = Math.min(idealScore, childScore);
                beta = Math.min(beta, idealScore);
                if (beta <= alpha) {
                    break;
                }
            }
        }

        // System.out.println(" ".repeat(currDepth * 2) + "returning ideal score: " + idealScore);
        // if (selectedState != null)
        //     gomokuUtils.prettyPrintBoardIndent(selectedState.getBoard().toByteArray(), currDepth);
        // else {
        //     System.out.println(" ".repeat(currDepth * 2) + "null");
        // }

        return idealScore;
    }

    // Basic minimax function to select the best move from the current state
    public static GameOuterClass.GameState basicMinimax(GameOuterClass.GameState state, int boardSize, int currPiece, int maxPiece) {
        // Decorators does not exist in java, so we have to manually measure time
        long startTime = System.nanoTime();  // Start timing

        int depth = (state.getNumTurns() > 4) ? 3 : 2;
        // Generate move tree (you'll need a function for move generation in Java)
        MoveGeneration moveGeneration = new MoveGeneration(boardSize);
        List<GomokuUtils.GameStateNode> moveTree = moveGeneration.generateMoveTree(state, boardSize, (byte) currPiece, depth);
        GameOuterClass.GameState rootNode =  moveTree.get(0).state();
        List<GameOuterClass.GameState> rootChildren =  moveTree.get(0).children();

        int maxScore = Integer.MIN_VALUE;
        int maxScoreIdx = -1;

        // Iterate through root's children and evaluate them
        for (int i = 0; i < rootChildren.size(); i++) {
            GameOuterClass.GameState child = rootChildren.get(i);
            int childScore = minimaxEval(moveTree, child, boardSize, currPiece != maxPiece, maxPiece, 0, Integer.MIN_VALUE, Integer.MAX_VALUE);
            if (childScore >= maxScore) {
                maxScore = childScore;
                maxScoreIdx = i;
            }
        }

        GameOuterClass.GameState res = GameOuterClass.GameState.newBuilder().build();
        if (maxScoreIdx >= 0 && maxScoreIdx < rootChildren.size()) {
            res =  rootChildren.get(maxScoreIdx);
        } else {
            res = state;
        }
        
        long endTime = System.nanoTime();    // End timing
        long durationNs = endTime - startTime; // Duration in nanoseconds
        String formattedDuration = TimeFormatter.formatTime(durationNs);

        System.out.println("Function basicMinimax took " + formattedDuration);

        return res;
    }

    // You can use this as a helper to time your minimax method
    public static void measureDuration(Runnable task) {
        long startTime = System.nanoTime();
        task.run();
        long endTime = System.nanoTime();
        System.out.println("Execution time: " + (endTime - startTime) + " ns");
    }
}
