package org.gomoku;

import com.google.common.primitives.Bytes;
import com.google.protobuf.ByteString;
import game.GameOuterClass;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.Function;

public class StaticEvaluation {
    public static List<List<Byte>> extractDimensionalCells(byte[] board, List<List<Integer>> rowIndices) {
        List<List<Byte>> directionCells = new ArrayList<>();
        for (List<Integer> rowIndexSet : rowIndices) {
            List<Byte> rowCells = new ArrayList<>();
            for (int index : rowIndexSet) {
                rowCells.add(board[index]);
            }
            directionCells.add(rowCells);
        }
        return directionCells;
    }

    // Generate row indices
    public static List<List<Integer>> generateRowIndices(int boardSize) {
        List<List<Integer>> rowIndices = new ArrayList<>();
        for (int i = 0; i < boardSize; i++) {
            List<Integer> currRow = new ArrayList<>();
            for (int j = 0; j < boardSize; j++) {
                currRow.add(i * boardSize + j);
            }
            rowIndices.add(currRow);
        }
        return rowIndices;
    }

    // Generate column indices
    public static List<List<Integer>> generateColumnIndices(int boardSize) {
        List<List<Integer>> columnIndices = new ArrayList<>();
        for (int i = 0; i < boardSize; i++) {
            List<Integer> currCol = new ArrayList<>();
            for (int j = 0; j < boardSize; j++) {
                currCol.add(i + (boardSize * j));
            }
            columnIndices.add(currCol);
        }
        return columnIndices;
    }

    // Generate diagonal indices (normal direction)
    public static List<List<Integer>> generateDiagIndices(int boardSize) {
        List<List<Integer>> diagIndices = new ArrayList<>();
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

            List<Integer> buffer = new ArrayList<>();
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
        List<List<Integer>> diagIndices = new ArrayList<>();
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

            List<Integer> buffer = new ArrayList<>();
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

    public static int calculateGapPenalty(int startIdx, int endIdx, byte[] extraction, byte ourPiece) {
        int penaltyEndIdx = startIdx;
        int penaltyStartIdx = startIdx;
        int res = 0;
        while (penaltyEndIdx != endIdx) {
            while (penaltyEndIdx != endIdx && extraction[penaltyEndIdx] != 0) {
                penaltyEndIdx++;
            }
            if (penaltyEndIdx == endIdx) {
                break;
            }

            while (penaltyEndIdx != endIdx && extraction[penaltyEndIdx] == 0) {
                penaltyEndIdx++;
            }
            if (penaltyEndIdx == endIdx) {
                break;
            }

            while (extraction[penaltyStartIdx] == ourPiece) {
                penaltyStartIdx++;
            }

            int diff = penaltyEndIdx - penaltyStartIdx;
            if (diff > 4) {
                res++;
            }
        }
        return res;
    }

    public static int calculateOpenBonus(byte[] extraction, int ourPiece, int movesNext) {
        int res = 0;
        int start = -1;

        while (start < extraction.length - 1) {
            start++;
            int gap = 0;
            int power = 3;
            int cumCount = 1;

            if (extraction[start] != ourPiece) {
                continue;
            }
            if (start == 0 || extraction[start - 1] != 0) {
                power--;
            }

            while (start < extraction.length) {
                start++;
                if (start == extraction.length || extraction[start] != ourPiece) {
                    break;
                }
                if (extraction[start] == 0) {
                    if (gap == 0) {
                        gap++;
                        continue;
                    } else {
                        break;
                    }
                }
                cumCount++;
            }

            if (start == extraction.length || extraction[start] != 0) {
                power--;
            }

            res += Math.pow(cumCount, power);
        }
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
            byte enemyPiece,
            int movesNext
    ) {
        int dimension = boardSize * boardSize;
        byte[] board = gameState.getBoard().toByteArray();
        int scoreRes = countPieces(board, ourPiece);

        // Generate indices for all directions
        List<List<List<Integer>>> allIndicesDirections = new ArrayList<>();
        allIndicesDirections.add(generateRowIndices(boardSize));
        allIndicesDirections.add(generateColumnIndices(boardSize));
        allIndicesDirections.add(generateDiagIndicesInverse(boardSize));
        allIndicesDirections.add(generateDiagIndices(boardSize));

        for (List<List<Integer>> directionIndices : allIndicesDirections) {
            List<List<Byte>> directionCells = extractDimensionalCells(board, directionIndices);

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

                    // Extract section
                    List<Byte> section = extraction.subList(startIdx, endIdx);

                    // Count number of our pieces in the section and append score
                    int numPiecesSection = (int) section.stream().filter(piece -> piece == ourPiece).count();
                    extractionScore += numPiecesSection;

                    // Penalize big gaps in our combos (low sensitivity)
                    extractionScore -= calculateGapPenalty(startIdx, endIdx, Bytes.toArray(extraction), ourPiece);

                    // Move start index to the current end index
                    startIdx = endIdx;
                }
                extractionScore += calculateOpenBonus(Bytes.toArray(extraction), ourPiece, movesNext);
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
            int boardSize,
            int currPiece,
            byte[] board
    ) {
        int checkCellIdx = directionFn.apply(idx);
        int checkCell = board[checkCellIdx];

        // Check if the cell in the given direction is the current piece
        if (checkCell == currPiece) {
            int checkNeighCell = board[(directionFn.apply(checkCellIdx))];
            if (checkNeighCell != currPiece && checkNeighCell != 0) {
                int antiDirectCell = board[(antiDirectionFn.apply(idx))];
                return antiDirectCell == currPiece || antiDirectCell == 0;
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

        if (ourCaptures >= 5) {
            return true;
        }

        // Generate indices for all directions
        List<List<List<Integer>>> allIndicesDirections = new ArrayList<>();
        allIndicesDirections.add(generateRowIndices(boardSize));
        allIndicesDirections.add(generateColumnIndices(boardSize));
        allIndicesDirections.add(generateDiagIndicesInverse(boardSize));
        allIndicesDirections.add(generateDiagIndices(boardSize));

        for (List<List<Integer>> directionIndices : allIndicesDirections) {
            List<List<Byte>> directionCells = extractDimensionalCells(board, directionIndices);

            for (List<Byte> extraction : directionCells) {
                int cumCount = 0;
                for (int cell : extraction) {
                    if (cell == ourPiece) {
                        cumCount++;
                    } else {
                        cumCount = 0;
                    }

                    if (cumCount >= 5) {
                        return true;
                    }
                }
            }
        }

        return false;
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


        int myScore = staticEvalDirectional(boardSize, gameState, (byte)ourPiece, (byte)enemyPiece, movesNext);
        int finalScore = myScore + ourCaptures * 2;

        int enemyScore = staticEvalDirectional(boardSize, gameState, (byte)enemyPiece, (byte)ourPiece, movesNext);
        finalScore -= enemyScore;
        finalScore -= enemyCaptures * 2;

        // Kill shot
        if (checkWinCondition(boardSize, gameState, 1, (int) gameState.getP1Captures())) {
            finalScore += (ourPiece == 1) ? 6969 : -6969;
        }

        if (checkWinCondition(boardSize, gameState, 2, (int) gameState.getP2Captures())) {
            finalScore += (ourPiece == 2) ? 6969 : -6969;
        }

        return finalScore;
    }
}
