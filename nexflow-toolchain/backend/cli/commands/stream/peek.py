# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow Peek Command

Inspect live or historical messages from Kafka topics with filtering and formatting.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.json import JSON
from rich.table import Table
from rich.live import Live

from backend.stream.config import KafkaConfig
from backend.stream.client import create_client, ConsumeOptions
from backend.stream.decoder import MessageDecoder
from backend.ast.serialization import SerializationFormat


console = Console()


def _format_timestamp(ts: Optional[int]) -> str:
    """Format a millisecond timestamp."""
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")


def _truncate(value: str, max_len: int = 50) -> str:
    """Truncate a string to max length."""
    if len(value) <= max_len:
        return value
    return value[:max_len - 3] + "..."


@click.command()
@click.argument("topic")
@click.option("--profile", "-p", default=None,
              help="Kafka cluster profile (default: from config)")
@click.option("--limit", "-n", default=10, type=int,
              help="Number of messages to display (default: 10)")
@click.option("--offset", default="latest",
              help="Start offset: 'earliest', 'latest', or numeric (default: latest)")
@click.option("--format", "-f", "output_format",
              type=click.Choice(["json", "table", "raw"]),
              default="json", help="Output format (default: json)")
@click.option("--filter", "filter_expr", default=None,
              help="SQL-like filter expression")
@click.option("--follow", "-F", is_flag=True,
              help="Continuous streaming mode (like tail -f)")
@click.option("--partition", type=int, default=None,
              help="Specific partition to read from")
@click.option("--timeout", default=30, type=int,
              help="Connection timeout in seconds (default: 30)")
@click.option("--unmask", is_flag=True,
              help="Disable PII masking (requires confirmation)")
@click.option("--schema", type=click.Path(exists=True),
              help="Local schema file for decoding (offline mode)")
@click.option("--decode-format", type=click.Choice(["auto", "json", "avro", "confluent-avro", "protobuf"]),
              default="auto", help="Message serialization format (default: auto)")
@click.pass_context
def peek(
    ctx: click.Context,
    topic: str,
    profile: Optional[str],
    limit: int,
    offset: str,
    output_format: str,
    filter_expr: Optional[str],
    follow: bool,
    partition: Optional[int],
    timeout: int,
    unmask: bool,
    schema: Optional[str],
    decode_format: str,
):
    """
    Inspect messages from a Kafka topic.

    View live or historical messages with optional filtering and formatting.
    Supports JSON, Avro, and Protobuf serialization formats.

    \b
    Examples:
        nexflow peek orders-avro
        nexflow peek orders-avro --filter "status = 'pending'"
        nexflow peek orders-avro --follow --filter "amount > 100"
        nexflow peek orders-avro --profile prod --limit 100
        nexflow peek orders-avro --offset earliest --limit 50
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    # Handle unmask confirmation
    if unmask:
        if not click.confirm("⚠️  This will show unmasked PII data. Are you sure?"):
            console.print("[yellow]Cancelled[/yellow]")
            return

    try:
        # Load Kafka configuration
        config_path = Path.cwd() / "nexflow.toml"
        kafka_config = KafkaConfig.from_toml(config_path)

        # Get profile
        kafka_profile = kafka_config.get_profile(profile)

        # Override PII masking if unmask requested
        if unmask:
            kafka_profile.pii_mask = False

        # Configure decoder
        fmt = None
        if decode_format != "auto":
            fmt = SerializationFormat(decode_format.replace("-", "_").upper())

        schema_path = Path(schema) if schema else None
        registry_url = kafka_config.schema_registry.url if kafka_config.schema_registry else None

        decoder = MessageDecoder(
            format=fmt,
            schema_path=schema_path,
            registry_url=registry_url,
        )

        # Create client
        client = create_client(kafka_config, profile, decoder)

        # Show connection info
        if verbose:
            console.print(f"[dim]Connecting to {kafka_profile.bootstrap_servers}...[/dim]")
            if kafka_profile.pii_mask:
                console.print("[dim]PII masking: enabled[/dim]")

        # Get topic metadata
        try:
            metadata = client.get_topic_metadata(topic)
            if verbose:
                console.print(f"[dim]Topic: {metadata.name} ({metadata.partitions} partitions)[/dim]")
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to get topic metadata: {e}")
            sys.exit(3)

        # Configure consume options
        options = ConsumeOptions(
            limit=limit,
            offset=offset,
            partition=partition,
            filter_expr=filter_expr,
            timeout_seconds=timeout,
            follow=follow,
        )

        # Consume and display messages
        if output_format == "table":
            _display_table(client, topic, options, follow)
        elif output_format == "raw":
            _display_raw(client, topic, options)
        else:
            _display_json(client, topic, options)

    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(2)
    except RuntimeError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        sys.exit(3)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


def _display_json(client, topic: str, options: ConsumeOptions):
    """Display messages as JSON."""
    messages = []

    try:
        for msg in client.consume(topic, options):
            msg_dict = msg.to_dict()

            if options.follow:
                # In follow mode, print each message immediately
                console.print(JSON(json.dumps(msg_dict, indent=2, default=str)))
                console.print()
            else:
                messages.append(msg_dict)

        if not options.follow:
            # Print all messages at once
            if messages:
                console.print(JSON(json.dumps(messages, indent=2, default=str)))
            else:
                console.print("[yellow]No messages found[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[dim]Stopped[/dim]")


def _display_table(client, topic: str, options: ConsumeOptions, follow: bool):
    """Display messages as a table."""
    table = Table(title=f"Messages from {topic}")
    table.add_column("Offset", style="cyan", width=10)
    table.add_column("Part", style="magenta", width=5)
    table.add_column("Timestamp", style="green", width=20)
    table.add_column("Key", style="yellow", width=15)
    table.add_column("Value", style="white")

    try:
        for msg in client.consume(topic, options):
            value_str = json.dumps(msg.value, default=str) if isinstance(msg.value, dict) else str(msg.value)

            table.add_row(
                str(msg.offset),
                str(msg.partition),
                _format_timestamp(msg.timestamp),
                _truncate(str(msg.key) if msg.key else "-", 15),
                _truncate(value_str, 60),
            )

            if follow:
                # Re-render table in follow mode
                console.clear()
                console.print(table)

        if not follow:
            console.print(table)

    except KeyboardInterrupt:
        console.print("\n[dim]Stopped[/dim]")
        console.print(table)


def _display_raw(client, topic: str, options: ConsumeOptions):
    """Display messages as raw JSON lines."""
    try:
        for msg in client.consume(topic, options):
            print(json.dumps(msg.to_dict(), default=str))

    except KeyboardInterrupt:
        pass
