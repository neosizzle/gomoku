package org.gomoku;

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
}
