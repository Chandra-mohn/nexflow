"""
Unit tests for Schema Code Generator.
"""

import pytest
import tempfile
from pathlib import Path

from backend.parser import parse
from backend.generators import get_generator, GeneratorConfig


class TestSchemaGeneratorBasic:
    """Basic schema code generation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = GeneratorConfig(
            output_dir=Path(self.temp_dir),
            package_prefix='com.test',
        )
        self.generator = get_generator('schema', self.config)

    def test_simple_schema_generation(self):
        """Test generating code for simple schema."""
        dsl = """
        schema user
            fields
                id: integer required
                name: string required
                email: string optional
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        gen_result = self.generator.generate(result.ast)
        assert gen_result.success, f"Generation failed"
        assert len(gen_result.files) > 0

        # Check that Java class is generated
        java_files = [f for f in gen_result.files if str(f.path).endswith('.java')]
        assert len(java_files) > 0

    def test_schema_class_content(self):
        """Test the content of generated schema class."""
        dsl = """
        schema product
            fields
                sku: string required
                price: decimal required
                active: boolean optional
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        gen_result = self.generator.generate(result.ast)
        assert gen_result.success

        # Find the Product class (generator converts to PascalCase)
        product_file = next(
            (f for f in gen_result.files if 'Product.java' in str(f.path)),
            None
        )
        assert product_file is not None

        content = product_file.content

        # Verify record structure (Java Records instead of POJOs)
        assert 'record Product' in content
        assert 'implements Serializable' in content
        assert 'sku' in content.lower()  # Has fields as record components

    def test_builder_generation(self):
        """Test that builder class is generated."""
        dsl = """
        schema order
            fields
                order_id: string required
                total: decimal required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        gen_result = self.generator.generate(result.ast)
        assert gen_result.success

        # Check for builder class
        builder_files = [f for f in gen_result.files if 'Builder' in str(f.path)]
        assert len(builder_files) > 0


class TestSchemaGeneratorTypes:
    """Schema type mapping tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = GeneratorConfig(output_dir=Path(self.temp_dir), package_prefix='com.test')
        self.generator = get_generator('schema', self.config)

    def test_type_mappings(self):
        """Test DSL to Java type mappings."""
        dsl = """
        schema type_test
            fields
                int_field: integer required
                str_field: string required
                bool_field: boolean required
                dec_field: decimal required
                ts_field: timestamp required
                uuid_field: uuid required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        gen_result = self.generator.generate(result.ast)
        assert gen_result.success

        # Find main class (generator converts to PascalCase)
        type_file = next(
            (f for f in gen_result.files if 'TypeTest.java' in str(f.path)),
            None
        )
        assert type_file is not None

        content = type_file.content

        # Check type mappings (flexible - depends on implementation)
        # These checks verify the content has appropriate Java types
        assert 'Integer' in content or 'int' in content or 'Long' in content
        assert 'String' in content
        assert 'Boolean' in content or 'boolean' in content


class TestSchemaGeneratorNested:
    """Nested schema generation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = GeneratorConfig(output_dir=Path(self.temp_dir), package_prefix='com.test')
        self.generator = get_generator('schema', self.config)

    def test_nested_object_generation(self):
        """Test generating nested object schemas."""
        dsl = """
        schema order_with_address
            fields
                order_id: string required
                total: decimal required
            end

            address: object
                street: string required
                city: string required
                postal_code: string required
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        gen_result = self.generator.generate(result.ast)
        assert gen_result.success


class TestSchemaGeneratorMultiple:
    """Multiple schema generation tests."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = GeneratorConfig(output_dir=Path(self.temp_dir), package_prefix='com.test')
        self.generator = get_generator('schema', self.config)

    def test_multiple_schemas(self):
        """Test generating multiple schemas from one file."""
        dsl = """
        schema user
            fields
                id: integer required
                name: string required
            end
        end

        schema profile
            fields
                user_id: integer required
                bio: string optional
            end
        end
        """
        result = parse(dsl, 'schema')
        assert result.success, f"Parse failed: {result.errors}"

        gen_result = self.generator.generate(result.ast)
        assert gen_result.success

        # Should have files for both schemas (generator converts to PascalCase)
        user_files = [f for f in gen_result.files if 'User' in str(f.path)]
        profile_files = [f for f in gen_result.files if 'Profile' in str(f.path)]

        assert len(user_files) > 0
        assert len(profile_files) > 0
