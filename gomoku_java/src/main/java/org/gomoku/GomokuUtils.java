package org.gomoku;

import game.GameOuterClass;

import java.util.List;

public class GomokuUtils {
    private final int BOARD_SIZE;
    GomokuUtils(int board_size) {
        this.BOARD_SIZE = board_size;
    }

    public int getTopIdx(int idx) {
        if (idx < BOARD_SIZE) {
            return -1;
        }
        return idx - BOARD_SIZE;
    }

    // Get bottom index (downward move)
    public int getBtmIdx(int idx) {
        int dim = BOARD_SIZE * BOARD_SIZE;
        if (idx > (dim - BOARD_SIZE - 1)) {
            return -1;
        }
        return idx + BOARD_SIZE;
    }

    // Get left index (leftward move)
    public int getLeftIdx(int idx) {
        if (idx % BOARD_SIZE == 0) {
            return -1;
        }
        return idx - 1;
    }

    // Get right index (rightward move)
    public int getRightIdx(int idx) {
        if ((idx + 1) % BOARD_SIZE == 0) {
            return -1;
        }
        return idx + 1;
    }

    public int getTopLeftIdx(int idx) {
        int top = getTopIdx(idx);
        if (top == -1) {
            return -1;
        }
        return getLeftIdx(top);
    }

    public int getBtmLeftIdx(int idx) {
        int btm = getBtmIdx(idx);
        if (btm == -1) {
            return -1;
        }
        return getLeftIdx(btm);
    }

    public int getTopRightIdx(int idx) {
        int top = getTopIdx(idx);
        if (top == -1) {
            return -1;
        }
        return getRightIdx(top);
    }

    public int getBtmRightIdx(int idx) {
        int btm = getBtmIdx(idx);
        if (btm == -1) {
            return -1;
        }
        return getRightIdx(btm);
    }
    public void prettyPrintBoard(byte[] buffer) {
        int counter = 0;
        for (byte b : buffer) {
            System.out.print(" " + (int) b + " ");
            counter++;
            if (counter == BOARD_SIZE) {
                System.out.println();
                counter = 0;
            }
        }
    }

    public void prettyPrintBoardIndent(byte[] buffer, int indentCount) {
        int counter = 0;
        String indent = " ".repeat(indentCount * 2);  // Calculate the indent
        System.out.print(indent);  // Print initial indent

        for (byte b : buffer) {
            System.out.print(" " + (int) b + " ");
            counter++;
            if (counter == BOARD_SIZE) {
                System.out.println();
                System.out.print(indent);  // Print indent for next row
                counter = 0;
            }
        }
    }
    public record GameStateNode(game.GameOuterClass.GameState state, List<GameOuterClass.GameState> children) {
    }
}
