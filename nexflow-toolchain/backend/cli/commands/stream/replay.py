# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow Replay Command

Replay messages from one Kafka topic to another with optional filtering and transformation.
Supports time-based selection and rate limiting.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table

from backend.stream.config import KafkaConfig
from backend.stream.client import create_client, ConsumeOptions
from backend.stream.decoder import MessageDecoder
from backend.stream.filter import matches_filter


console = Console()


def _parse_timestamp(ts_str: str) -> Optional[int]:
    """Parse ISO timestamp to milliseconds since epoch."""
    if not ts_str:
        return None

    try:
        # Try ISO format
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return int(dt.timestamp() * 1000)
    except ValueError:
        # Try date-only format
        try:
            dt = datetime.strptime(ts_str, "%Y-%m-%d")
            return int(dt.timestamp() * 1000)
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {ts_str}. Use ISO format (2025-01-15T10:30:00Z)")


def _apply_transform(record: Dict[str, Any], transform_expr: str) -> Dict[str, Any]:
    """Apply a simple field transformation expression."""
    # Parse transform expressions like "field = 'value'" or "field = MASKED"
    result = record.copy()

    for part in transform_expr.split(','):
        part = part.strip()
        if '=' not in part:
            continue

        field, value = part.split('=', 1)
        field = field.strip()
        value = value.strip().strip("'\"")

        # Handle nested fields
        parts = field.split('.')
        obj = result
        for p in parts[:-1]:
            if p not in obj:
                obj[p] = {}
            obj = obj[p]

        obj[parts[-1]] = value

    return result


@click.command()
@click.argument("source_topic")
@click.argument("target_topic")
@click.option("--profile", "-p", default=None,
              help="Kafka cluster profile (default: from config)")
@click.option("--from-offset", default="earliest",
              help="Start offset: 'earliest', 'latest', or numeric (default: earliest)")
@click.option("--to-offset", default="latest",
              help="End offset: 'latest' or numeric (default: latest)")
@click.option("--from-time", default=None,
              help="Start timestamp (ISO format, e.g., 2025-01-15T00:00:00Z)")
@click.option("--to-time", default=None,
              help="End timestamp (ISO format, e.g., 2025-01-15T12:00:00Z)")
@click.option("--filter", "filter_expr", default=None,
              help="SQL-like filter expression")
@click.option("--transform", default=None,
              help="Field transformation expression (e.g., \"customer_id = 'ANONYMIZED'\")")
@click.option("--dry-run", is_flag=True,
              help="Preview without actually sending messages")
@click.option("--rate-limit", type=int, default=None,
              help="Maximum messages per second")
@click.option("--batch-size", type=int, default=100,
              help="Batch size for sending (default: 100)")
@click.option("--limit", "-n", type=int, default=None,
              help="Maximum messages to replay")
@click.option("--confirm/--no-confirm", default=True,
              help="Require confirmation before replay (default: true)")
@click.pass_context
def replay(
    ctx: click.Context,
    source_topic: str,
    target_topic: str,
    profile: Optional[str],
    from_offset: str,
    to_offset: str,
    from_time: Optional[str],
    to_time: Optional[str],
    filter_expr: Optional[str],
    transform: Optional[str],
    dry_run: bool,
    rate_limit: Optional[int],
    batch_size: int,
    limit: Optional[int],
    confirm: bool,
):
    """
    Replay messages from source topic to target topic.

    Copies messages with optional filtering, transformation, and rate limiting.
    Useful for populating dev/test environments or reprocessing data.

    \b
    Examples:
        nexflow replay orders-prod orders-dev --profile dev
        nexflow replay orders-prod orders-dev --from-time "2025-01-15T00:00:00Z" --to-time "2025-01-15T12:00:00Z"
        nexflow replay orders-prod orders-dev --filter "customer_id = 'C123'"
        nexflow replay orders-prod orders-dev --dry-run --limit 10
        nexflow replay orders-prod orders-dev --rate-limit 100
        nexflow replay orders-prod orders-dev --transform "customer_id = 'ANONYMIZED'"
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        # Load Kafka configuration
        config_path = Path.cwd() / "nexflow.toml"
        kafka_config = KafkaConfig.from_toml(config_path)

        # Get profile
        kafka_profile = kafka_config.get_profile(profile)

        # Parse timestamps
        start_ts = _parse_timestamp(from_time) if from_time else None
        end_ts = _parse_timestamp(to_time) if to_time else None

        # Create client (without PII masking for replay)
        kafka_profile.pii_mask = False
        client = create_client(kafka_config, profile)

        # Show connection info
        if verbose:
            console.print(f"[dim]Connecting to {kafka_profile.bootstrap_servers}...[/dim]")

        # Get source topic metadata
        try:
            source_meta = client.get_topic_metadata(source_topic)
            total_available = sum(high - low for low, high in source_meta.partition_offsets.values())
        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to get source topic metadata: {e}")
            sys.exit(3)

        # Estimate message count
        estimated_count = limit if limit else total_available

        # Display replay configuration
        table = Table(title="Replay Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Source", f"{source_topic} ({kafka_profile.name} cluster)")
        table.add_row("Target", target_topic)
        table.add_row("Offset Range", f"{from_offset} → {to_offset}")

        if from_time or to_time:
            table.add_row("Time Range", f"{from_time or 'start'} → {to_time or 'now'}")

        if filter_expr:
            table.add_row("Filter", filter_expr)

        if transform:
            table.add_row("Transform", transform)

        table.add_row("Estimated Messages", f"~{estimated_count:,}")

        if rate_limit:
            table.add_row("Rate Limit", f"{rate_limit} msg/s")

        if dry_run:
            table.add_row("Mode", "[yellow]DRY RUN (no messages will be sent)[/yellow]")

        console.print(table)
        console.print()

        # Confirmation
        if confirm and not dry_run:
            if not click.confirm("Proceed with replay?"):
                console.print("[yellow]Cancelled[/yellow]")
                return

        # Configure consume options
        options = ConsumeOptions(
            limit=limit if limit else estimated_count,
            offset=from_offset,
            filter_expr=filter_expr,
            timeout_seconds=60,
            follow=False,
        )

        # Replay messages
        sent = 0
        skipped = 0
        errors = 0
        messages_batch = []
        last_send_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Replaying...", total=estimated_count)

            for msg in client.consume(source_topic, options):
                # Filter by timestamp if specified
                if start_ts and msg.timestamp and msg.timestamp < start_ts:
                    continue
                if end_ts and msg.timestamp and msg.timestamp > end_ts:
                    continue

                # Apply transformation
                value = msg.value
                if transform and isinstance(value, dict):
                    value = _apply_transform(value, transform)

                if dry_run:
                    # Just count in dry run mode
                    sent += 1
                    progress.update(task, advance=1, description=f"Previewing... ({sent:,} messages)")
                else:
                    # Add to batch
                    messages_batch.append(value)

                    # Send batch when full
                    if len(messages_batch) >= batch_size:
                        try:
                            client.produce(target_topic, messages_batch)
                            sent += len(messages_batch)
                            messages_batch = []

                            # Rate limiting
                            if rate_limit:
                                elapsed = time.time() - last_send_time
                                expected_time = batch_size / rate_limit
                                if elapsed < expected_time:
                                    time.sleep(expected_time - elapsed)
                                last_send_time = time.time()

                        except Exception as e:
                            errors += len(messages_batch)
                            messages_batch = []
                            if verbose:
                                console.print(f"[red]Send error:[/red] {e}")

                progress.update(task, advance=1, description=f"Replaying... ({sent:,} sent)")

                if limit and sent >= limit:
                    break

            # Send remaining batch
            if messages_batch and not dry_run:
                try:
                    client.produce(target_topic, messages_batch)
                    sent += len(messages_batch)
                except Exception as e:
                    errors += len(messages_batch)
                    if verbose:
                        console.print(f"[red]Send error:[/red] {e}")

        # Summary
        console.print()
        if dry_run:
            console.print(f"[green]✓[/green] Dry run complete: {sent:,} messages would be replayed")
        else:
            console.print(f"[green]✓[/green] Replay complete: {sent:,} messages sent")

        if skipped > 0:
            console.print(f"[yellow]⚠[/yellow] {skipped:,} messages skipped (filtered or out of time range)")

        if errors > 0:
            console.print(f"[red]✗[/red] {errors:,} messages failed to send")

    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        sys.exit(2)
    except RuntimeError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        sys.exit(3)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        console.print(f"[dim]Sent {sent:,} messages before cancellation[/dim]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)
