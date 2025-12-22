# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Input Block Visitor Mixin for Proc Parser

Handles parsing of input declarations: receive statements, schema references,
projections, store actions, and match actions.

Updated for grammar v0.5.0+ which uses flexible clause ordering.
"""

from backend.ast import proc_ast as ast
from backend.parser.generated.proc import ProcDSLParser


class ProcInputVisitorMixin:
    """Mixin for input block visitor methods."""

    def visitReceiveDecl(self, ctx: ProcDSLParser.ReceiveDeclContext) -> ast.ReceiveDecl:
        """
        Visit a receive declaration.

        Grammar: RECEIVE IDENTIFIER (FROM IDENTIFIER)? receiveClause*

        The first IDENTIFIER is the alias, the optional second is an inline source reference.
        Clauses (schema, connector, project, action, filter) can appear in any order.

        v0.8.0+: Supports parquet, csv, timestamp bounds.
        """
        identifiers = ctx.IDENTIFIER()

        # First identifier is always the alias
        alias = identifiers[0].getText() if identifiers else None

        # Second identifier (if present) is inline source: "receive X from Y"
        source = identifiers[1].getText() if len(identifiers) > 1 else None

        # Process clauses in any order
        schema = None
        project = None
        store_action = None
        match_action = None
        connector_source = None
        connector_type = ast.ConnectorType.KAFKA  # Default
        timestamp_bounds = None
        parquet_config = None
        csv_config = None
        filter_expr = None

        for clause_ctx in ctx.receiveClause():
            if clause_ctx.schemaDecl():
                schema = self.visitSchemaDecl(clause_ctx.schemaDecl())
            elif clause_ctx.projectClause():
                project = self.visitProjectClause(clause_ctx.projectClause())
            elif clause_ctx.receiveAction():
                action_ctx = clause_ctx.receiveAction()
                if action_ctx.storeAction():
                    store_action = self.visitStoreAction(action_ctx.storeAction())
                elif action_ctx.matchAction():
                    match_action = self.visitMatchAction(action_ctx.matchAction())
            elif clause_ctx.connectorClause():
                # Extract source and connector type from connector clause
                connector_ctx = clause_ctx.connectorClause()

                # Determine connector type
                if connector_ctx.connectorType():
                    ct_ctx = connector_ctx.connectorType()
                    ct_text = self._get_text(ct_ctx).lower()
                    if 'kafka' in ct_text:
                        connector_type = ast.ConnectorType.KAFKA
                    elif 'parquet' in ct_text:
                        connector_type = ast.ConnectorType.PARQUET
                    elif 'csv' in ct_text:
                        connector_type = ast.ConnectorType.CSV
                    elif 'redis' in ct_text:
                        connector_type = ast.ConnectorType.REDIS
                    elif 'mongodb' in ct_text:
                        connector_type = ast.ConnectorType.MONGODB
                    elif 'state_store' in ct_text:
                        connector_type = ast.ConnectorType.STATE_STORE
                    elif 'scheduler' in ct_text:
                        connector_type = ast.ConnectorType.SCHEDULER

                if connector_ctx.connectorConfig():
                    config = connector_ctx.connectorConfig()
                    # Get first string or identifier from config
                    if config.STRING():
                        connector_source = config.STRING(0).getText().strip('"')
                    elif config.IDENTIFIER():
                        connector_source = config.IDENTIFIER(0).getText()

                    # v0.8.0+: Parse connector options for timestamp bounds and file configs
                    if hasattr(config, 'connectorOptions') and config.connectorOptions():
                        for opt_ctx in config.connectorOptions():
                            # Parse timestamp bounds
                            if hasattr(opt_ctx, 'timestampBounds') and opt_ctx.timestampBounds():
                                timestamp_bounds = self._parse_timestamp_bounds(opt_ctx.timestampBounds())
                            # Parse parquet options
                            if hasattr(opt_ctx, 'parquetOptions') and opt_ctx.parquetOptions():
                                partition_cols, schema_path = self._parse_parquet_options(opt_ctx.parquetOptions())
                                if not parquet_config:
                                    parquet_config = ast.ParquetConfig(
                                        path=connector_source or "",
                                        partition_columns=partition_cols,
                                        schema_path=schema_path
                                    )
                                else:
                                    if partition_cols:
                                        parquet_config.partition_columns = partition_cols
                                    if schema_path:
                                        parquet_config.schema_path = schema_path
                            # Parse csv options
                            if hasattr(opt_ctx, 'csvOptions') and opt_ctx.csvOptions():
                                csv_opts = self._parse_csv_options(opt_ctx.csvOptions())
                                if not csv_config:
                                    csv_config = ast.CsvConfig(path=connector_source or "", **csv_opts)
                                else:
                                    for k, v in csv_opts.items():
                                        setattr(csv_config, k, v)

            # Filter clause handled separately if needed

        # Use inline source or connector source
        final_source = source or connector_source or alias

        # Create file configs if connector type requires it
        if connector_type == ast.ConnectorType.PARQUET and not parquet_config:
            parquet_config = ast.ParquetConfig(path=final_source, timestamp_bounds=timestamp_bounds)
        elif connector_type == ast.ConnectorType.CSV and not csv_config:
            csv_config = ast.CsvConfig(path=final_source, timestamp_bounds=timestamp_bounds)

        return ast.ReceiveDecl(
            source=final_source,
            connector_type=connector_type,
            alias=alias,
            schema=schema,
            project=project,
            store_action=store_action,
            match_action=match_action,
            parquet_config=parquet_config,
            csv_config=csv_config,
            timestamp_bounds=timestamp_bounds,
            location=self._get_location(ctx)
        )

    def _parse_timestamp_bounds(self, ctx) -> ast.TimestampBounds:
        """Parse timestamp bounds from connector options.

        Grammar: FROM TIMESTAMP STRING (TO TIMESTAMP STRING)?
               | TO TIMESTAMP STRING
        """
        from_ts = None
        to_ts = None

        strings = ctx.STRING() if hasattr(ctx, 'STRING') else []
        if strings:
            strings = strings if isinstance(strings, list) else [strings]
            # Check for FROM keyword
            has_from = any(
                self._get_text(child).lower() == 'from'
                for child in ctx.getChildren()
                if hasattr(child, 'getText')
            )

            if has_from and len(strings) >= 1:
                from_ts = strings[0].getText().strip('"\'')
                if len(strings) >= 2:
                    to_ts = strings[1].getText().strip('"\'')
            elif len(strings) >= 1:
                # Only TO timestamp
                to_ts = strings[0].getText().strip('"\'')

        return ast.TimestampBounds(
            from_timestamp=from_ts,
            to_timestamp=to_ts,
            location=self._get_location(ctx)
        )

    def _parse_parquet_options(self, ctx) -> tuple:
        """Parse parquet-specific options.

        Returns: (partition_columns, schema_path)
        """
        partition_cols = None
        schema_path = None

        if hasattr(ctx, 'fieldList') and ctx.fieldList():
            partition_cols = self._get_field_list(ctx.fieldList())
        if hasattr(ctx, 'STRING') and ctx.STRING():
            schema_path = ctx.STRING().getText().strip('"\'')

        return partition_cols, schema_path

    def _parse_csv_options(self, ctx) -> dict:
        """Parse CSV-specific options.

        Returns: dict with csv options
        """
        opts = {}

        if hasattr(ctx, 'STRING') and ctx.STRING():
            string_val = ctx.STRING().getText().strip('"\'')
            # Determine which option based on context
            text = self._get_text(ctx).lower()
            if 'delimiter' in text:
                opts['delimiter'] = string_val
            elif 'quote' in text:
                opts['quote_char'] = string_val
            elif 'escape' in text:
                opts['escape_char'] = string_val
            elif 'null_value' in text:
                opts['null_value'] = string_val

        if hasattr(ctx, 'booleanLiteral') and ctx.booleanLiteral():
            bool_val = self._get_text(ctx.booleanLiteral()).lower() == 'true'
            opts['has_header'] = bool_val

        return opts

    def visitSchemaDecl(self, ctx: ProcDSLParser.SchemaDeclContext) -> ast.SchemaDecl:
        schema_name = ctx.IDENTIFIER().getText()
        return ast.SchemaDecl(
            schema_name=schema_name,
            location=self._get_location(ctx)
        )

    def visitProjectClause(self, ctx: ProcDSLParser.ProjectClauseContext) -> ast.ProjectClause:
        fields = self._get_field_list(ctx.fieldList())
        is_except = any(
            self._get_text(child) == 'except'
            for child in ctx.getChildren()
        )
        return ast.ProjectClause(
            fields=fields,
            is_except=is_except,
            location=self._get_location(ctx)
        )

    def visitStoreAction(self, ctx: ProcDSLParser.StoreActionContext) -> ast.StoreAction:
        state_name = ctx.IDENTIFIER().getText()
        return ast.StoreAction(
            state_name=state_name,
            location=self._get_location(ctx)
        )

    def visitMatchAction(self, ctx: ProcDSLParser.MatchActionContext) -> ast.MatchAction:
        state_name = ctx.IDENTIFIER().getText()
        on_fields = self._get_field_list(ctx.fieldList())
        return ast.MatchAction(
            state_name=state_name,
            on_fields=on_fields,
            location=self._get_location(ctx)
        )
