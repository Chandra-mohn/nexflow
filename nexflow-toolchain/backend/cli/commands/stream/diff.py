# Nexflow DSL Toolchain
# Author: Chandra Mohn

"""
Nexflow Diff Command

Compare messages between Kafka topics, time ranges, or snapshots.
Identifies differences at message and field level.
"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from backend.stream.config import KafkaConfig
from backend.stream.client import create_client, ConsumeOptions
from backend.stream.decoder import DecodedMessage


console = Console()


@dataclass
class DiffResult:
    """Result of comparing two message sets."""
    left_only: List[str] = field(default_factory=list)  # Keys only in left
    right_only: List[str] = field(default_factory=list)  # Keys only in right
    matching: List[str] = field(default_factory=list)  # Keys that match
    different: List[Tuple[str, Dict, Dict]] = field(default_factory=list)  # (key, left, right)
    field_changes: Dict[str, int] = field(default_factory=lambda: defaultdict(int))  # field -> count


def _get_message_key(msg: DecodedMessage, key_fields: Optional[List[str]] = None) -> str:
    """Extract the comparison key from a message."""
    if key_fields and isinstance(msg.value, dict):
        key_parts = []
        for field in key_fields:
            parts = field.split('.')
            value = msg.value
            for p in parts:
                if isinstance(value, dict) and p in value:
                    value = value[p]
                else:
                    value = None
                    break
            key_parts.append(str(value) if value is not None else "null")
        return ":".join(key_parts)

    return str(msg.key) if msg.key else f"offset-{msg.partition}-{msg.offset}"


def _compare_values(left: Any, right: Any, path: str = "") -> List[Tuple[str, Any, Any]]:
    """Compare two values and return list of differences as (path, left_val, right_val)."""
    differences = []

    if type(left) != type(right):
        differences.append((path or "root", left, right))
    elif isinstance(left, dict):
        all_keys = set(left.keys()) | set(right.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in left:
                differences.append((new_path, None, right[key]))
            elif key not in right:
                differences.append((new_path, left[key], None))
            else:
                differences.extend(_compare_values(left[key], right[key], new_path))
    elif isinstance(left, list):
        if len(left) != len(right):
            differences.append((path, f"[{len(left)} items]", f"[{len(right)} items]"))
        else:
            for i, (l, r) in enumerate(zip(left, right)):
                differences.extend(_compare_values(l, r, f"{path}[{i}]"))
    elif left != right:
        differences.append((path or "root", left, right))

    return differences


def _collect_messages(
    client,
    topic: str,
    options: ConsumeOptions,
    key_fields: Optional[List[str]],
    progress,
    task,
    label: str,
) -> Dict[str, DecodedMessage]:
    """Collect messages from a topic into a keyed dictionary."""
    messages = {}

    for msg in client.consume(topic, options):
        key = _get_message_key(msg, key_fields)
        messages[key] = msg
        progress.update(task, advance=1, description=f"Reading {label}... ({len(messages):,})")

    return messages


def _format_value(value: Any, max_len: int = 40) -> str:
    """Format a value for display."""
    if value is None:
        return "[dim]null[/dim]"
    if isinstance(value, dict):
        s = json.dumps(value, default=str)
    elif isinstance(value, list):
        s = json.dumps(value, default=str)
    else:
        s = str(value)

    if len(s) > max_len:
        return s[:max_len - 3] + "..."
    return s


@click.command()
@click.argument("source1")
@click.argument("source2")
@click.option("--profile", "-p", default=None,
              help="Kafka cluster profile (default: from config)")
@click.option("--key", "key_fields", default=None,
              help="Field(s) to use as comparison key (comma-separated)")
@click.option("--ignore", "ignore_fields", default=None,
              help="Fields to ignore in comparison (comma-separated)")
@click.option("--output", "-o", type=click.Path(),
              help="Output file for diff report")
@click.option("--format", "-f", "output_format",
              type=click.Choice(["json", "table", "summary"]),
              default="summary", help="Output format (default: summary)")
@click.option("--limit", "-n", type=int, default=1000,
              help="Max messages to compare (default: 1000)")
@click.option("--offset", default="earliest",
              help="Start offset (default: earliest)")
@click.option("--from-time", default=None,
              help="Start timestamp for comparison (ISO format)")
@click.option("--to-time", default=None,
              help="End timestamp for comparison (ISO format)")
@click.pass_context
def diff(
    ctx: click.Context,
    source1: str,
    source2: str,
    profile: Optional[str],
    key_fields: Optional[str],
    ignore_fields: Optional[str],
    output: Optional[str],
    output_format: str,
    limit: int,
    offset: str,
    from_time: Optional[str],
    to_time: Optional[str],
):
    """
    Compare messages between two Kafka topics.

    Identifies messages that exist only in one topic, messages that match,
    and messages with the same key but different values.

    \b
    Examples:
        nexflow diff orders-v1 orders-v2 --key order_id
        nexflow diff orders-dev orders-staging --key order_id --ignore updated_at,created_at
        nexflow diff orders-avro orders-avro --from-time "2025-01-14" --to-time "2025-01-15" --key order_id
        nexflow diff orders-dev orders-prod --key order_id --output diff-report.json --format json
    """
    verbose = ctx.obj.get("verbose", False) if ctx.obj else False

    try:
        # Load Kafka configuration
        config_path = Path.cwd() / "nexflow.toml"
        kafka_config = KafkaConfig.from_toml(config_path)

        # Parse key and ignore fields
        keys = [k.strip() for k in key_fields.split(',')] if key_fields else None
        ignores = set(f.strip() for f in ignore_fields.split(',')) if ignore_fields else set()

        # Get profile (without PII masking for comparison)
        kafka_profile = kafka_config.get_profile(profile)
        kafka_profile.pii_mask = False

        # Create client
        client = create_client(kafka_config, profile)

        # Show connection info
        if verbose:
            console.print(f"[dim]Connecting to {kafka_profile.bootstrap_servers}...[/dim]")
            console.print(f"[dim]Comparing: {source1} vs {source2}[/dim]")
            if keys:
                console.print(f"[dim]Key fields: {', '.join(keys)}[/dim]")
            if ignores:
                console.print(f"[dim]Ignoring: {', '.join(ignores)}[/dim]")

        # Configure consume options
        options = ConsumeOptions(
            limit=limit,
            offset=offset,
            timeout_seconds=60,
            follow=False,
        )

        # Collect messages from both sources
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True,
        ) as progress:
            task1 = progress.add_task(f"Reading {source1}...", total=limit)
            left_messages = _collect_messages(client, source1, options, keys, progress, task1, source1)

            task2 = progress.add_task(f"Reading {source2}...", total=limit)
            right_messages = _collect_messages(client, source2, options, keys, progress, task2, source2)

        # Compare messages
        result = DiffResult()
        left_keys = set(left_messages.keys())
        right_keys = set(right_messages.keys())

        # Only in left
        result.left_only = sorted(left_keys - right_keys)

        # Only in right
        result.right_only = sorted(right_keys - left_keys)

        # In both
        common_keys = left_keys & right_keys
        for key in sorted(common_keys):
            left_val = left_messages[key].value
            right_val = right_messages[key].value

            # Remove ignored fields before comparison
            if ignores and isinstance(left_val, dict) and isinstance(right_val, dict):
                left_val = {k: v for k, v in left_val.items() if k not in ignores}
                right_val = {k: v for k, v in right_val.items() if k not in ignores}

            differences = _compare_values(left_val, right_val)

            if differences:
                result.different.append((key, left_messages[key].value, right_messages[key].value))
                for field_path, _, _ in differences:
                    result.field_changes[field_path] += 1
            else:
                result.matching.append(key)

        # Output results
        if output_format == "json":
            _output_json(result, source1, source2, output)
        elif output_format == "table":
            _output_table(result, source1, source2, output)
        else:
            _output_summary(result, source1, source2, left_messages, right_messages, output)

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


def _output_summary(result: DiffResult, source1: str, source2: str,
                   left_messages: Dict, right_messages: Dict, output: Optional[str]):
    """Output summary format."""
    total_left = len(left_messages)
    total_right = len(right_messages)
    total_compared = len(result.matching) + len(result.different)

    lines = []
    lines.append(f"Diff Report: {source1} vs {source2}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Messages analyzed: {total_left:,} vs {total_right:,}")

    if result.matching:
        pct = len(result.matching) / total_compared * 100 if total_compared else 0
        lines.append(f"  ✓ Matching: {len(result.matching):,} ({pct:.1f}%)")

    if result.different:
        pct = len(result.different) / total_compared * 100 if total_compared else 0
        lines.append(f"  ✗ Different: {len(result.different):,} ({pct:.1f}%)")

    if result.right_only:
        lines.append(f"  + Only in {source2}: {len(result.right_only):,}")

    if result.left_only:
        lines.append(f"  - Only in {source1}: {len(result.left_only):,}")

    # Field-level differences
    if result.field_changes:
        lines.append("")
        lines.append("Field-level differences:")
        for field, count in sorted(result.field_changes.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  • {field}: {count} changes")

    # Sample differences
    if result.different:
        lines.append("")
        lines.append("Sample Differences:")

        table = Table()
        table.add_column("Key", style="cyan", width=15)
        table.add_column(source1, style="yellow", width=30)
        table.add_column(source2, style="green", width=30)

        for key, left, right in result.different[:5]:
            diffs = _compare_values(left, right)
            if diffs:
                field, l_val, r_val = diffs[0]
                table.add_row(
                    key[:15],
                    f"{field}: {_format_value(l_val)}",
                    f"{field}: {_format_value(r_val)}",
                )

        console.print("\n".join(lines))
        console.print(table)
    else:
        console.print("\n".join(lines))

    if output:
        Path(output).write_text("\n".join(lines))
        console.print(f"\n[dim]Report saved to {output}[/dim]")


def _output_table(result: DiffResult, source1: str, source2: str, output: Optional[str]):
    """Output table format."""
    table = Table(title=f"Diff: {source1} vs {source2}")
    table.add_column("Status", style="bold", width=10)
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Details", style="white")

    for key in result.left_only[:10]:
        table.add_row("[red]-[/red]", key, f"Only in {source1}")

    for key in result.right_only[:10]:
        table.add_row("[green]+[/green]", key, f"Only in {source2}")

    for key, left, right in result.different[:10]:
        diffs = _compare_values(left, right)
        details = ", ".join(f"{f}: {_format_value(l)} → {_format_value(r)}" for f, l, r in diffs[:3])
        table.add_row("[yellow]~[/yellow]", key, details)

    console.print(table)

    if output:
        # Save as text
        with open(output, 'w') as f:
            f.write(f"Diff: {source1} vs {source2}\n")
            f.write("-" * 60 + "\n")
            for key in result.left_only:
                f.write(f"- {key}: Only in {source1}\n")
            for key in result.right_only:
                f.write(f"+ {key}: Only in {source2}\n")
            for key, left, right in result.different:
                f.write(f"~ {key}: Values differ\n")
        console.print(f"\n[dim]Report saved to {output}[/dim]")


def _output_json(result: DiffResult, source1: str, source2: str, output: Optional[str]):
    """Output JSON format."""
    report = {
        "sources": {
            "left": source1,
            "right": source2,
        },
        "summary": {
            "matching": len(result.matching),
            "different": len(result.different),
            "left_only": len(result.left_only),
            "right_only": len(result.right_only),
        },
        "field_changes": dict(result.field_changes),
        "left_only": result.left_only,
        "right_only": result.right_only,
        "differences": [
            {"key": key, "left": left, "right": right}
            for key, left, right in result.different
        ],
    }

    json_output = json.dumps(report, indent=2, default=str)

    if output:
        Path(output).write_text(json_output)
        console.print(f"[green]✓[/green] Report saved to {output}")
    else:
        print(json_output)
