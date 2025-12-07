"""
Voltage Encryption Profile Management

Manages Voltage Format-Preserving Encryption (FPE) profiles for PII fields.
Profiles define how different types of sensitive data should be encrypted.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import yaml


@dataclass
class VoltageProfile:
    """Voltage encryption profile configuration."""
    name: str
    format: str  # ssn, pan, email, full, custom
    description: str
    clear_prefix: int = 0  # Characters to leave clear at start
    clear_suffix: int = 0  # Characters to leave clear at end


class VoltageProfilesConfig:
    """Manages Voltage encryption profiles."""

    DEFAULT_PROFILES = {
        'ssn': VoltageProfile(
            name='ssn',
            format='ssn',
            description='SSN format - last 4 digits clear',
            clear_prefix=0,
            clear_suffix=4
        ),
        'pan': VoltageProfile(
            name='pan',
            format='pan',
            description='Credit card PAN - first 4 and last 4 clear',
            clear_prefix=4,
            clear_suffix=4
        ),
        'email': VoltageProfile(
            name='email',
            format='email',
            description='Email format preserving encryption',
            clear_prefix=0,
            clear_suffix=0
        ),
        'phone': VoltageProfile(
            name='phone',
            format='phone',
            description='Phone number format preserving',
            clear_prefix=0,
            clear_suffix=4
        ),
        'full': VoltageProfile(
            name='full',
            format='full',
            description='Full encryption - no clear text',
            clear_prefix=0,
            clear_suffix=0
        ),
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.profiles: Dict[str, VoltageProfile] = dict(self.DEFAULT_PROFILES)
        if config_path and config_path.exists():
            self._load_config(config_path)

    def _load_config(self, path: Path) -> None:
        """Load custom profiles from YAML config."""
        with open(path) as f:
            config = yaml.safe_load(f)
            if 'profiles' in config:
                for name, data in config['profiles'].items():
                    self.profiles[name] = VoltageProfile(
                        name=name,
                        format=data.get('format', 'custom'),
                        description=data.get('description', ''),
                        clear_prefix=data.get('clear_prefix', 0),
                        clear_suffix=data.get('clear_suffix', 0)
                    )

    def get_profile(self, name: Optional[str]) -> VoltageProfile:
        """Get profile by name, defaults to 'full' encryption."""
        if name is None:
            return self.profiles['full']
        return self.profiles.get(name, self.profiles['full'])
