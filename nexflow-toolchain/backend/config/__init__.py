# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Configuration Module

Provides configuration resolution for Nexflow builds:
- Organization-level policy governance (nexflow-org.toml)
- Serialization format configuration (JSON, Avro, Protobuf)
- Hierarchical config loading from nexflow.toml files
- Policy validation and enforcement
- Environment-specific overlays

Governance Hierarchy:
    Organization (nexflow-org.toml)
        └── Team/Project (nexflow.toml)
             └── Schema (.schema file)
                  └── Connector (.proc file)
"""

from backend.config.org_policy import (
    OrganizationPolicy,
    find_org_policy_file,
    load_org_policy,
)

from backend.config.policy_validator import (
    ViolationLevel,
    PolicyViolation,
    ValidationResult,
    PolicyValidator,
    create_validator,
)

from backend.config.serialization_resolver import (
    SerializationResolver,
    resolve_serialization,
    resolve_serialization_with_validation,
)

__all__ = [
    # Organization Policy
    "OrganizationPolicy",
    "find_org_policy_file",
    "load_org_policy",
    # Policy Validation
    "ViolationLevel",
    "PolicyViolation",
    "ValidationResult",
    "PolicyValidator",
    "create_validator",
    # Serialization Resolution
    "SerializationResolver",
    "resolve_serialization",
    "resolve_serialization_with_validation",
]
