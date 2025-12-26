# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
SQL Operators Mixin

Generates Flink/Spark SQL transform code for embedded SQL queries.
"""

import re
from backend.ast import proc_ast as ast
from backend.generators.common.java_utils import to_pascal_case, to_camel_case


class SqlOperatorsMixin:
    """Mixin for SQL transform operator wiring."""

    def _wire_sql_transform(self, sql_decl: ast.SqlTransformDecl, input_stream: str,
                             input_type: str, idx: int) -> tuple:
        """Wire embedded SQL transform using Flink Table API or Spark SQL.

        Generates code that:
        1. Registers the input DataStream as a temporary table
        2. Executes the SQL query
        3. Converts the result back to a DataStream
        """
        engine = self._get_sql_engine()

        if engine == "spark":
            return self._wire_sql_transform_spark(sql_decl, input_stream, input_type, idx)
        else:
            return self._wire_sql_transform_flink(sql_decl, input_stream, input_type, idx)

    def _get_sql_engine(self) -> str:
        """Get SQL execution engine from L5 config."""
        if hasattr(self, 'config') and self.config:
            engine = getattr(self.config, 'sql_engine', None)
            if engine:
                return engine.lower()
            context = getattr(self.config, 'validation_context', None)
            if context:
                l5_config = getattr(context, 'l5_config', None)
                if l5_config:
                    engine = getattr(l5_config, 'sql_engine', None)
                    if engine:
                        return engine.lower()
        return "flink"

    def _wire_sql_transform_flink(self, sql_decl: ast.SqlTransformDecl, input_stream: str,
                                   input_type: str, idx: int) -> tuple:
        """Generate Flink SQL execution code."""
        output_stream = f"sql{idx}Stream"

        if sql_decl.output_type:
            output_type = to_pascal_case(sql_decl.output_type)
        else:
            output_type = f"Sql{idx}Result"

        sql_content = sql_decl.sql_content.strip()
        input_table_name = self._extract_table_name_from_sql(sql_content, input_type)

        code = f'''        // SQL Transform (Flink SQL)
        // Register input stream as temporary table
        StreamTableEnvironment tableEnv = StreamTableEnvironment.create(env);
        tableEnv.createTemporaryView("{input_table_name}", {input_stream});

        // Execute SQL query
        Table sqlResult = tableEnv.sqlQuery(
            """
            {sql_content}
            """
        );

        // Convert result back to DataStream
        DataStream<{output_type}> {output_stream} = tableEnv
            .toDataStream(sqlResult, {output_type}.class)
            .name("sql-transform-{idx}");
'''
        return code, output_stream, output_type

    def _wire_sql_transform_spark(self, sql_decl: ast.SqlTransformDecl, input_stream: str,
                                   input_type: str, idx: int) -> tuple:
        """Generate Spark SQL execution code."""
        output_stream = f"sql{idx}Dataset"

        if sql_decl.output_type:
            output_type = to_pascal_case(sql_decl.output_type)
        else:
            output_type = f"Sql{idx}Result"

        sql_content = sql_decl.sql_content.strip()
        input_table_name = self._extract_table_name_from_sql(sql_content, input_type)

        code = f'''        // SQL Transform (Spark SQL)
        // Register input as temporary view
        {input_stream}.createOrReplaceTempView("{input_table_name}");

        // Execute SQL query
        Dataset<Row> sqlResult = spark.sql(
            """
            {sql_content}
            """
        );

        // Convert to typed Dataset
        Encoder<{output_type}> encoder = Encoders.bean({output_type}.class);
        Dataset<{output_type}> {output_stream} = sqlResult.as(encoder);
'''
        return code, output_stream, output_type

    def _extract_table_name_from_sql(self, sql_content: str, fallback: str) -> str:
        """Extract table name from SQL query for registration."""
        match = re.search(r'\bFROM\s+(\w+)', sql_content, re.IGNORECASE)
        if match:
            return match.group(1)
        return to_camel_case(fallback.replace('.', '_'))

    def get_sql_imports(self, engine: str = "flink") -> set:
        """Get imports needed for SQL transforms."""
        if engine == "spark":
            return {
                "org.apache.spark.sql.Dataset",
                "org.apache.spark.sql.Row",
                "org.apache.spark.sql.Encoders",
                "org.apache.spark.sql.Encoder",
                "org.apache.spark.sql.SparkSession",
            }
        else:
            return {
                "org.apache.flink.table.api.Table",
                "org.apache.flink.table.api.bridge.java.StreamTableEnvironment",
            }
