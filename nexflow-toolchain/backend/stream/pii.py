# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
PII Masking Module

Automatically masks personally identifiable information (PII) in stream messages
when viewing production data.
"""

import re
from typing import Any, Dict, List, Set

from .config import PIIConfig


class PIIMasker:
    """Masks PII fields in message records."""

    def __init__(self, config: PIIConfig):
        self.config = config
        self._masked_fields_lower = {f.lower() for f in config.masked_fields}

        # Common PII patterns for auto-detection
        self._patterns = {
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
        }

    def mask(self, record: Dict[str, Any], field_path: str = "") -> Dict[str, Any]:
        """Recursively mask PII fields in a record."""
        if not self.config.enabled:
            return record

        return self._mask_value(record, field_path)

    def _mask_value(self, value: Any, path: str) -> Any:
        """Mask a value recursively."""
        if isinstance(value, dict):
            return {
                k: self._mask_value(v, f"{path}.{k}" if path else k)
                for k, v in value.items()
            }
        elif isinstance(value, list):
            return [
                self._mask_value(item, f"{path}[{i}]")
                for i, item in enumerate(value)
            ]
        elif isinstance(value, str):
            return self._mask_string(value, path)
        else:
            return value

    def _mask_string(self, value: str, path: str) -> str:
        """Mask a string value if it's PII."""
        # Check if field name indicates PII
        field_name = path.split('.')[-1].split('[')[0].lower()

        if self._is_pii_field(field_name):
            return self.config.mask_pattern

        # Check for PII patterns in value
        if self._contains_pii_pattern(value):
            return self.config.mask_pattern

        return value

    def _is_pii_field(self, field_name: str) -> bool:
        """Check if field name indicates PII."""
        # Exact match
        if field_name in self._masked_fields_lower:
            return True

        # Partial match (e.g., 'customer_ssn' contains 'ssn')
        for pii_field in self._masked_fields_lower:
            if pii_field in field_name or field_name in pii_field:
                return True

        return False

    def _contains_pii_pattern(self, value: str) -> bool:
        """Check if value contains PII patterns."""
        for pattern in self._patterns.values():
            if pattern.search(value):
                return True
        return False

    def get_masked_fields(self, record: Dict[str, Any]) -> Set[str]:
        """Get a set of field paths that would be masked."""
        masked = set()
        self._collect_masked_fields(record, "", masked)
        return masked

    def _collect_masked_fields(self, value: Any, path: str, masked: Set[str]):
        """Collect paths of fields that would be masked."""
        if isinstance(value, dict):
            for k, v in value.items():
                new_path = f"{path}.{k}" if path else k
                self._collect_masked_fields(v, new_path, masked)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                self._collect_masked_fields(item, f"{path}[{i}]", masked)
        elif isinstance(value, str):
            field_name = path.split('.')[-1].split('[')[0].lower()
            if self._is_pii_field(field_name) or self._contains_pii_pattern(value):
                masked.add(path)


def create_masker(profile_has_pii_mask: bool, pii_config: PIIConfig) -> PIIMasker:
    """Create a PII masker based on profile and config."""
    config = PIIConfig(
        masked_fields=pii_config.masked_fields,
        mask_pattern=pii_config.mask_pattern,
        enabled=profile_has_pii_mask and pii_config.enabled,
    )
    return PIIMasker(config)
