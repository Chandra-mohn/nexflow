# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
PII Helper Generator Module

Generates Voltage SDK helper classes for PII field encryption/decryption.
"""

from typing import List, Tuple

from backend.ast import schema_ast as ast
from backend.generators.base import BaseGenerator


class PiiHelperGeneratorMixin:
    """Mixin providing PII helper generation capabilities."""

    def generate_pii_helper(self: BaseGenerator, schema: ast.SchemaDefinition,
                            class_name: str, package: str) -> str:
        """Generate Voltage SDK helper for PII encryption/decryption."""
        header = self.generate_java_header(
            f"{class_name}PiiHelper", f"PII encryption helper for {class_name}"
        )
        package_decl = self.generate_package_declaration(package)

        imports = self.generate_imports([
            'com.voltage.securedata.enterprise.VoltageSDK',
            'com.voltage.securedata.enterprise.FPEEncryption',
        ])

        all_fields = self._collect_all_fields(schema)

        # Collect PII fields
        pii_fields = [
            (f, self._get_pii_profile(f))
            for f in all_fields if self._get_pii_profile(f)
        ]

        encrypt_methods = self._generate_encrypt_methods(class_name, pii_fields)
        decrypt_methods = self._generate_decrypt_methods(class_name, pii_fields)
        bulk_methods = self._generate_bulk_methods(class_name, pii_fields)

        return f'''{header}
{package_decl}
{imports}

/**
 * Helper class for encrypting/decrypting PII fields in {class_name}.
 * Uses Voltage Format-Preserving Encryption (FPE) SDK.
 */
public class {class_name}PiiHelper {{

    private {class_name}PiiHelper() {{
        // Utility class
    }}

{encrypt_methods}

{decrypt_methods}

{bulk_methods}
}}
'''

    def _generate_encrypt_methods(
        self: BaseGenerator,
        class_name: str,
        pii_fields: List[Tuple[ast.FieldDecl, str]]
    ) -> str:
        """Generate individual field encrypt methods."""
        methods = []
        for field_decl, profile_name in pii_fields:
            field_name = self.to_java_field_name(field_decl.name)
            method_suffix = field_name[0].upper() + field_name[1:]
            getter = f"get{method_suffix}"
            setter = f"set{method_suffix}"

            profile = self.voltage_profiles.get_profile(profile_name)

            methods.append(f'''    /**
     * Encrypt {field_decl.name} field using '{profile_name}' profile.
     * {profile.description}
     */
    public static void encrypt{method_suffix}({class_name} record, VoltageSDK sdk) {{
        if (record.{getter}() != null) {{
            String encrypted = sdk.protect("{profile_name}", record.{getter}());
            record.{setter}(encrypted);
        }}
    }}''')

        return '\n\n'.join(methods)

    def _generate_decrypt_methods(
        self: BaseGenerator,
        class_name: str,
        pii_fields: List[Tuple[ast.FieldDecl, str]]
    ) -> str:
        """Generate individual field decrypt methods."""
        methods = []
        for field_decl, profile_name in pii_fields:
            field_name = self.to_java_field_name(field_decl.name)
            method_suffix = field_name[0].upper() + field_name[1:]
            getter = f"get{method_suffix}"
            setter = f"set{method_suffix}"

            methods.append(f'''    /**
     * Decrypt {field_decl.name} field using '{profile_name}' profile.
     */
    public static void decrypt{method_suffix}({class_name} record, VoltageSDK sdk) {{
        if (record.{getter}() != null) {{
            String decrypted = sdk.access("{profile_name}", record.{getter}());
            record.{setter}(decrypted);
        }}
    }}''')

        return '\n\n'.join(methods)

    def _generate_bulk_methods(
        self: BaseGenerator,
        class_name: str,
        pii_fields: List[Tuple[ast.FieldDecl, str]]
    ) -> str:
        """Generate bulk encrypt/decrypt methods."""
        encrypt_calls = '\n'.join(
            f'        encrypt{self.to_java_field_name(f.name)[0].upper()}'
            f'{self.to_java_field_name(f.name)[1:]}(record, sdk);'
            for f, _ in pii_fields
        )
        decrypt_calls = '\n'.join(
            f'        decrypt{self.to_java_field_name(f.name)[0].upper()}'
            f'{self.to_java_field_name(f.name)[1:]}(record, sdk);'
            for f, _ in pii_fields
        )

        return f'''    /**
     * Encrypt all PII fields in the record.
     */
    public static void encryptAll({class_name} record, VoltageSDK sdk) {{
{encrypt_calls}
    }}

    /**
     * Decrypt all PII fields in the record.
     */
    public static void decryptAll({class_name} record, VoltageSDK sdk) {{
{decrypt_calls}
    }}'''
