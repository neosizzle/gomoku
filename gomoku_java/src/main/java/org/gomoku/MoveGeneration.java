package org.gomoku;


import com.google.protobuf.ByteString;
import game.GameOuterClass;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collector;
import java.util.stream.Collectors;

public class MoveGeneration {

    private final GomokuUtils gomokuUtils;

    MoveGeneration(int boardSize) {
        gomokuUtils = new GomokuUtils(boardSize);
    }
    public List<List<Integer>> expandAllDirections(int idx, int depth) {
        List<List<Integer>> res = new ArrayList<>();
        List<Function<Integer, Integer>> dirFns = List.of(gomokuUtils::getTopIdx,
                gomokuUtils::getBtmIdx,
                gomokuUtils::getLeftIdx,
                gomokuUtils::getRightIdx,
                gomokuUtils::getTopLeftIdx,
                gomokuUtils::getTopRightIdx,
                gomokuUtils::getBtmLeftIdx,
                gomokuUtils::getBtmRightIdx);

        for (Function<Integer, Integer> dir : dirFns) {
            int lastDirRes = idx;
            List<Integer> curr = new ArrayList<>();
            for (int i = 0; i < depth; i++) {
                int newDirRes = dir.apply(lastDirRes);
                if (newDirRes == -1) break;
                curr.add(newDirRes);
                lastDirRes = newDirRes;
            }
            res.add(curr);
        }
        return res;
    }

    // Checks if a capture is made by placing curr_piece at idx
    public static boolean checkCaptureMadeDir(Function<Integer, Integer> directionFn, int idx, int boardSize, int currPiece, byte[] board) {
        byte piece = (byte) currPiece;
        int checkCellIdx = directionFn.apply(idx);
        byte checkCell = checkCellIdx > 0 ? board[checkCellIdx] : -1;

        if (checkCell > 0 && checkCell != piece) {
            checkCellIdx = directionFn.apply(checkCellIdx);
            checkCell = checkCellIdx > 0 ? board[checkCellIdx] : -1;

            if (checkCell > 0 && checkCell != piece) {
                checkCellIdx = directionFn.apply(checkCellIdx);
                checkCell = checkCellIdx > 0 ? board[checkCellIdx] : -1;

                return checkCell == piece;
            }
        }
        return false;
    }

    // Group local expansions
    public static List<List<Integer>> groupLocalExpansions(List<List<Integer>> localExpansions) {
        List<List<Integer>> res = new ArrayList<>();

        res.add(concatReverse(localExpansions.get(0), localExpansions.get(1)));
        res.add(concatReverse(localExpansions.get(2), localExpansions.get(3)));
        res.add(concatReverse(localExpansions.get(4), localExpansions.get(7)));
        res.add(concatReverse(localExpansions.get(5), localExpansions.get(6)));

        return res;
    }

    // Helper method to concatenate two lists with the first list reversed
    private static List<Integer> concatReverse(List<Integer> list1, List<Integer> list2) {
        List<Integer> result = new ArrayList<>();
        for (int i = list1.size() - 1; i >= 0; --i)
            result.add(list1.get(i));
        for (int i = 0; i < list2.size(); ++i)
            result.add(list2.get(i));

        return result;
    }

    // Check if a buffer has a free three for the given piece
    public static boolean hasFreeThree(List<Byte> buffer, byte piece, int idxToPlace) {
        if (buffer.size() < 5 || idxToPlace == -1) {
            return false;
        }

        List<Byte> bufferClone = new ArrayList<>(buffer);
        bufferClone.set(idxToPlace, piece);
        int begin = 0;

        while (begin < bufferClone.size()) {
            int end = begin + 1;
            while (end < bufferClone.size()) {
                if (bufferClone.get(end) != piece && bufferClone.get(end) != 0) {
                    break;
                }
                if (bufferClone.get(end) == 0) {
                    break;
                }
                end++;
            }

            if (begin == 0 || end == bufferClone.size()) {
                begin = end;
                continue;
            }

            if (!(idxToPlace >= begin && idxToPlace <= end)) {
                begin = end;
                continue;
            }

            if (end - begin == 4 && bufferClone.get(begin) == 0 && bufferClone.get(end) == 0) {
                return true;
            }
            begin = end;
        }

        return false;
    }

    // Detect double free threes when placing a piece
    public boolean detectDoubleFreeThrees(int inputIdx, int BOARD_SIZE, byte piece, byte[] board) {
        List<List<Integer>> localExpansions = expandAllDirections(inputIdx, BOARD_SIZE);
        List<List<Integer>> localExpansionGrouping = groupLocalExpansions(localExpansions);

        List<List<Byte>> cellValueBuffers = new ArrayList<>();
        List<Integer> groupIndices = new ArrayList<>();

        for (List<Integer> localExpansion : localExpansionGrouping) {
            List<Byte> cellValues = new ArrayList<>();
            int groupIdx = -1;

            for (int i = 0; i < localExpansion.size(); i++) {
                int expansionIndex = localExpansion.get(i);

                if (expansionIndex > inputIdx && groupIdx == -1) {
                    cellValues.add(board[inputIdx]);
                    groupIdx = i;
                }

                cellValues.add(board[expansionIndex]);
            }

            if (groupIdx == -1) {
                cellValues.add(board[inputIdx]);
                groupIdx = cellValues.size() - 1;
            }

            cellValueBuffers.add(cellValues);
            groupIndices.add(groupIdx);
        }

        int freeThreeIdx = -1;
        for (int i = 0; i < cellValueBuffers.size(); i++) {
            List<Byte> buffer = cellValueBuffers.get(i);
            if (hasFreeThree(buffer, piece, groupIndices.get(i))) {
                if (freeThreeIdx != -1) {
                    return true;
                }
                freeThreeIdx = i;
            }
        }

        return false;
    }

    public boolean hasThreat(int inputIdx, int BOARD_SIZE, byte piece, byte[] board) {
        // Generate local expansions of current piece
        List<List<Integer>> localExpansions = expandAllDirections(inputIdx, BOARD_SIZE);
        
        // Group pairs of directions together
        List<List<Integer>> localExpansionGrouping = groupLocalExpansions(localExpansions);
        
        List<List<Byte>> cellValueBuffers = new ArrayList<>();
        List<Integer> groupIndices = new ArrayList<>();

        for (List<Integer> localExpansion : localExpansionGrouping) {
            List<Byte> cellValues = new ArrayList<>();
            int groupIdx = -1;
            for (int i = 0; i < localExpansion.size(); i++) {
                int expansionIndex = localExpansion.get(i);

                // If the current idx is more than the idx stated in expansion
                if (expansionIndex > inputIdx && groupIdx == -1) {
                    cellValues.add(board[inputIdx]);
                    groupIdx = i; // the index where the input index is located at the group
                }

                cellValues.add(board[expansionIndex]);
            }

            if (groupIdx == -1) {
                cellValues.add(board[inputIdx]);
                groupIdx = cellValues.size() - 1;
            }

            cellValueBuffers.add(cellValues);
            groupIndices.add(groupIdx);
        }

        // Check if a threat formation or threat block is detected
        for (int i = 0; i < cellValueBuffers.size(); i++) {
            List<Byte> cellValues = cellValueBuffers.get(i);
            int idxToPlace = groupIndices.get(i);
            if (detectThreatFormation(cellValues, piece, idxToPlace) || detectThreatBlock(cellValues, piece, idxToPlace)) {
                return true;
            }
        }

        return false;
    }

    // Detects threat formation when attempting to place a piece
    public static boolean detectThreatFormation(List<Byte> buffer, byte piece, int idxToPlace) {
        int startIdx = idxToPlace - 1;
        int endIdx = idxToPlace + 1;
        boolean gap = false;

        // Initial gap detection for startIdx and endIdx
        if (startIdx >= 0 && buffer.get(startIdx) == 0 && !gap) {
            if (startIdx > 2 && buffer.get(startIdx - 2) == piece) {
                gap = true;
                startIdx--;
            }
        }

        if (endIdx < buffer.size() && buffer.get(endIdx) == 0 && !gap) {
            if (endIdx < buffer.size() - 2 && buffer.get(endIdx + 2) == piece) {
                gap = true;
                endIdx++;
            }
        }

        // Move startIdx to the start of the threat sequence, gap sensitive
        while (startIdx >= 0 && buffer.get(startIdx) == piece) {
            // Early gap detection
            if (startIdx > 1) {
                if (buffer.get(startIdx - 1) == 0 && buffer.get(startIdx - 2) == piece && !gap) {
                    gap = true;
                    startIdx--;
                }
            }
            startIdx--;
        }

        // Move endIdx to the end of the threat sequence, gap sensitive
        while (endIdx < buffer.size() && buffer.get(endIdx) == piece) {
            // Early gap detection
            if (endIdx < buffer.size() - 2) {
                if (buffer.get(endIdx + 1) == 0 && buffer.get(endIdx + 2) == piece && !gap) {
                    gap = true;
                    endIdx++;
                }
            }
            endIdx++;
        }

        boolean startClosed = startIdx == -1 || buffer.get(startIdx) != 0;
        boolean endClosed = endIdx == buffer.size() || buffer.get(endIdx) != 0;

        // Evaluate real threat size
        int realThreatSize = endIdx - startIdx - 1;

        // Calculate potential threat size
        if (!startClosed) {
            // this assumption should be true if startClosed is false, gap sensitive
            while (startIdx >= 0 && buffer.get(startIdx) == (byte)0) {
                // early gap detection
                if (startIdx > 1) {
                    if (buffer.get(startIdx - 1) == (byte)0 && buffer.get(startIdx -2) == (byte)piece && !gap) {
                        gap = true;
                        startIdx--;
                    }
                }
                startIdx--;
            }
        }


        if (!endClosed) {
            while (endIdx < buffer.size() && buffer.get(endIdx) == 0) {
                if (endIdx < buffer.size() - 2) {
                    if (buffer.get(endIdx + 1) == 0 && buffer.get(endIdx + 2) == piece && !gap) {
                        gap = true;
                        endIdx++;
                    }
                }
                endIdx++;
            }
        }

        int potentialThreatSize = endIdx - startIdx;

        // Comparison
        if (realThreatSize < 3) {
            return false;
        }

        if (potentialThreatSize < 6) {
            return false;
        }

        return !startClosed || !endClosed || realThreatSize >= 5;
    }

    // Detects threat when attempting to place a piece, returns true if an enemy threat is blocked
    public static boolean detectThreatBlock(List<Byte> buffer, int piece, int idxToPlace) {
        byte enemyPiece = (piece == 1) ? (byte) 2 : (byte) 1;
        boolean validThreat = detectThreatFormation(buffer, enemyPiece, idxToPlace);
        if (!validThreat) {
            return false;
        }

        // Since we are defending, no gaps should be allowed
        int leftIdx = idxToPlace - 1;
        int rightIdx = idxToPlace + 1;

        if (leftIdx > 1) {
            if (buffer.get(leftIdx) == 0 && buffer.get(leftIdx - 1) == enemyPiece) {
                return false;
            }
        }

        if (rightIdx < buffer.size() - 2) {
            return buffer.get(rightIdx) != 0 || buffer.get(rightIdx + 1) != enemyPiece;
        }

        return true;
    }

    public GameOuterClass.GameState placePieceAttempt(int index, byte piece, GameOuterClass.GameState state, int BOARD_SIZE, boolean ignoreSelfCaptured) {
        byte[] board = state.getBoard().toByteArray();

        // Validate if the board index is empty
        if (board[index] != 0) {
            return null;
        }

        // Validate if placing this piece violates the double free three rule
        if (detectDoubleFreeThrees(index, BOARD_SIZE, piece, board)) {
            return null;
        }

        // Validate if placing such a piece will capture an opponent
        List<Boolean> capturedValidationRes = new ArrayList<>();
        List<Function<Integer, Integer>> fnMappings = List.of(
                gomokuUtils::getBtmIdx,
                gomokuUtils::getTopIdx,
                gomokuUtils::getLeftIdx,
                gomokuUtils::getRightIdx,
                gomokuUtils::getBtmLeftIdx,
                gomokuUtils::getTopRightIdx,
                gomokuUtils::getTopLeftIdx,
                gomokuUtils::getBtmRightIdx
        );

        // Check for captures in all 8 directions
        for (Function<Integer, Integer> fnMapping : fnMappings) {
            capturedValidationRes.add(checkCaptureMadeDir(fnMapping, index, BOARD_SIZE, piece, board));
        }

        List<Integer> weCapturedIndices = new ArrayList<>();
        for (int i = 0; i < capturedValidationRes.size(); i++) {
            if (capturedValidationRes.get(i)) {
                weCapturedIndices.add(i);
            }
        }

        // If we captured opponent pieces
        if (!weCapturedIndices.isEmpty()) {
            byte[] newBoard = board.clone();
            newBoard[index] = piece; // Place the piece

            int newP1Captures = (int) state.getP1Captures();
            int newP2Captures = (int) state.getP2Captures();

            // Process each captured piece
            for (int weCapturedIdx : weCapturedIndices) {
                // Determine the direction of capture
                Function<Integer, Integer> fnMapping = fnMappings.get(weCapturedIdx);
                int idx1 = fnMapping.apply(index);
                int idx2 = fnMapping.apply(idx1);

                newBoard[idx1] = 0; // Remove captured piece
                newBoard[idx2] = 0;

                if (piece == (byte) 1) {
                    newP1Captures++;
                } else {
                    newP2Captures++;
                }
            }

            // Create the new game state
            GameOuterClass.GameState gameState = GameOuterClass.GameState.newBuilder()
                    .setBoard(ByteString.copyFrom(newBoard))
                    .setP1Captures(newP1Captures)
                    .setP2Captures(newP2Captures)
                    .setNumTurns(state.getNumTurns() + 1)
                    .build();

            // Check for win condition
            int isEnd = 0;
            if (piece == (byte) 1 && StaticEvaluation.checkWinCondition(BOARD_SIZE, gameState, 1, newP1Captures)) {
                isEnd = 1;
            }
            if (piece == (byte) 2 && StaticEvaluation.checkWinCondition(BOARD_SIZE, gameState, 2, newP2Captures)) {
                isEnd = 2;
            }

            gameState = gameState.toBuilder().setIsEnd(isEnd).build();
            return gameState;
        }

        // If no captures were made, place the piece in the empty space
        byte[] newBoard = board.clone();
        newBoard[index] = piece;

        GameOuterClass.GameState newGameState = GameOuterClass.GameState.newBuilder()
                .setBoard(ByteString.copyFrom(newBoard))
                .setP1Captures(state.getP1Captures())
                .setP2Captures(state.getP2Captures())
                .setNumTurns(state.getNumTurns() + 1)
                .build();

        // Check for win condition
        int isEnd = 0;
        if (piece == (byte) 1 && StaticEvaluation.checkWinCondition(BOARD_SIZE, newGameState, 1, (int) state.getP1Captures())) {
            isEnd = 1;
        }
        if (piece == (byte) 2 && StaticEvaluation.checkWinCondition(BOARD_SIZE, newGameState, 2, (int) state.getP2Captures())) {
            isEnd = 2;
        }

        newGameState = newGameState.toBuilder().setIsEnd(isEnd).build();
        return newGameState;
    }

    public List<GameOuterClass.GameState> generatePossibleMoves(GameOuterClass.GameState state, int boardSize, byte piece, boolean filterEndMoves) {
        byte[] currBoard = state.getBoard().toByteArray(); // Assuming `getBoard()` returns a 1D array representation
        int dims = boardSize * boardSize;
        List<GameOuterClass.GameState> result = new ArrayList<>();
        Set<Integer> initialSearchIndices = new HashSet<>();
        Set<Integer> threatSearchIndices = new HashSet<>();

        // Check if the game is already in an end state
        if (state.getIsEnd() != 0) {
            return result;
        }

        // Identify possible cells for moves
        for (int i = 0; i < dims; i++) {
            if (currBoard[i] == 0) {
                continue;
            }

            // Get all indices in a 2-cell range in all directions
            List<Integer> directionalIndices = expandAllDirections(i, 2).stream().flatMap(List::stream)
            .collect(Collectors.toList());
            for (Integer val : directionalIndices) {
                if (currBoard[val] != 0) {
                    continue;
                }

                initialSearchIndices.add(val);

                // Add to threat indices if placing here forms/blocks a threat
                if (hasThreat(val, boardSize, piece, currBoard)) {
                    threatSearchIndices.add(val);
                }
            }
        }

        // Use threat indices if available; otherwise, use initial search indices
        Set<Integer> indicesToCheck = !threatSearchIndices.isEmpty() ? threatSearchIndices : initialSearchIndices;

        for (int i : indicesToCheck) {
            GameOuterClass.GameState newState = placePieceAttempt(i, piece, state, boardSize, true); // Assuming ignoreSelfCaptured is true
            if (newState != null) {
                 result.add(newState);
            }
        }

        // Filter for winning moves if required
        if (filterEndMoves) {
            List<GameOuterClass.GameState> winningMoves = new ArrayList<>();
            for (GameOuterClass.GameState move : result) {
                if (move.getIsEnd() == piece) {
                    winningMoves.add(move);
                }
            }
            if (!winningMoves.isEmpty()) {
                return winningMoves;
            }
        }

        return result;
    }

    public List<List<Object>> generateMoveTree(GameOuterClass.GameState state, int boardSize, byte piece, int depth) {
        List<List<Object>> result = new ArrayList<>();

        for (int i = 0; i < depth; i++) {
            byte currPiece = (i % 2 == 0) ? piece : (byte) (piece ==  (byte) 1 ? (byte) 2 : (byte) 1);

            // Generate first depth
            if (result.isEmpty()) {
                List<GameOuterClass.GameState> rootChildren = generatePossibleMoves(state, boardSize, currPiece, true);
                result.add(Arrays.asList(state, rootChildren));

                for (GameOuterClass.GameState child : rootChildren) {
                    result.add(Arrays.asList(child, null));
                }
            } else {
                List<List<GameOuterClass.GameState>> newLeaves = new ArrayList<>();

                // Find leaves and generate their children
                for (int j = 0; j < result.size(); j++) {
                    List<Object> node = result.get(j);
                    if (node.get(1) == null) {
                        GameOuterClass.GameState leafState = (GameOuterClass.GameState) node.get(0);
                        List<GameOuterClass.GameState> leafChildren = generatePossibleMoves(leafState, boardSize, currPiece, true);
                        node.set(1, leafChildren);
                        newLeaves.add(leafChildren);
                    }
                }

                // Add new leaves to the result
                for (List<GameOuterClass.GameState> leafList : newLeaves) {
                    for (GameOuterClass.GameState leaf : leafList) {
                        result.add(Arrays.asList(leaf, null));
                    }
                }
            }
        }

        return result;
    }
}
