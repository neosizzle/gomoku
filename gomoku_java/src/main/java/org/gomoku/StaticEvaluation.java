package org.gomoku;

import com.google.common.primitives.Bytes;
import com.google.protobuf.ByteString;
import game.GameOuterClass;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Vector;
import java.util.function.Function;

public class StaticEvaluation {

    // preallocation constant for directionCells, should be big enough to
    // at the maximum of all elements in allIndicesDirections
    // assuming we handle up to size 19x19, the max should be size 19
    static final int DIR_CELLS_CAP = 19;
    static final byte FIN_BYTE = (byte) 255;
    public static List<List<Byte>> extractDimensionalCells(byte[] board, List<List<Integer>> rowIndices) {
        List<List<Byte>> directionCells = new ArrayList<>(DIR_CELLS_CAP);
        for (List<Integer> rowIndexSet : rowIndices) {
            List<Byte> rowCells = new ArrayList<>(DIR_CELLS_CAP);
            for (int index : rowIndexSet) {
                rowCells.add(board[index]);
            }
            directionCells.add(rowCells);
        }
        return directionCells;
    }

    // Generate row indices
    public static List<List<Integer>> generateRowIndices(int boardSize) {
        List<List<Integer>> rowIndices = new ArrayList<>(boardSize);
        for (int i = 0; i < boardSize; i++) {
            List<Integer> currRow = new ArrayList<>(boardSize);
            for (int j = 0; j < boardSize; j++) {
                currRow.add(i * boardSize + j);
            }
            rowIndices.add(currRow);
        }
        return rowIndices;
    }

    // Generate column indices
    public static List<List<Integer>> generateColumnIndices(int boardSize) {
        List<List<Integer>> columnIndices = new ArrayList<>(boardSize);
        for (int i = 0; i < boardSize; i++) {
            List<Integer> currCol = new ArrayList<>(boardSize);
            for (int j = 0; j < boardSize; j++) {
                currCol.add(i + (boardSize * j));
            }
            columnIndices.add(currCol);
        }
        return columnIndices;
    }

    // Generate diagonal indices (normal direction)
    public static List<List<Integer>> generateDiagIndices(int boardSize) {
        List<List<Integer>> diagIndices = new ArrayList<>(boardSize);
        int combs = boardSize + (boardSize - 1);
        int counter = 1;
        boolean directionUp = true;
        for (int i = 0; i < combs; i++) {
            if (i == 0) {
                diagIndices.add(Arrays.asList(0));
                counter++;
                continue;
            }

            int smallestElem = directionUp ? diagIndices.get(i - 1).get(0) + 1 : diagIndices.get(i - 1).get(1) + 1;

            List<Integer> buffer = new ArrayList<>(counter);
            for (int j = 0; j < counter; j++) {
                buffer.add(smallestElem + (j * (boardSize - 1)));
            }
            diagIndices.add(buffer);

            if (directionUp) {
                if (counter == boardSize) {
                    counter--;
                    directionUp = false;
                } else {
                    counter++;
                }
            } else {
                counter--;
            }
        }
        return diagIndices;
    }

    // Generate inverse diagonal indices
    public static List<List<Integer>> generateDiagIndicesInverse(int boardSize) {
        List<List<Integer>> diagIndices = new ArrayList<>(boardSize);
        int combs = boardSize + (boardSize - 1);
        int counter = 1;
        boolean directionUp = true;
        for (int i = 0; i < combs; i++) {
            if (i == 0) {
                diagIndices.add(Arrays.asList(boardSize - 1));
                counter++;
                continue;
            }
            int smallestElem = directionUp ? diagIndices.get(i - 1).get(0) - 1 : diagIndices.get(i - 1).get(1) - 1;

            List<Integer> buffer = new ArrayList<>(counter);
            for (int j = 0; j < counter; j++) {
                buffer.add(smallestElem + (j * (boardSize + 1)));
            }
            diagIndices.add(buffer);

            if (directionUp) {
                if (counter == boardSize) {
                    counter--;
                    directionUp = false;
                } else {
                    counter++;
                }
            } else {
                counter--;
            }
        }
        return diagIndices;
    }

    public static int calculateGapPenalty(int startIdx, int endIdx, List<Byte> extraction, byte ourPiece) {
        int penaltyEndIdx = startIdx;
        int penaltyStartIdx = startIdx;
        int res = 0;
        while (penaltyEndIdx != endIdx) {
            // move penalty_end to either the blank or end 
            while (penaltyEndIdx != endIdx && extraction.get(penaltyEndIdx) != 0) {
                penaltyEndIdx++;
            }

            // if penalty_end is at end already, can break, should be no more penalty
            if (penaltyEndIdx == endIdx) {
                break;
            }

            // move penalty_end to the next non-blank symbol
            while (penaltyEndIdx != endIdx && extraction.get(penaltyEndIdx) == 0) {
                penaltyEndIdx++;
            }
            
            // if penalty_end is at end already, can break, should be no more penalty
            if (penaltyEndIdx == endIdx) {
                break;
            }

            // can assume penalty_end is at enemy piece now, move penalty start to a non - our piece
            while (extraction.get(penaltyStartIdx) == ourPiece) {
                penaltyStartIdx++;
            }

            // can assume that penalty_end is actually bigger than penalty_start now, get diff
            // if diff is more than winning  piece count, incur 1 point penalty
            int diff = penaltyEndIdx - penaltyStartIdx;
            if (diff > 4) {
                res++;
            }
        }
        return res;
    }

    public static int calculateOpenBonus(List<Byte> extraction, int ourPiece, int movesNext) {
        int res = 0;
        int start = -1;

        while (start < extraction.size() - 1) {
            start++;
            int gap = 0;
            int power = 3;
            int cumCount = 1;

            // keep going until start hits our piece
            if (extraction.get(start) != ourPiece) {
                continue;
            }

            // we hit our piece, check for left edge and left enemy
            if (start == 0 || extraction.get(start - 1) != 0) {
                power--;
            }

            // move start until the end of combo, counting our pieces
            while (start < extraction.size()) {
                start++;
                if (start == extraction.size() || extraction.get(start - 1) != ourPiece) {
                    break;
                }
                if (extraction.get(start) == 0) {
                    if (gap == 0) {
                        gap++;
                        continue;
                    } else {
                        break;
                    }
                }
                cumCount++;
            }

            // check if we end the combo at an edge / enemy
            if (start == extraction.size() || extraction.get(start) != 0) {
                power--;
            }

            res += Math.pow(cumCount, power);
        }

        // bonus multiplier if we are moving next
        if (movesNext == ourPiece) {
            return res * res;
        }
        return res;
    }

    public static int countPieces(byte[] board, int piece) {

        int count = 0;
        for (byte cell : board) {
            if (cell == piece) {
                count++;
            }
        }

        return count;
    }

    public static int staticEvalDirectional(
            int boardSize,
            GameOuterClass.GameState gameState,
            byte ourPiece,
            int ourCaptures,
            byte enemyPiece,
            int movesNext,
            List<Integer> is_win_check
    ) {
        int dimension = boardSize * boardSize;
        byte[] board = gameState.getBoard().toByteArray();
        int scoreRes = countPieces(board, ourPiece);

        // Generate indices for all directions
        List<List<List<Integer>>> allIndicesDirections = new ArrayList<>(4);
        allIndicesDirections.add(generateRowIndices(boardSize));
        allIndicesDirections.add(generateColumnIndices(boardSize));
        allIndicesDirections.add(generateDiagIndicesInverse(boardSize));
        allIndicesDirections.add(generateDiagIndices(boardSize));

        for (List<List<Integer>> directionIndices : allIndicesDirections) {
            List<List<Byte>> directionCells = extractDimensionalCells(board, directionIndices);

            // check if we win, if yes, return early and write to is_win_check
            GomokuUtils utils = new GomokuUtils(boardSize);

            if (ourCaptures >= 5) {
                is_win_check.set(0, 1);
                return 0;
            }
            
            for (int i = 0; i < directionCells.size(); i++) {
                List<Byte> extraction = directionCells.get(i);
                int cumCount = 0;
                for (int cell : extraction) {
                    if (cell == ourPiece) {
                        cumCount++;
                    } else {
                        cumCount = 0;
                    }

                    if (cumCount >= 5) {
                        if (checkWinCombNoCap(board, directionIndices.get(i), utils)) {
                            is_win_check.set(0, 1);
                            return 0;
                        }
                    }
                }
            }

            int totalScore = 0;
            for (List<Byte> extraction : directionCells) {
                int startIdx = 0;
                int endIdx = 0;
                int extractionScore = 0;

                while (startIdx < extraction.size()) {
                    // Move start index to our piece
                    while (startIdx < extraction.size() && extraction.get(startIdx) != ourPiece) {
                        startIdx++;
                    }
                    if (startIdx == extraction.size()) break;

                    endIdx = startIdx;

                    // Move end index to enemy piece or edge
                    while (endIdx < extraction.size() && extraction.get(endIdx) != enemyPiece) {
                        endIdx++;
                    }
                    			
                    // Count number of our pieces in the section and append score
                    int numPiecesSection = 0;
                    for (int i = startIdx; i < endIdx; i++) {
                        if (extraction.get(i) == ourPiece)
                            ++numPiecesSection;
                    }
                    extractionScore += numPiecesSection;

                    // Penalize big gaps in our combos (low sensitivity)
                    extractionScore -= calculateGapPenalty(startIdx, endIdx, extraction, ourPiece);

                    // Move start index to the current end index
                    startIdx = endIdx;
                }

                extractionScore += calculateOpenBonus(extraction, ourPiece, movesNext);

                
                totalScore += extractionScore;
            }
            scoreRes += totalScore;
        }
        return scoreRes;
    }

    public static boolean validateNoCapDirection(
            Function<Integer, Integer> directionFn,
            Function<Integer, Integer> antiDirectionFn,
            int idx,
            int currPiece,
            byte[] board
    ) {
        int checkCellIdx = directionFn.apply(idx);
        if (checkCellIdx < 0 || checkCellIdx >= board.length) {
            return false; // Index is out of bounds
        }
        int checkCell = board[checkCellIdx];

        // Check if the cell in the given direction is the current piece
        if (checkCell == currPiece) {
            // Get the next cell in the same direction
            int nextCellIdx = directionFn.apply(checkCellIdx);
            if (nextCellIdx < 0 || nextCellIdx >= board.length) {
                return false; // Index is out of bounds
            }
            int checkNeighCell = board[nextCellIdx];

            if (checkNeighCell != currPiece && checkNeighCell != 0) {
                // Check the anti-direction
                int antiDirectCell = antiDirectionFn.apply(idx);
                if (antiDirectCell < 0 || antiDirectCell >= board.length) {
                    return false; // Index is out of bounds
                }
                int antiCell = board[antiDirectCell];
                return (antiCell == currPiece || antiCell == 0);
            }
        }

        return true;
    }

    public static boolean checkWinCondition(
            int boardSize,
            GameOuterClass.GameState gameState,
            int ourPiece,
            int ourCaptures
    ) {
        byte[] board = gameState.getBoard().toByteArray();
        GomokuUtils utils = new GomokuUtils(boardSize);
        if (ourCaptures >= 5) {
            return true;
        }

        // Generate indices for all directions
        List<List<List<Integer>>> allIndicesDirections = new ArrayList<>(4);
        allIndicesDirections.add(generateRowIndices(boardSize));
        allIndicesDirections.add(generateColumnIndices(boardSize));
        allIndicesDirections.add(generateDiagIndicesInverse(boardSize));
        allIndicesDirections.add(generateDiagIndices(boardSize));

        for (List<List<Integer>> directionIndices : allIndicesDirections) {
            List<List<Byte>> directionCells = extractDimensionalCells(board, directionIndices);

            for (int i = 0; i < directionCells.size(); i++) {
                List<Byte> extraction = directionCells.get(i);
                int cumCount = 0;
                for (int cell : extraction) {
                    if (cell == ourPiece) {
                        cumCount++;
                    } else {
                        cumCount = 0;
                    }

                    if (cumCount >= 5) {
                        if (checkWinCombNoCap(board, directionIndices.get(i), utils)) {
                        return true;
                        }
                    }
                }
            }
        }

        return false;
    }

    public static boolean validatePotentialNoCapDirection(
            Function<Integer, Integer> directionFn,
            Function<Integer, Integer> antiDirectionFn,
            int idx,
            int currPiece,
            byte[] board) {

        if (currPiece != 1 && currPiece != 2) {
            return true;
        }

        int checkCellIdx = directionFn.apply(idx);
        if (checkCellIdx < 0 || checkCellIdx >= board.length) {
            return true;
        }
        byte checkCell = board[checkCellIdx];

        if (checkCell == currPiece) {
            int nextCellIdx = directionFn.apply(checkCellIdx);
            if (nextCellIdx < 0 || nextCellIdx >= board.length) {
                return true;
            }
            byte checkNeighCell = board[nextCellIdx];

            if (checkNeighCell != currPiece && checkNeighCell != 0) {
                int antiDirectCell = antiDirectionFn.apply(idx);
                if (antiDirectCell < 0 || antiDirectCell >= board.length) {
                    return true;
                }
                byte antiCell = board[antiDirectCell];
                return (antiCell == currPiece || antiCell == 0);
            }
        }

        if (checkCell != 0 && checkCell != -1 && checkCell != currPiece) {
            int antiDirIdx = antiDirectionFn.apply(idx);
            if (antiDirIdx < 0 || antiDirIdx >= board.length) {
                return true;
            }
            byte checkNeighCell = board[antiDirIdx];

            if (checkNeighCell == currPiece) {
                int secondAntiDirIdx = antiDirectionFn.apply(antiDirIdx);
                if (secondAntiDirIdx < 0 || secondAntiDirIdx >= board.length) {
                    return true;
                }
                byte secondCheckNeighCell = board[secondAntiDirIdx];

                return secondCheckNeighCell != 0;
            }
        }

        return true;
    }
    public static boolean checkWinCombNoCap(byte[] board, List<Integer> indiceToCheck, GomokuUtils utils) {
        List<Boolean> endgameCapValidationRes = new ArrayList<>(8 * (indiceToCheck.size()));
        for (int cumIdx : indiceToCheck) {
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getBtmIdx, utils::getTopIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getTopIdx, utils::getBtmIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getLeftIdx, utils::getRightIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getRightIdx, utils::getLeftIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getBtmLeftIdx, utils::getTopRightIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getTopRightIdx, utils::getBtmLeftIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getTopLeftIdx, utils::getBtmRightIdx, cumIdx, board[cumIdx], board));
            endgameCapValidationRes.add(validatePotentialNoCapDirection(utils::getBtmRightIdx, utils::getTopLeftIdx, cumIdx, board[cumIdx], board));
        }
        return !endgameCapValidationRes.contains(false);
    }

    public static int staticEval(
            int boardSize,
            GameOuterClass.GameState gameState,
            int ourPiece,
            int enemyPiece,
            int ourCaptures,
            int enemyCaptures
    ) {
        int movesNext = (gameState.getNumTurns() % 2 == 0) ? 1 : 2;
        // long startTime = System.nanoTime();  // Start timing

        List<Integer> is_win_check_ours = new ArrayList<>(1);
        is_win_check_ours.add(0);

        List<Integer> is_win_check_enemy = new ArrayList<>(1);
        is_win_check_enemy.add(0);

        int myScore = staticEvalDirectional(boardSize, gameState, (byte)ourPiece, ourCaptures, (byte)enemyPiece, movesNext, is_win_check_ours);
        int finalScore = myScore + (int) Math.pow(gameState.getNumTurns(), ourCaptures);

        int enemyScore = staticEvalDirectional(boardSize, gameState, (byte)enemyPiece, enemyCaptures, (byte)ourPiece, movesNext, is_win_check_enemy);
        finalScore -= enemyScore;
        finalScore -= (int) Math.pow(gameState.getNumTurns(), enemyCaptures);

        // Kill shot - assuming that there can be no 2 simultaneous winners
        if (is_win_check_ours.get(0) == 1) {
            finalScore = Integer.MAX_VALUE; // not using actual value since we want to do range compare @ minimax
        }

        if (is_win_check_enemy.get(0) == 1) {
            finalScore = Integer.MIN_VALUE; // not using actual value since we want to do range compare @ minimax
        }

        // long endTime = System.nanoTime();    // End timing
        // long durationNs = endTime - startTime; // Duration in nanoseconds
        // String formattedDuration = TimeFormatter.formatTime(durationNs);
        // System.out.println("Function staticEval took " + formattedDuration);
        return finalScore;
    }
}
