"""
Metadata Generator Mixin

Generates Java code for L3 Transform metadata (version, description, compatibility).
"""

from typing import Set

from backend.ast import transform_ast as ast


class MetadataGeneratorMixin:
    """
    Mixin for generating Java metadata constants for transforms.

    Generates:
    - Version constants (TRANSFORM_VERSION)
    - Description constants (TRANSFORM_DESCRIPTION)
    - Compatibility mode constants
    - Previous version tracking
    """

    def generate_metadata_constants(
        self,
        metadata: ast.TransformMetadata,
        transform_name: str
    ) -> str:
        """Generate Java constants for transform metadata.

        Args:
            metadata: The transform metadata AST node
            transform_name: Name of the transform

        Returns:
            Java code declaring metadata constants
        """
        if not metadata:
            return ""

        lines = [
            "    // Transform Metadata Constants",
        ]

        # Version constant
        if metadata.version:
            lines.append(
                f'    public static final String TRANSFORM_VERSION = "{metadata.version}";'
            )

        # Previous version constant (for migration tracking)
        if metadata.previous_version:
            lines.append(
                f'    public static final String PREVIOUS_VERSION = "{metadata.previous_version}";'
            )

        # Description constant
        if metadata.description:
            # Escape quotes in description
            desc = metadata.description.replace('"', '\\"')
            lines.append(
                f'    public static final String TRANSFORM_DESCRIPTION = "{desc}";'
            )

        # Compatibility mode constant
        if metadata.compatibility:
            compat_value = metadata.compatibility.value.upper()
            lines.append(
                f'    public static final CompatibilityMode COMPATIBILITY_MODE = '
                f'CompatibilityMode.{compat_value};'
            )

        # Add blank line if we generated any constants
        if len(lines) > 1:
            lines.append("")

        return '\n'.join(lines)

    def generate_compatibility_enum(self) -> str:
        """Generate CompatibilityMode enum for transform compatibility."""
        return '''    /**
     * Compatibility mode for transform versioning.
     */
    public enum CompatibilityMode {
        /** New version can read old data */
        BACKWARD,
        /** Old version can read new data */
        FORWARD,
        /** Both backward and forward compatible */
        FULL,
        /** No compatibility guarantees */
        NONE
    }'''

    def generate_version_check_method(
        self,
        metadata: ast.TransformMetadata
    ) -> str:
        """Generate version compatibility check method.

        Args:
            metadata: The transform metadata AST node

        Returns:
            Java method for checking version compatibility
        """
        if not metadata or not metadata.version:
            return ""

        lines = [
            "    /**",
            "     * Check if this transform version is compatible with the given version.",
            "     *",
            "     * @param otherVersion The version to check compatibility against",
            "     * @return true if compatible, false otherwise",
            "     */",
            "    public boolean isCompatibleWith(String otherVersion) {",
        ]

        if metadata.compatibility:
            compat = metadata.compatibility.value
            if compat == "full":
                lines.append("        // Full compatibility - always compatible")
                lines.append("        return true;")
            elif compat == "none":
                lines.append("        // No compatibility - only exact match")
                lines.append("        return TRANSFORM_VERSION.equals(otherVersion);")
            elif compat == "backward":
                lines.extend([
                    "        // Backward compatible - can read older versions",
                    "        return compareVersions(TRANSFORM_VERSION, otherVersion) >= 0;",
                ])
            elif compat == "forward":
                lines.extend([
                    "        // Forward compatible - older versions can read this",
                    "        return compareVersions(TRANSFORM_VERSION, otherVersion) <= 0;",
                ])
        else:
            lines.append("        // Default: exact version match")
            lines.append("        return TRANSFORM_VERSION.equals(otherVersion);")

        lines.append("    }")

        return '\n'.join(lines)

    def generate_version_compare_helper(self) -> str:
        """Generate helper method for semantic version comparison."""
        return '''    /**
     * Compare two semantic versions.
     *
     * @param v1 First version (e.g., "1.2.3")
     * @param v2 Second version (e.g., "1.2.0")
     * @return negative if v1 < v2, zero if equal, positive if v1 > v2
     */
    private static int compareVersions(String v1, String v2) {
        String[] parts1 = v1.split("\\\\.");
        String[] parts2 = v2.split("\\\\.");

        for (int i = 0; i < Math.max(parts1.length, parts2.length); i++) {
            int p1 = i < parts1.length ? Integer.parseInt(parts1[i]) : 0;
            int p2 = i < parts2.length ? Integer.parseInt(parts2[i]) : 0;
            if (p1 != p2) {
                return p1 - p2;
            }
        }
        return 0;
    }'''

    def generate_metadata_javadoc(
        self,
        metadata: ast.TransformMetadata,
        transform_name: str
    ) -> str:
        """Generate Javadoc section with metadata info.

        Args:
            metadata: The transform metadata AST node
            transform_name: Name of the transform

        Returns:
            Javadoc lines with metadata information
        """
        lines = []

        if metadata:
            if metadata.version:
                lines.append(f" * @version {metadata.version}")
            if metadata.description:
                lines.append(f" * <p>{metadata.description}</p>")
            if metadata.compatibility:
                lines.append(
                    f" * @compatibility {metadata.compatibility.value}"
                )
            if metadata.previous_version:
                lines.append(
                    f" * @previousVersion {metadata.previous_version}"
                )

        return '\n'.join(lines)

    def has_compatibility_features(
        self,
        metadata: ast.TransformMetadata
    ) -> bool:
        """Check if metadata has compatibility features requiring enum generation."""
        return metadata is not None and metadata.compatibility is not None

    def has_version_features(
        self,
        metadata: ast.TransformMetadata
    ) -> bool:
        """Check if metadata has version features requiring version comparison."""
        return (
            metadata is not None and
            metadata.version is not None and
            (metadata.compatibility is not None or metadata.previous_version is not None)
        )

    def get_metadata_imports(self) -> Set[str]:
        """Get required imports for metadata generation."""
        # No special imports needed for basic metadata constants
        return set()
