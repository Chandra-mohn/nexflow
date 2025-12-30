# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow Decode Command

Decode binary-serialized Kafka messages (Avro, Protobuf) to human-readable JSON/YAML.
Supports both online (schema registry) and offline (local schema file) modes.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

from backend.stream.config import KafkaConfig
from backend.stream.client import create_client, ConsumeOptions
from backend.stream.decoder import MessageDecoder
from backend.ast.serialization import SerializationFormat


console = Console()


@click.command()
@click.argument("topic")
@click.option("--profile", "-p", default=None,
              help="Kafka cluster profile (default: from config)")
@click.option("--from", "from_format",
              type=click.Choice(["avro", "protobuf", "confluent-avro", "auto"]),
              default="auto", help="Source format (default: auto)")
@click.option("--to", "to_format",
              type=click.Choice(["json", "yaml"]),
              default="json", help="Target format (default: json)")
@click.option("--schema", type=click.Path(exists=True),
              help="Local schema file path (for offline mode)")
@click.option("--registry", default=None,
              help="Schema registry URL (overrides config)")
@click.option("--output", "-o", type=click.Path(),
              help="Output file path (default: stdout)")
@click.option("--pretty/--no-pretty", default=True,
              help="Pretty-print output (default: true)")
@click.option("--limit", "-n", type=int, default=None,
              help="Number of messages to decode (default: all available)")
@click.option("--offset", default="earliest",
              help="Start offset: 'earliest', 'latest', or numeric (default: earliest)")
@click.option("--partition", type=int, default=None,
              help="Specific partition to read from")
@click.pass_context
def decode(
    ctx: click.Context,
    topic: str,
    profile: Optional[str],
    from_format: str,
    to_format: str,
    schema: Optional[str],
    registry: Optional[str],
    output: Optional[str],
    pretty: bool,
    limit: Optional[int],
    offset: str,
    partition: Optional[int],
):
    """
    Decode binary Kafka messages to human-readable format.

    Converts Avro, Protobuf, or Confluent Avro messages to JSON or YAML.
    Supports both online (schema registry) and offline (local schema) modes.

    \b
    Examples:
        nexflow decode orders-avro --to json
        nexflow decode orders-avro --schema ./schemas/order.avsc --to json
        nexflow decode orders-avro --to json --output orders.json
        nexflow decode events-proto --from protobuf --schema ./protos/event.proto
        nexflow decode orders-avro --profile prod --registry https://prod-registry:8081
        nexflow decode orders-avro --limit 1000 --output sample.json
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        # Load Kafka configuration
        config_path = Path.cwd() / "nexflow.toml"
        kafka_config = KafkaConfig.from_toml(config_path)

        # Determine registry URL
        registry_url = registry
        if not registry_url and kafka_config.schema_registry:
            registry_url = kafka_config.schema_registry.url

        # Determine format
        fmt = None
        if from_format != "auto":
            format_map = {
                "avro": SerializationFormat.AVRO,
                "confluent-avro": SerializationFormat.CONFLUENT_AVRO,
                "protobuf": SerializationFormat.PROTOBUF,
            }
            fmt = format_map.get(from_format)

        # Validate schema requirements
        if from_format in ("avro", "protobuf") and not schema:
            console.print(f"[red]Error:[/red] --schema required for {from_format} format in offline mode")
            console.print(f"  Use --from confluent-avro for schema registry mode")
            sys.exit(2)

        if from_format == "confluent-avro" and not registry_url:
            console.print("[red]Error:[/red] Schema registry URL required for confluent-avro format")
            console.print("  Configure in nexflow.toml or use --registry option")
            sys.exit(2)

        # Create decoder
        schema_path = Path(schema) if schema else None
        decoder = MessageDecoder(
            format=fmt,
            schema_path=schema_path,
            registry_url=registry_url,
        )

        # Create client (with PII masking disabled for decode - raw export)
        kafka_profile = kafka_config.get_profile(profile)
        kafka_profile.pii_mask = False  # Don't mask for decode operations

        client = create_client(kafka_config, profile, decoder)

        # Show connection info
        if verbose:
            console.print(f"[dim]Connecting to {kafka_profile.bootstrap_servers}...[/dim]")
            console.print(f"[dim]Source format: {from_format}[/dim]")
            console.print(f"[dim]Target format: {to_format}[/dim]")
            if schema:
                console.print(f"[dim]Using local schema: {schema}[/dim]")
            elif registry_url:
                console.print(f"[dim]Using schema registry: {registry_url}[/dim]")

        # Get topic metadata for progress tracking
        try:
            metadata = client.get_topic_metadata(topic)
            total_messages = sum(high - low for low, high in metadata.partition_offsets.values())
            if verbose:
                console.print(f"[dim]Topic: {metadata.name} (~{total_messages} messages available)[/dim]")
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to get topic metadata: {e}")
            sys.exit(3)

        # Configure consume options
        max_messages = limit if limit else total_messages
        options = ConsumeOptions(
            limit=max_messages,
            offset=offset,
            partition=partition,
            timeout_seconds=60,
            follow=False,
        )

        # Collect decoded messages
        messages = []
        errors = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Decoding {topic}...", total=max_messages)

            for msg in client.consume(topic, options):
                messages.append(msg.to_dict())
                progress.update(task, advance=1)

                if limit and len(messages) >= limit:
                    break

        # Convert to target format
        if to_format == "yaml":
            try:
                import yaml
                output_content = yaml.dump(messages, default_flow_style=False, allow_unicode=True)
            except ImportError:
                console.print("[red]Error:[/red] PyYAML required for YAML output. Install with: pip install pyyaml")
                sys.exit(1)
        else:
            indent = 2 if pretty else None
            output_content = json.dumps(messages, indent=indent, default=str, ensure_ascii=False)

        # Write output
        if output:
            output_path = Path(output)
            output_path.write_text(output_content, encoding='utf-8')
            console.print(f"[green][OK][/green] Decoded {len(messages)} messages to {output_path}")
        else:
            print(output_content)

        if errors > 0:
            console.print(f"[yellow]⚠[/yellow] {errors} messages failed to decode", err=True)

    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(2)
    except RuntimeError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        sys.exit(3)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)
