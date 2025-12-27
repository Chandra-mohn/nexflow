# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
String Functions Generator Mixin

Generates string-related functions for NexflowRuntime.java:
- upper(), lower(), trim(), length(), concat()
- substring(), startsWith(), endsWith(), contains()
- replace(), isEmpty(), isBlank()
"""


class StringFunctionsMixin:
    """Mixin for generating string runtime functions."""

    def _generate_string_functions(self) -> str:
        """Generate string functions."""
        return '''    // =========================================================================
    // String Functions
    // =========================================================================

    /**
     * Convert string to uppercase.
     *
     * @param str The input string
     * @return Uppercase string, or null if input is null
     */
    public static String upper(String str) {
        return str == null ? null : str.toUpperCase();
    }

    /**
     * Convert string to lowercase.
     *
     * @param str The input string
     * @return Lowercase string, or null if input is null
     */
    public static String lower(String str) {
        return str == null ? null : str.toLowerCase();
    }

    /**
     * Trim whitespace from both ends of a string.
     *
     * @param str The input string
     * @return Trimmed string, or null if input is null
     */
    public static String trim(String str) {
        return str == null ? null : str.trim();
    }

    /**
     * Get the length of a string.
     *
     * @param str The input string
     * @return Length of string, or 0 if null
     */
    public static int length(String str) {
        return str == null ? 0 : str.length();
    }

    /**
     * Concatenate multiple strings.
     *
     * @param parts The strings to concatenate
     * @return Concatenated string (null parts are treated as empty)
     */
    public static String concat(String... parts) {
        if (parts == null) return null;
        StringBuilder sb = new StringBuilder();
        for (String part : parts) {
            if (part != null) sb.append(part);
        }
        return sb.toString();
    }

    /**
     * Get a substring.
     *
     * @param str The input string
     * @param start Start index (0-based)
     * @param end End index (exclusive)
     * @return Substring, or null if input is null
     */
    public static String substring(String str, int start, int end) {
        if (str == null) return null;
        int actualEnd = Math.min(end, str.length());
        int actualStart = Math.max(0, Math.min(start, actualEnd));
        return str.substring(actualStart, actualEnd);
    }

    /**
     * Get a substring from start to end.
     *
     * @param str The input string
     * @param start Start index (0-based)
     * @return Substring from start to end, or null if input is null
     */
    public static String substring(String str, int start) {
        if (str == null) return null;
        int actualStart = Math.max(0, Math.min(start, str.length()));
        return str.substring(actualStart);
    }

    /**
     * Check if a string starts with a prefix.
     *
     * @param str The input string
     * @param prefix The prefix to check
     * @return true if str starts with prefix, false otherwise
     */
    public static boolean startsWith(String str, String prefix) {
        if (str == null || prefix == null) return false;
        return str.startsWith(prefix);
    }

    /**
     * Check if a string ends with a suffix.
     *
     * @param str The input string
     * @param suffix The suffix to check
     * @return true if str ends with suffix, false otherwise
     */
    public static boolean endsWith(String str, String suffix) {
        if (str == null || suffix == null) return false;
        return str.endsWith(suffix);
    }

    /**
     * Check if a string contains a substring.
     *
     * @param str The input string
     * @param substring The substring to search for
     * @return true if str contains substring, false otherwise
     */
    public static boolean contains(String str, String substring) {
        if (str == null || substring == null) return false;
        return str.contains(substring);
    }

    /**
     * Replace all occurrences of a pattern in a string.
     *
     * @param str The input string
     * @param oldValue The pattern to replace
     * @param newValue The replacement
     * @return String with replacements, or null if input is null
     */
    public static String replace(String str, String oldValue, String newValue) {
        if (str == null) return null;
        if (oldValue == null) return str;
        return str.replace(oldValue, newValue == null ? "" : newValue);
    }

    /**
     * Check if a string is null or empty.
     *
     * @param str The input string
     * @return true if str is null or empty, false otherwise
     */
    public static boolean isEmpty(String str) {
        return str == null || str.isEmpty();
    }

    /**
     * Check if a string is null, empty, or contains only whitespace.
     *
     * @param str The input string
     * @return true if str is null, empty, or blank, false otherwise
     */
    public static boolean isBlank(String str) {
        return str == null || str.trim().isEmpty();
    }'''
