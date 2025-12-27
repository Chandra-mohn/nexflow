# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Date Context Functions Generator Mixin

Generates date context functions for NexflowRuntime.java (v0.7.0+):
- processingDate(): System time when record is processed
- businessDate(): Business date from calendar context
- businessDateOffset(): Business date plus/minus offset days
- isBusinessDay(): Check if date is a business day

MOCK: Weekend skipping only. Replace with BusinessCalendarService for holidays.
"""


class DateContextMixin:
    """Mixin for generating date context runtime functions."""

    def _generate_date_context_functions(self) -> str:
        """Generate date context functions for process-level date access (v0.7.0+)."""
        return '''    // =========================================================================
    // Date Context Functions (v0.7.0+)
    // MOCK: Skips weekends only. Replace with BusinessCalendarService for holidays.
    // =========================================================================

    /**
     * Get the processing date - the system time when the record is being processed.
     *
     * This function captures the current system time when called, representing
     * when the record enters the processing pipeline. Unlike business_date which
     * comes from a business calendar, processing_date is always the wall-clock time.
     *
     * In DSL:
     *   processing_date auto
     *   ...
     *   posting_timestamp = processing_date()
     *
     * @param context The execution context (provides access to system clock)
     * @return Current processing timestamp as Instant
     */
    public static Instant processingDate(Object context) {
        // When context is available and has a configured clock, use that
        // Otherwise fall back to system clock
        return Instant.now();
    }

    /**
     * Get the business date from the calendar context.
     *
     * This function retrieves the business date from the process execution context.
     * The business date is determined by the business calendar configuration
     * (e.g., trading_calendar) and represents when the transaction will be
     * posted for accounting/settlement purposes.
     *
     * MOCK: Returns current date, adjusted to next Monday if weekend.
     * Replace with actual BusinessCalendarService integration for holidays.
     *
     * In DSL:
     *   business_date from trading_calendar
     *   ...
     *   settlement_date = business_date()
     *
     * @param context The execution context (provides access to business calendar)
     * @return Current business date as LocalDate
     */
    public static LocalDate businessDate(Object context) {
        // MOCK: Returns current date, skipping weekends
        // Replace with actual BusinessCalendarService integration
        LocalDate today = LocalDate.now();
        DayOfWeek dow = today.getDayOfWeek();
        if (dow == DayOfWeek.SATURDAY) {
            return today.plusDays(2); // Move to Monday
        } else if (dow == DayOfWeek.SUNDAY) {
            return today.plusDays(1); // Move to Monday
        }
        return today;
    }

    /**
     * Get the business date plus/minus offset days.
     *
     * Useful for calculating settlement dates, value dates, etc.
     * Skips weekends when calculating offset.
     *
     * MOCK: Skips weekends only. Replace with BusinessCalendarService for holidays.
     *
     * In DSL:
     *   t_plus_2 = business_date_offset(2)  // T+2 settlement
     *
     * @param context The execution context
     * @param offsetDays Number of business days to add (can be negative)
     * @return Business date offset by specified business days
     */
    public static LocalDate businessDateOffset(Object context, int offsetDays) {
        LocalDate date = businessDate(context);
        // MOCK: Skip weekends only
        // Replace with actual BusinessCalendarService for holidays
        int direction = offsetDays >= 0 ? 1 : -1;
        int remaining = Math.abs(offsetDays);

        while (remaining > 0) {
            date = date.plusDays(direction);
            DayOfWeek dow = date.getDayOfWeek();
            if (dow != DayOfWeek.SATURDAY && dow != DayOfWeek.SUNDAY) {
                remaining--;
            }
        }
        return date;
    }

    /**
     * Check if a date is a business day (not weekend).
     *
     * MOCK: Checks weekends only. Replace with BusinessCalendarService for holidays.
     *
     * @param date The date to check
     * @return true if business day, false if weekend
     */
    public static boolean isBusinessDay(LocalDate date) {
        // MOCK: Check weekends only
        // Replace with actual BusinessCalendarService for holidays
        if (date == null) return false;
        DayOfWeek dow = date.getDayOfWeek();
        return dow != DayOfWeek.SATURDAY && dow != DayOfWeek.SUNDAY;
    }'''
