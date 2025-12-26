# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Kafka Configuration Module

Handles Kafka cluster profiles, SSL configuration, and PII masking settings.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import tomllib


@dataclass
class PIIConfig:
    """PII masking configuration."""
    masked_fields: List[str] = field(default_factory=lambda: [
        "ssn", "social_security_number",
        "credit_card", "card_number", "cvv",
        "email", "phone", "mobile",
        "address", "street_address",
        "date_of_birth", "dob",
        "password", "secret", "token",
        "account_number", "routing_number",
    ])
    mask_pattern: str = "***MASKED***"
    enabled: bool = True


@dataclass
class KafkaProfile:
    """Kafka cluster connection profile."""
    name: str
    bootstrap_servers: str
    security_protocol: str = "PLAINTEXT"

    # SSL configuration
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    ssl_password: Optional[str] = None

    # SASL configuration
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None

    # PII handling
    pii_mask: bool = False

    # Timeouts
    request_timeout_ms: int = 30000
    session_timeout_ms: int = 10000

    def to_kafka_config(self) -> Dict[str, any]:
        """Convert to confluent-kafka configuration dictionary."""
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'security.protocol': self.security_protocol,
            'request.timeout.ms': self.request_timeout_ms,
            'session.timeout.ms': self.session_timeout_ms,
        }

        # SSL settings
        if self.security_protocol in ('SSL', 'SASL_SSL'):
            if self.ssl_cafile:
                config['ssl.ca.location'] = self.ssl_cafile
            if self.ssl_certfile:
                config['ssl.certificate.location'] = self.ssl_certfile
            if self.ssl_keyfile:
                config['ssl.key.location'] = self.ssl_keyfile
            if self.ssl_password:
                config['ssl.key.password'] = self.ssl_password

        # SASL settings
        if self.security_protocol in ('SASL_PLAINTEXT', 'SASL_SSL'):
            if self.sasl_mechanism:
                config['sasl.mechanism'] = self.sasl_mechanism
            if self.sasl_username:
                config['sasl.username'] = self.sasl_username
            if self.sasl_password:
                config['sasl.password'] = self.sasl_password

        return config


@dataclass
class SchemaRegistryConfig:
    """Schema registry configuration."""
    url: str = "http://localhost:8081"
    ssl_cafile: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    basic_auth_user: Optional[str] = None
    basic_auth_password: Optional[str] = None

    def to_registry_config(self) -> Dict[str, any]:
        """Convert to schema registry client configuration."""
        config = {'url': self.url}

        if self.ssl_cafile:
            config['ssl.ca.location'] = self.ssl_cafile
        if self.ssl_certfile:
            config['ssl.certificate.location'] = self.ssl_certfile
        if self.ssl_keyfile:
            config['ssl.key.location'] = self.ssl_keyfile
        if self.basic_auth_user and self.basic_auth_password:
            config['basic.auth.credentials.source'] = 'USER_INFO'
            config['basic.auth.user.info'] = f"{self.basic_auth_user}:{self.basic_auth_password}"

        return config


@dataclass
class KafkaConfig:
    """Complete Kafka configuration including all profiles."""
    profiles: Dict[str, KafkaProfile] = field(default_factory=dict)
    default_profile: str = "dev"
    schema_registry: Optional[SchemaRegistryConfig] = None
    pii: PIIConfig = field(default_factory=PIIConfig)

    @classmethod
    def from_toml(cls, toml_path: Path) -> 'KafkaConfig':
        """Load Kafka configuration from nexflow.toml."""
        if not toml_path.exists():
            return cls()

        with open(toml_path, 'rb') as f:
            data = tomllib.load(f)

        kafka_data = data.get('kafka', {})

        # Parse profiles
        profiles = {}
        for name, profile_data in kafka_data.get('profiles', {}).items():
            profiles[name] = KafkaProfile(
                name=name,
                bootstrap_servers=profile_data.get('bootstrap_servers', 'localhost:9092'),
                security_protocol=profile_data.get('security_protocol', 'PLAINTEXT'),
                ssl_cafile=profile_data.get('ssl_cafile'),
                ssl_certfile=profile_data.get('ssl_certfile'),
                ssl_keyfile=profile_data.get('ssl_keyfile'),
                ssl_password=profile_data.get('ssl_password'),
                sasl_mechanism=profile_data.get('sasl_mechanism'),
                sasl_username=profile_data.get('sasl_username'),
                sasl_password=profile_data.get('sasl_password'),
                pii_mask=profile_data.get('pii_mask', False),
                request_timeout_ms=profile_data.get('request_timeout_ms', 30000),
                session_timeout_ms=profile_data.get('session_timeout_ms', 10000),
            )

        # Default dev profile if none configured
        if not profiles:
            profiles['dev'] = KafkaProfile(
                name='dev',
                bootstrap_servers='localhost:9092',
            )

        # Parse schema registry
        schema_registry = None
        registry_data = kafka_data.get('schema_registry', {})
        if registry_data:
            schema_registry = SchemaRegistryConfig(
                url=registry_data.get('url', 'http://localhost:8081'),
                ssl_cafile=registry_data.get('ssl_cafile'),
                ssl_certfile=registry_data.get('ssl_certfile'),
                ssl_keyfile=registry_data.get('ssl_keyfile'),
                basic_auth_user=registry_data.get('basic_auth_user'),
                basic_auth_password=registry_data.get('basic_auth_password'),
            )

        # Parse PII config
        pii_data = kafka_data.get('pii', {})
        pii = PIIConfig(
            masked_fields=pii_data.get('masked_fields', PIIConfig().masked_fields),
            mask_pattern=pii_data.get('mask_pattern', '***MASKED***'),
            enabled=pii_data.get('enabled', True),
        )

        # Default profile
        default_profile = kafka_data.get('default_profile', {}).get('name', 'dev')

        return cls(
            profiles=profiles,
            default_profile=default_profile,
            schema_registry=schema_registry,
            pii=pii,
        )

    def get_profile(self, name: Optional[str] = None) -> KafkaProfile:
        """Get a profile by name, or the default profile."""
        profile_name = name or self.default_profile
        if profile_name not in self.profiles:
            raise ValueError(f"Unknown Kafka profile: {profile_name}. "
                           f"Available: {list(self.profiles.keys())}")
        return self.profiles[profile_name]
