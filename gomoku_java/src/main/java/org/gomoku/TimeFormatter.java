package org.gomoku;

import java.math.RoundingMode;
import java.text.DecimalFormat;

public class TimeFormatter {

    public static String formatTime(long nanoseconds) {
        // Constants
        final long MINUTE = 60L * 1_000_000_000L;   // 1 minute in nanoseconds
        final long SECOND = 1_000_000_000L;          // 1 second in nanoseconds
        final long MILLISECOND = 1_000_000L;         // 1 millisecond in nanoseconds
        final long MICROSECOND = 1_000L;             // 1 microsecond in nanoseconds

        // Decimal format for rounding
        DecimalFormat df = new DecimalFormat("#");
        df.setRoundingMode(RoundingMode.CEILING);

        // return nanoseconds + " nanosecond" + (nanoseconds > 1 ? "s" : "");

        if (nanoseconds >= MINUTE) {
            // Convert to minutes and round up
            long minutes = (long) Math.ceil((double) nanoseconds / MINUTE);
            return minutes + " minute" + (minutes > 1 ? "s" : "");
        } else if (nanoseconds >= SECOND) {
            // Convert to seconds and round up
            long seconds = (long) Math.ceil((double) nanoseconds / SECOND);
            return seconds + " second" + (seconds > 1 ? "s" : "");
        } else if (nanoseconds >= MILLISECOND) {
            // Convert to milliseconds and round up
            long milliseconds = (long) Math.ceil((double) nanoseconds / MILLISECOND);
            return milliseconds + " millisecond" + (milliseconds > 1 ? "s" : "");
        } else if (nanoseconds >= MICROSECOND) {
            // Convert to microseconds and round up
            long microseconds = (long) Math.ceil((double) nanoseconds / MICROSECOND);
            return microseconds + " microsecond" + (microseconds > 1 ? "s" : "");
        } else {
            // Return the value in nanoseconds if it's too small
            return nanoseconds + " nanosecond" + (nanoseconds > 1 ? "s" : "");
        }
    }
}
