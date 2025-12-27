# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Time Functions Generator Mixin

Generates time-related functions for NexflowRuntime.java:
- hour(), dayOfWeek(), dayOfMonth(), month(), year()
- now(), today(), daysBetween(), addDays()
"""


class TimeFunctionsMixin:
    """Mixin for generating time-related runtime functions."""

    def _generate_time_functions(self) -> str:
        """Generate time-related functions."""
        return '''    // =========================================================================
    // Time Functions
    // =========================================================================

    /**
     * Extract the hour (0-23) from a timestamp.
     *
     * @param timestamp The timestamp to extract hour from
     * @return Hour of day (0-23), or -1 if timestamp is null
     */
    public static int hour(Instant timestamp) {
        if (timestamp == null) return -1;
        return timestamp.atZone(ZoneOffset.UTC).getHour();
    }

    /**
     * Extract the hour (0-23) from a LocalDateTime.
     *
     * @param dateTime The datetime to extract hour from
     * @return Hour of day (0-23), or -1 if dateTime is null
     */
    public static int hour(LocalDateTime dateTime) {
        if (dateTime == null) return -1;
        return dateTime.getHour();
    }

    /**
     * Extract the day of week (1=Monday, 7=Sunday) from a timestamp.
     * Follows ISO-8601 standard where Monday is 1.
     *
     * @param timestamp The timestamp to extract day of week from
     * @return Day of week (1-7), or -1 if timestamp is null
     */
    public static int dayOfWeek(Instant timestamp) {
        if (timestamp == null) return -1;
        return timestamp.atZone(ZoneOffset.UTC).getDayOfWeek().getValue();
    }

    /**
     * Extract the day of week (1=Monday, 7=Sunday) from a LocalDate.
     *
     * @param date The date to extract day of week from
     * @return Day of week (1-7), or -1 if date is null
     */
    public static int dayOfWeek(LocalDate date) {
        if (date == null) return -1;
        return date.getDayOfWeek().getValue();
    }

    /**
     * Extract the day of month (1-31) from a timestamp.
     *
     * @param timestamp The timestamp to extract day from
     * @return Day of month (1-31), or -1 if timestamp is null
     */
    public static int dayOfMonth(Instant timestamp) {
        if (timestamp == null) return -1;
        return timestamp.atZone(ZoneOffset.UTC).getDayOfMonth();
    }

    /**
     * Extract the month (1-12) from a timestamp.
     *
     * @param timestamp The timestamp to extract month from
     * @return Month (1-12), or -1 if timestamp is null
     */
    public static int month(Instant timestamp) {
        if (timestamp == null) return -1;
        return timestamp.atZone(ZoneOffset.UTC).getMonthValue();
    }

    /**
     * Extract the year from a timestamp.
     *
     * @param timestamp The timestamp to extract year from
     * @return Year, or -1 if timestamp is null
     */
    public static int year(Instant timestamp) {
        if (timestamp == null) return -1;
        return timestamp.atZone(ZoneOffset.UTC).getYear();
    }

    /**
     * Get the current timestamp (UTC).
     *
     * @return Current instant in UTC
     */
    public static Instant now() {
        return Instant.now();
    }

    /**
     * Get the current date (UTC).
     *
     * @return Current date in UTC
     */
    public static LocalDate today() {
        return LocalDate.now(ZoneOffset.UTC);
    }

    /**
     * Calculate days between two dates.
     *
     * @param from Start date
     * @param to End date
     * @return Number of days between dates, or 0 if either is null
     */
    public static long daysBetween(LocalDate from, LocalDate to) {
        if (from == null || to == null) return 0;
        return ChronoUnit.DAYS.between(from, to);
    }

    /**
     * Calculate days between two timestamps.
     *
     * @param from Start timestamp
     * @param to End timestamp
     * @return Number of days between timestamps, or 0 if either is null
     */
    public static long daysBetween(Instant from, Instant to) {
        if (from == null || to == null) return 0;
        return ChronoUnit.DAYS.between(from, to);
    }

    /**
     * Add days to a date.
     *
     * @param date The base date
     * @param days Number of days to add (can be negative)
     * @return New date with days added, or null if date is null
     */
    public static LocalDate addDays(LocalDate date, long days) {
        if (date == null) return null;
        return date.plusDays(days);
    }

    /**
     * Add days to a timestamp.
     *
     * @param timestamp The base timestamp
     * @param days Number of days to add (can be negative)
     * @return New timestamp with days added, or null if timestamp is null
     */
    public static Instant addDays(Instant timestamp, long days) {
        if (timestamp == null) return null;
        return timestamp.plus(days, ChronoUnit.DAYS);
    }'''
