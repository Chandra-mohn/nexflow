# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow Project Configuration

Handles nexflow.toml manifest parsing and project structure.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import toml


class ProjectError(Exception):
    """Error related to project configuration or structure."""
    pass


# DSL language extensions and their layer mapping
DSL_EXTENSIONS = {
    ".proc": "flow",        # L1 - Process Orchestration
    ".flow": "flow",        # L1 - Process Orchestration (alternate)
    ".schema": "schema",    # L2 - Schema Registry
    ".xform": "transform",  # L3 - Transform Catalog
    ".transform": "transform",  # L3 - Transform Catalog (alternate)
    ".rules": "rules",      # L4 - Business Rules
    ".infra": "infra",      # L5 - Infrastructure Binding
}

# Default directory structure
DEFAULT_SRC_DIRS = {
    "flow": "src/flow",
    "schema": "src/schema",
    "transform": "src/transform",
    "rules": "src/rules",
    "infra": "src/infra",   # L5 - Infrastructure files
}


@dataclass
class SourceConfig:
    """Source directory configuration for a DSL type."""
    path: str
    include: List[str] = field(default_factory=lambda: ["**/*"])
    exclude: List[str] = field(default_factory=list)


@dataclass
class TargetConfig:
    """Code generation target configuration."""
    name: str
    output: str
    enabled: bool = True
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Project:
    """Nexflow project configuration."""
    name: str
    version: str
    root_dir: Path
    src_dir: Path
    output_dir: Path
    targets: List[str]
    sources: Dict[str, SourceConfig]
    target_configs: Dict[str, TargetConfig]
    dependencies: List[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Project":
        """Load project from nexflow.toml."""
        if path is None:
            path = cls._find_project_root()

        config_file = path / "nexflow.toml"
        if not config_file.exists():
            raise ProjectError(
                f"No nexflow.toml found in {path}. "
                "Run 'nexflow init' to create a project."
            )

        try:
            config = toml.load(config_file)
        except Exception as e:
            raise ProjectError(f"Failed to parse nexflow.toml: {e}")

        return cls._from_config(config, path)

    @classmethod
    def _find_project_root(cls) -> Path:
        """Find project root by looking for nexflow.toml."""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "nexflow.toml").exists():
                return parent
        return current  # Default to current directory

    @classmethod
    def _from_config(cls, config: Dict[str, Any], root_dir: Path) -> "Project":
        """Create Project from parsed TOML config."""
        # Project metadata
        project_config = config.get("project", {})
        name = project_config.get("name", root_dir.name)
        version = project_config.get("version", "0.1.0")

        # Paths
        paths_config = config.get("paths", {})
        src_dir = root_dir / paths_config.get("src", "src")
        output_dir = root_dir / paths_config.get("output", "generated")

        # Sources
        sources_config = config.get("sources", {})
        sources = {}
        for lang in DSL_EXTENSIONS.values():
            if lang in sources_config:
                src_cfg = sources_config[lang]
                sources[lang] = SourceConfig(
                    path=src_cfg.get("path", DEFAULT_SRC_DIRS.get(lang, f"src/{lang}")),
                    include=src_cfg.get("include", ["**/*"]),
                    exclude=src_cfg.get("exclude", []),
                )
            else:
                # Use defaults
                sources[lang] = SourceConfig(
                    path=DEFAULT_SRC_DIRS.get(lang, f"src/{lang}")
                )

        # Targets
        targets_config = config.get("targets", {})
        targets = []
        target_configs = {}

        for target_name in ["flink", "spark"]:
            if target_name in targets_config:
                t_cfg = targets_config[target_name]
                enabled = t_cfg.get("enabled", True)
                if enabled:
                    targets.append(target_name)
                target_configs[target_name] = TargetConfig(
                    name=target_name,
                    output=t_cfg.get("output", f"generated/{target_name}"),
                    enabled=enabled,
                    options=t_cfg.get("options", {}),
                )
            else:
                # Default: flink enabled, spark disabled
                enabled = target_name == "flink"
                if enabled:
                    targets.append(target_name)
                target_configs[target_name] = TargetConfig(
                    name=target_name,
                    output=f"generated/{target_name}",
                    enabled=enabled,
                )

        # Dependencies
        dependencies = config.get("dependencies", [])

        return cls(
            name=name,
            version=version,
            root_dir=root_dir,
            src_dir=src_dir,
            output_dir=output_dir,
            targets=targets,
            sources=sources,
            target_configs=target_configs,
            dependencies=dependencies,
        )

    @property
    def file_counts(self) -> Dict[str, int]:
        """Count DSL files by type."""
        counts = {}
        # Use shorthand extensions: .proc, .xform, .infra
        for lang, ext in [("flow", ".proc"), ("schema", ".schema"),
                          ("transform", ".xform"), ("rules", ".rules"),
                          ("infra", ".infra")]:
            src_config = self.sources.get(lang)
            if src_config:
                src_path = self.root_dir / src_config.path
                if src_path.exists():
                    counts[lang] = len(list(src_path.rglob(f"*{ext}")))
                else:
                    counts[lang] = 0
            else:
                counts[lang] = 0
        return counts

    def get_source_files(self, lang: str) -> List[Path]:
        """Get all source files for a DSL language."""
        src_config = self.sources.get(lang)
        if not src_config:
            return []

        # Map language to file extension (using shorthand extensions)
        ext_map = {"flow": ".proc", "schema": ".schema",
                   "transform": ".xform", "rules": ".rules",
                   "infra": ".infra"}
        ext = ext_map.get(lang)
        if not ext:
            return []

        src_path = self.root_dir / src_config.path
        if not src_path.exists():
            return []

        files = []
        for pattern in src_config.include:
            files.extend(src_path.rglob(f"{pattern}{ext}"))

        # Apply exclusions
        for exclude_pattern in src_config.exclude:
            files = [f for f in files if not f.match(exclude_pattern)]

        return sorted(files)

    def get_all_source_files(self) -> Dict[str, List[Path]]:
        """Get all source files organized by language."""
        return {
            lang: self.get_source_files(lang)
            for lang in DSL_EXTENSIONS.values()
        }

    def get_output_path(self, target: str) -> Path:
        """Get output directory for a target."""
        target_config = self.target_configs.get(target)
        if target_config:
            return self.root_dir / target_config.output
        return self.output_dir / target

    def get_package_prefix(self, target: str) -> str:
        """Get Java package prefix for a target."""
        target_config = self.target_configs.get(target)
        if target_config and target_config.options:
            return target_config.options.get("package", f"com.{self.name.replace('-', '.')}")
        return f"com.{self.name.replace('-', '.')}"

    def get_java_version(self, target: str) -> str:
        """Get Java version for a target."""
        target_config = self.target_configs.get(target)
        if target_config and target_config.options:
            return target_config.options.get("java_version", "17")
        return "17"


def create_default_config(name: str) -> str:
    """Create default nexflow.toml content."""
    return f'''# Nexflow Project Configuration
# https://github.com/your-org/nexflow

[project]
name = "{name}"
version = "0.1.0"

[paths]
src = "src"
output = "generated"

# Source directories for each DSL type
[sources.flow]
path = "src/flow"

[sources.schema]
path = "src/schema"

[sources.transform]
path = "src/transform"

[sources.rules]
path = "src/rules"

# Code generation targets
[targets.flink]
enabled = true
output = "generated/flink"

[targets.flink.options]
package = "{name.replace('-', '_')}.flink"
java_version = "17"

[targets.spark]
enabled = false
output = "generated/spark"

[targets.spark.options]
package = "{name.replace('-', '_')}.spark"

# External dependencies (other Nexflow projects)
# dependencies = ["../shared-schemas"]
'''
