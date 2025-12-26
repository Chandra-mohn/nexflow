# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
File Sources Mixin

Generates Flink FileSource connectors for file-based sources:
- Parquet
- CSV
"""

from typing import Set

from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_camel_case


class FileSourcesMixin:
    """Mixin for generating file-based source connectors (Parquet, CSV)."""

    def _generate_parquet_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate Parquet source code for a receive declaration.

        Generates Flink FileSource with Parquet format for batch reads.
        Supports timestamp bounds for filtering and partition columns.
        """
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        # Get parquet config
        parquet_config = receive.parquet_config
        path = parquet_config.path if parquet_config else source_name
        partition_cols = parquet_config.partition_columns if parquet_config else None

        lines = [
            f"// Parquet Source: {source_name}",
        ]

        # Build FileSource with Parquet format
        lines.extend([
            f"FileSource<{schema_class}> {to_camel_case(source_name)}Source = FileSource",
            f"    .forRecordStreamFormat(",
            f"        new ParquetAvroReaders().forGenericRecord(),",
            f"        new Path(\"{path}\")",
            f"    )",
        ])

        # Add partition filter if partition columns specified
        if partition_cols:
            lines.append(f"    // Partition columns: {', '.join(partition_cols)}")

        # Add timestamp bounds filter if specified
        timestamp_bounds = receive.timestamp_bounds or (parquet_config.timestamp_bounds if parquet_config else None)
        if timestamp_bounds:
            if timestamp_bounds.from_timestamp:
                lines.append(f"    // From timestamp: {timestamp_bounds.from_timestamp}")
            if timestamp_bounds.to_timestamp:
                lines.append(f"    // To timestamp: {timestamp_bounds.to_timestamp}")

        lines.extend([
            f"    .build();",
            "",
        ])

        # Create DataStream with watermark strategy
        watermark_strategy = self._generate_watermark_strategy(process, schema_class)
        lines.extend([
            f"DataStream<{schema_class}> {stream_var} = env",
            f"    .fromSource(",
            f"        {to_camel_case(source_name)}Source,",
            f"        {watermark_strategy},",
            f"        \"{source_name}\"",
            f"    );",
            "",
        ])

        # Apply projections and actions
        lines.extend(self._apply_source_options(receive, stream_var, schema_class, stream_alias))

        return '\n'.join(lines)

    def _generate_csv_source(self, receive: ast.ReceiveDecl, process: ast.ProcessDefinition) -> str:
        """Generate CSV source code for a receive declaration.

        Generates Flink FileSource with CSV format for batch reads.
        """
        source_name = receive.source
        stream_alias = receive.alias if receive.alias else source_name
        stream_var = self._to_stream_var(stream_alias)
        schema_class = self._get_schema_class(receive)

        # Get CSV config
        csv_config = receive.csv_config
        path = csv_config.path if csv_config else source_name
        delimiter = csv_config.delimiter if csv_config else ","
        quote_char = csv_config.quote_char if csv_config else '"'
        has_header = csv_config.has_header if csv_config else True
        null_value = csv_config.null_value if csv_config else ""

        lines = [
            f"// CSV Source: {source_name}",
            f"CsvReaderFormat<{schema_class}> csvFormat = CsvReaderFormat.forSchema(",
            f"    CsvSchema.builder()",
            f"        .setColumnSeparator('{delimiter}')",
            f"        .setQuoteChar('{quote_char}')",
            f"        .setUseHeader({str(has_header).lower()})",
            f"        .setNullValue(\"{null_value}\")",
            f"        .build(),",
            f"    TypeInformation.of({schema_class}.class)",
            f");",
            "",
            f"FileSource<{schema_class}> {to_camel_case(source_name)}Source = FileSource",
            f"    .forRecordStreamFormat(csvFormat, new Path(\"{path}\"))",
            f"    .build();",
            "",
        ]

        # Create DataStream with watermark strategy
        watermark_strategy = self._generate_watermark_strategy(process, schema_class)
        lines.extend([
            f"DataStream<{schema_class}> {stream_var} = env",
            f"    .fromSource(",
            f"        {to_camel_case(source_name)}Source,",
            f"        {watermark_strategy},",
            f"        \"{source_name}\"",
            f"    );",
            "",
        ])

        # Apply projections and actions
        lines.extend(self._apply_source_options(receive, stream_var, schema_class, stream_alias))

        return '\n'.join(lines)

    def get_parquet_imports(self) -> Set[str]:
        """Get imports needed for Parquet sources."""
        return {
            'org.apache.flink.connector.file.src.FileSource',
            'org.apache.flink.core.fs.Path',
            'org.apache.flink.formats.parquet.ParquetAvroReaders',
        }

    def get_csv_imports(self) -> Set[str]:
        """Get imports needed for CSV sources."""
        return {
            'org.apache.flink.connector.file.src.FileSource',
            'org.apache.flink.core.fs.Path',
            'org.apache.flink.formats.csv.CsvReaderFormat',
            'org.apache.flink.shaded.jackson2.com.fasterxml.jackson.dataformat.csv.CsvSchema',
            'org.apache.flink.api.common.typeinfo.TypeInformation',
        }
