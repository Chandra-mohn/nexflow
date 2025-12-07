"""
Resilience Generator Mixin

Generates Flink resilience code from L1 resilience declarations.
"""

from typing import Set, List

from backend.ast import proc_ast as ast


class ResilienceGeneratorMixin:
    """
    Mixin for generating Flink resilience configuration.

    Generates:
    - Checkpoint configuration
    - Error handling with side outputs
    - Backpressure alerting configuration
    """

    def generate_resilience_code(self, process: ast.ProcessDefinition) -> str:
        """Generate resilience configuration code for a process."""
        if not process.resilience:
            return ""

        lines = []

        # Checkpoint configuration
        if process.resilience.checkpoint:
            lines.append(self._generate_checkpoint_config(process.resilience.checkpoint))
            lines.append("")

        # Error handling
        if process.resilience.error:
            lines.append(self._generate_error_handling(process.resilience.error))
            lines.append("")

        # Backpressure configuration
        if process.resilience.backpressure:
            lines.append(self._generate_backpressure_config(process.resilience.backpressure))

        return '\n'.join(lines)

    def _generate_checkpoint_config(self, checkpoint: ast.CheckpointBlock) -> str:
        """Generate checkpoint configuration."""
        interval_ms = self._duration_to_ms(checkpoint.interval)
        storage = checkpoint.storage

        return f'''// Checkpoint Configuration
env.enableCheckpointing({interval_ms}, CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setCheckpointStorage("{storage}");
env.getCheckpointConfig().setMinPauseBetweenCheckpoints({interval_ms // 2});
env.getCheckpointConfig().setTolerableCheckpointFailureNumber(3);
env.getCheckpointConfig().setExternalizedCheckpointCleanup(
    CheckpointConfig.ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION
);'''

    def _generate_error_handling(self, error_block: ast.ErrorBlock) -> str:
        """Generate error handling code."""
        lines = ["// Error Handling Configuration"]

        for handler in error_block.handlers:
            lines.append(self._generate_error_handler(handler))

        return '\n'.join(lines)

    def _generate_error_handler(self, handler: ast.ErrorHandler) -> str:
        """Generate code for a single error handler."""
        error_type = handler.error_type.value
        action = handler.action

        if action.action_type == ast.ErrorActionType.DEAD_LETTER:
            target = action.target or "dlq"
            return f'''// On {error_type} error: send to dead letter queue "{target}"
private static final OutputTag<FailedRecord> {self._to_camel_case(error_type)}DlqTag =
    new OutputTag<FailedRecord>("{target}") {{}};'''

        elif action.action_type == ast.ErrorActionType.RETRY:
            retry_count = action.retry_count or 3
            return f'''// On {error_type} error: retry {retry_count} times
// Configure in ProcessFunction with retry logic'''

        elif action.action_type == ast.ErrorActionType.SKIP:
            return f'''// On {error_type} error: skip record
// Handled via try-catch in ProcessFunction'''

        else:
            return f"// On {error_type} error: {action.action_type.value}"

    def _generate_backpressure_config(self, backpressure: ast.BackpressureBlock) -> str:
        """Generate backpressure configuration."""
        strategy = backpressure.strategy.value
        lines = [f"// Backpressure Strategy: {strategy}"]

        if strategy == "drop":
            lines.append("// Configured via buffer timeout and dropping policy")
            lines.append("env.setBufferTimeout(100);")

        elif strategy == "sample":
            rate = backpressure.sample_rate or 0.1
            lines.append(f"// Sample rate: {rate * 100}%")
            lines.append(f"// Apply .filter(record -> Math.random() < {rate}) under backpressure")

        elif strategy == "pause":
            lines.append("// Pause strategy: relies on Flink's natural backpressure")

        if backpressure.alert:
            alert_ms = self._duration_to_ms(backpressure.alert.after)
            lines.append(f"// Alert after {alert_ms}ms of backpressure")
            lines.append("// Configure via Flink metrics and alerting system")

        return '\n'.join(lines)

    def _duration_to_ms(self, duration: ast.Duration) -> int:
        """Convert Duration to milliseconds."""
        multipliers = {'ms': 1, 's': 1000, 'm': 60000, 'h': 3600000, 'd': 86400000}
        return duration.value * multipliers.get(duration.unit, 1)

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        parts = name.split('_')
        return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])

    def get_resilience_imports(self) -> Set[str]:
        """Get required imports for resilience generation."""
        return {
            'org.apache.flink.streaming.api.CheckpointingMode',
            'org.apache.flink.streaming.api.environment.CheckpointConfig',
            'org.apache.flink.util.OutputTag',
        }
