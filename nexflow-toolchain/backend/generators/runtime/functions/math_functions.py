# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Math Functions Generator Mixin

Generates math-related functions for NexflowRuntime.java:
- abs(), min(), max(), round(), ceil(), floor()
- pow(), percentOf()
"""


class MathFunctionsMixin:
    """Mixin for generating math runtime functions."""

    def _generate_math_functions(self) -> str:
        """Generate math functions."""
        return '''    // =========================================================================
    // Math Functions
    // =========================================================================

    /**
     * Get the absolute value of a BigDecimal.
     *
     * @param value The value
     * @return Absolute value, or null if input is null
     */
    public static BigDecimal abs(BigDecimal value) {
        return value == null ? null : value.abs();
    }

    /**
     * Get the absolute value of a Long.
     *
     * @param value The value
     * @return Absolute value, or null if input is null
     */
    public static Long abs(Long value) {
        return value == null ? null : Math.abs(value);
    }

    /**
     * Get the minimum of two comparable values.
     *
     * @param a First value
     * @param b Second value
     * @return Minimum value (null values are ignored unless both are null)
     */
    public static <T extends Comparable<T>> T min(T a, T b) {
        if (a == null) return b;
        if (b == null) return a;
        return a.compareTo(b) <= 0 ? a : b;
    }

    /**
     * Get the maximum of two comparable values.
     *
     * @param a First value
     * @param b Second value
     * @return Maximum value (null values are ignored unless both are null)
     */
    public static <T extends Comparable<T>> T max(T a, T b) {
        if (a == null) return b;
        if (b == null) return a;
        return a.compareTo(b) >= 0 ? a : b;
    }

    /**
     * Round a BigDecimal to specified decimal places.
     *
     * @param value The value to round
     * @param decimalPlaces Number of decimal places
     * @return Rounded value, or null if input is null
     */
    public static BigDecimal round(BigDecimal value, int decimalPlaces) {
        if (value == null) return null;
        return value.setScale(decimalPlaces, RoundingMode.HALF_UP);
    }

    /**
     * Round a BigDecimal to integer (0 decimal places).
     *
     * @param value The value to round
     * @return Rounded value, or null if input is null
     */
    public static BigDecimal round(BigDecimal value) {
        return round(value, 0);
    }

    /**
     * Get the ceiling of a BigDecimal (round up to integer).
     *
     * @param value The value
     * @return Ceiling value, or null if input is null
     */
    public static BigDecimal ceil(BigDecimal value) {
        if (value == null) return null;
        return value.setScale(0, RoundingMode.CEILING);
    }

    /**
     * Get the floor of a BigDecimal (round down to integer).
     *
     * @param value The value
     * @return Floor value, or null if input is null
     */
    public static BigDecimal floor(BigDecimal value) {
        if (value == null) return null;
        return value.setScale(0, RoundingMode.FLOOR);
    }

    /**
     * Calculate the power of a BigDecimal.
     *
     * @param base The base value
     * @param exponent The exponent (must be non-negative integer)
     * @return base raised to exponent, or null if base is null
     */
    public static BigDecimal pow(BigDecimal base, int exponent) {
        if (base == null) return null;
        return base.pow(exponent);
    }

    /**
     * Calculate percentage of a value.
     *
     * @param value The base value
     * @param percentage The percentage (e.g., 10 for 10%)
     * @return Calculated percentage, or null if value is null
     */
    public static BigDecimal percentOf(BigDecimal value, BigDecimal percentage) {
        if (value == null || percentage == null) return null;
        return value.multiply(percentage).divide(new BigDecimal("100"), 10, RoundingMode.HALF_UP);
    }'''
