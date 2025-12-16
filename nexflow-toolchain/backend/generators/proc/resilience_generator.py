# Nexflow DSL Toolchain
# Author: Chandra Mohn

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
        """Generate code for a single error handler.

        Supports all error types including correlation_failure:
        - transform_failure: Errors during transformation
        - lookup_failure: Errors during async enrichment lookups
        - rule_failure: Errors during rule evaluation
        - correlation_failure: Errors during await/hold correlation (timeout, mismatch)
        """
        error_type = handler.error_type.value
        action = handler.action
        error_tag_name = self._to_camel_case(error_type) + "DlqTag"

        if action.action_type == ast.ErrorActionType.DEAD_LETTER:
            target = action.target or "dlq"

            # Correlation failure has special handling for timeout and mismatch
            if error_type == "correlation_failure":
                return f'''// On {error_type} error: send to dead letter queue "{target}"
// Captures: await timeouts, hold completion failures, match mismatches
private static final OutputTag<CorrelationFailure> {error_tag_name} =
    new OutputTag<CorrelationFailure>("{target}") {{}};

// In KeyedCoProcessFunction/KeyedProcessFunction:
// ctx.output({error_tag_name}, CorrelationFailure.timeout(event, "await_timeout"));
// ctx.output({error_tag_name}, CorrelationFailure.mismatch(event, "no_matching_buffer"));'''
            else:
                return f'''// On {error_type} error: send to dead letter queue "{target}"
private static final OutputTag<FailedRecord> {error_tag_name} =
    new OutputTag<FailedRecord>("{target}") {{}};'''

        elif action.action_type == ast.ErrorActionType.RETRY:
            retry_count = action.retry_count or 3
            delay_ms = 1000  # Default 1 second delay

            # Generate actual retry logic with exponential backoff
            if error_type == "correlation_failure":
                return f'''// On {error_type} error: retry {retry_count} times with exponential backoff
// Correlation retry: re-register timer for await, re-check buffer for hold
private static final int {self._to_upper_snake(error_type)}_MAX_RETRIES = {retry_count};
private static final long {self._to_upper_snake(error_type)}_RETRY_DELAY_MS = {delay_ms};

// In processElement:
// int retryCount = retryState.value() != null ? retryState.value() : 0;
// if (retryCount < {self._to_upper_snake(error_type)}_MAX_RETRIES) {{
//     retryState.update(retryCount + 1);
//     long delay = {self._to_upper_snake(error_type)}_RETRY_DELAY_MS * (1L << retryCount);  // Exponential backoff
//     ctx.timerService().registerProcessingTimeTimer(ctx.timerService().currentProcessingTime() + delay);
// }} else {{
//     // Max retries exceeded - emit to DLQ or skip
// }}'''
            else:
                return f'''// On {error_type} error: retry {retry_count} times with exponential backoff
private static final int {self._to_upper_snake(error_type)}_MAX_RETRIES = {retry_count};
private static final long {self._to_upper_snake(error_type)}_RETRY_DELAY_MS = {delay_ms};

// In processElement with try-catch:
// for (int attempt = 0; attempt <= {self._to_upper_snake(error_type)}_MAX_RETRIES; attempt++) {{
//     try {{
//         // Operation that may fail
//         break;
//     }} catch (Exception e) {{
//         if (attempt == {self._to_upper_snake(error_type)}_MAX_RETRIES) throw e;
//         Thread.sleep({self._to_upper_snake(error_type)}_RETRY_DELAY_MS * (1L << attempt));
//     }}
// }}'''

        elif action.action_type == ast.ErrorActionType.SKIP:
            if error_type == "correlation_failure":
                return f'''// On {error_type} error: skip and continue processing
// For correlation: emit partial result or skip entirely
// In KeyedCoProcessFunction:
// try {{
//     // Correlation logic
// }} catch (CorrelationException e) {{
//     LOG.warn("Correlation failed for key {{}}, skipping", ctx.getCurrentKey());
//     // Optionally emit metrics: correlationSkippedCounter.inc();
// }}'''
            else:
                return f'''// On {error_type} error: skip record
// Handled via try-catch in ProcessFunction'''

        else:
            return f"// On {error_type} error: {action.action_type.value}"

    def _to_upper_snake(self, name: str) -> str:
        """Convert snake_case to UPPER_SNAKE_CASE."""
        return name.upper()

    def _generate_backpressure_config(self, backpressure: ast.BackpressureBlock) -> str:
        """Generate backpressure configuration with alerting support.

        Strategies:
        - drop: Drop records when backpressure detected
        - sample: Sample records at specified rate under backpressure
        - pause/block: Rely on Flink's natural backpressure

        Alerting:
        - Configures metrics reporter for backpressure duration
        - Generates alert when threshold exceeded
        """
        strategy = backpressure.strategy.value
        lines = [f"// Backpressure Strategy: {strategy}"]

        if strategy == "drop":
            lines.extend([
                "// Drop strategy: configure buffer timeout for graceful degradation",
                "env.setBufferTimeout(100);  // 100ms buffer timeout",
                "",
                "// To enable dropping under backpressure, use:",
                "// stream.filter(record -> !isBackpressured()).name(\"backpressure-filter\");",
                "",
                "// Backpressure detection helper:",
                "// private boolean isBackpressured() {",
                "//     return getRuntimeContext().getMetricGroup()",
                "//         .gauge(\"backPressuredTimeMsPerSecond\", () -> ...) > threshold;",
                "// }",
            ])

        elif strategy == "sample":
            rate = backpressure.sample_rate or 0.1
            lines.extend([
                f"// Sample strategy: {rate * 100}% sampling rate under backpressure",
                "",
                f"// Apply sampling filter:",
                f"// DataStream<T> sampledStream = stream",
                f"//     .filter(record -> !isBackpressured() || Math.random() < {rate})",
                f"//     .name(\"backpressure-sampler\");",
            ])

        elif strategy == "pause" or strategy == "block":
            lines.extend([
                "// Pause/Block strategy: rely on Flink's natural backpressure propagation",
                "// No additional configuration needed - Flink handles this automatically",
                "// Upstream operators will slow down when downstream is backpressured",
            ])

        # Generate alerting configuration
        if backpressure.alert:
            alert_ms = self._duration_to_ms(backpressure.alert.after)
            alert_seconds = alert_ms / 1000
            lines.extend([
                "",
                f"// Backpressure Alerting: trigger after {alert_seconds}s of sustained backpressure",
                "// ================================================================================",
                "",
                "// 1. Register backpressure duration metric",
                "private transient Counter backpressureAlertCounter;",
                "private transient Gauge<Long> backpressureDurationGauge;",
                "private long backpressureStartTime = 0;",
                "",
                "@Override",
                "public void open(Configuration parameters) {",
                "    MetricGroup metrics = getRuntimeContext().getMetricGroup();",
                "    backpressureAlertCounter = metrics.counter(\"backpressureAlerts\");",
                "    backpressureDurationGauge = metrics.gauge(\"backpressureDurationMs\", () -> {",
                "        if (backpressureStartTime > 0) {",
                "            return System.currentTimeMillis() - backpressureStartTime;",
                "        }",
                "        return 0L;",
                "    });",
                "}",
                "",
                "// 2. Check backpressure in processElement",
                "private void checkBackpressure(Context ctx) {",
                "    // Detect backpressure via output availability or watermark lag",
                "    boolean isBackpressured = detectBackpressure();",
                "",
                "    if (isBackpressured && backpressureStartTime == 0) {",
                "        backpressureStartTime = System.currentTimeMillis();",
                "    } else if (!isBackpressured) {",
                "        backpressureStartTime = 0;",
                "    }",
                "",
                f"    // Alert if backpressure exceeds threshold",
                f"    if (backpressureStartTime > 0 && ",
                f"        System.currentTimeMillis() - backpressureStartTime > {alert_ms}) {{",
                "        backpressureAlertCounter.inc();",
                f"        LOG.warn(\"Backpressure alert: sustained for > {alert_seconds}s\");",
                "        // Optional: emit alert event to monitoring topic",
                "        // ctx.output(alertTag, new BackpressureAlert(...));",
                "    }",
                "}",
                "",
                "// 3. Flink metrics configuration (add to flink-conf.yaml):",
                "// metrics.reporters: prometheus",
                "// metrics.reporter.prometheus.class: org.apache.flink.metrics.prometheus.PrometheusReporter",
                "",
                "// 4. Prometheus alert rule example:",
                "// - alert: FlinkBackpressureAlert",
                f"//   expr: flink_taskmanager_job_task_backpressureDurationMs > {alert_ms}",
                "//   for: 30s",
                "//   labels:",
                "//     severity: warning",
                "//   annotations:",
                f"//     summary: \"Flink backpressure detected for > {alert_seconds}s\"",
            ])

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
