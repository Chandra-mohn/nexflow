/**
 * ProcDSL - Process Orchestration Domain-Specific Language
 *
 * ANTLR4 Grammar for L1 Process Orchestration DSL
 *
 * Version: 0.4.0
 * Specification: ../L1-Process-Orchestration-DSL.md
 * Runtime Spec: ../L1-Runtime-Semantics.md
 *
 * This grammar defines the syntax for PROC-DSL, a controlled natural language
 * for defining streaming and batch data processing pipelines.
 *
 * SEMANTIC VALIDATION NOTES (enforced by compiler, not grammar):
 * - Every process MUST have at least one output: emit, route using, or aggregate
 * - Window blocks MUST be followed by aggregate
 * - Join requires exactly two aliased inputs
 * - Await requires exactly two receive blocks
 * - Batch mode cannot use watermark, window, or await
 * - Partition key field must exist in input schema
 * - Completion blocks require correlation field declaration
 * - Completion blocks require at least one emit to in the process
 * - Correlation field must exist in output schema
 */

grammar ProcDSL;

// ============================================================================
// PARSER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Top-Level Structure
// ----------------------------------------------------------------------------

program
    : processDefinition+ EOF
    ;

processDefinition
    : 'process' processName
        executionBlock?
        inputBlock
        processingBlock*
        correlationBlock?
        outputBlock?
        completionBlock?           // NEW: Completion event declarations
        stateBlock?
        resilienceBlock?
      'end'
    ;

processName
    : IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Execution Block
// ----------------------------------------------------------------------------

executionBlock
    : parallelismDecl?
      partitionDecl?
      timeDecl?
      modeDecl?
    ;

parallelismDecl
    : 'parallelism' 'hint'? INTEGER
    ;

partitionDecl
    : 'partition' 'by' fieldList          // Support multi-field partition keys
    ;

timeDecl
    : 'time' 'by' fieldPath
        watermarkDecl?
        lateDataDecl?
        latenessDecl?
    ;

watermarkDecl
    : 'watermark' 'delay' duration
    ;

lateDataDecl
    : 'late' 'data' 'to' IDENTIFIER
    ;

latenessDecl
    : 'allowed' 'lateness' duration
    ;

modeDecl
    : 'mode' modeType
    ;

modeType
    : 'stream'
    | 'batch'
    | 'micro_batch' duration
    ;

// ----------------------------------------------------------------------------
// Input Block
// ----------------------------------------------------------------------------

inputBlock
    : receiveDecl+
    ;

receiveDecl
    : 'receive' (IDENTIFIER 'from')? IDENTIFIER
        schemaDecl?
        projectClause?
        receiveAction?                        // Optional action: store or match
    ;

// Field projection - select subset of fields from large schemas
projectClause
    : 'project' fieldList                     // Include only these fields
    | 'project' 'except' fieldList            // Include all except these fields
    ;

schemaDecl
    : 'schema' IDENTIFIER
    ;

// Actions that can follow a receive declaration
receiveAction
    : storeAction
    | matchAction
    ;

storeAction
    : 'store' 'in' IDENTIFIER
    ;

matchAction
    : 'match' 'from' IDENTIFIER 'on' fieldList
    ;

// ----------------------------------------------------------------------------
// Processing Block
// ----------------------------------------------------------------------------

processingBlock
    : enrichDecl
    | transformDecl
    | routeDecl
    | aggregateDecl
    | windowDecl
    | joinDecl
    | mergeDecl                               // NEW: merge operation
    ;

enrichDecl
    : 'enrich' 'using' IDENTIFIER
        'on' fieldList                        // Support multi-field join keys
        selectClause?
    ;

selectClause
    : 'select' fieldList
    ;

transformDecl
    : 'transform' 'using' IDENTIFIER
    ;

routeDecl
    : 'route' 'using' IDENTIFIER
    ;

aggregateDecl
    : 'aggregate' 'using' IDENTIFIER
    ;

// NEW: Merge operation for combining streams
mergeDecl
    : 'merge' IDENTIFIER (',' IDENTIFIER)+    // Merge 2+ streams
        ('into' IDENTIFIER)?                   // Optional output alias
    ;

// ----------------------------------------------------------------------------
// Window Block
// ----------------------------------------------------------------------------

windowDecl
    : 'window' windowType duration windowOptions?
    ;

windowType
    : 'tumbling'
    | 'sliding' duration 'every'
    | 'session' 'gap'
    ;

windowOptions
    : latenessDecl? lateDataDecl?
    ;

// ----------------------------------------------------------------------------
// Join Block
// ----------------------------------------------------------------------------

joinDecl
    : 'join' IDENTIFIER 'with' IDENTIFIER
        'on' fieldList                        // Support multi-field join keys
        'within' duration
        joinType?
    ;

joinType
    : 'type' ('inner' | 'left' | 'right' | 'outer')
    ;

// ----------------------------------------------------------------------------
// Correlation Block (Await/Hold)
// ----------------------------------------------------------------------------

correlationBlock
    : awaitDecl
    | holdDecl
    ;

// Await: Event-driven correlation
// Waits for a triggering event to arrive that matches on correlation key
awaitDecl
    : 'await' IDENTIFIER
        'until' IDENTIFIER 'arrives'
            'matching' 'on' fieldList         // Support multi-field correlation keys
        'timeout' duration
            timeoutAction
    ;

// Hold: Buffer-based correlation
// Buffers records keyed by field(s), with optional completion condition
holdDecl
    : 'hold' IDENTIFIER ('in' IDENTIFIER)?    // Optional named buffer
        'keyed' 'by' fieldList                // Support multi-field buffer keys
        completionClause?                      // NEW: When to consider complete
        'timeout' duration
            timeoutAction
    ;

// NEW: Completion conditions for hold buffers
completionClause
    : 'complete' 'when' completionCondition
    ;

completionCondition
    : 'count' '>=' INTEGER                    // Complete when N items collected
    | 'marker' 'received'                     // Complete when marker event arrives
    | 'using' IDENTIFIER                      // L4 rule determines completion
    ;

timeoutAction
    : 'emit' 'to' IDENTIFIER
    | 'dead_letter' IDENTIFIER
    | 'skip'
    ;

// ----------------------------------------------------------------------------
// Output Block
// ----------------------------------------------------------------------------

outputBlock
    : outputDecl+
    ;

// Output can be emit or route (for fan-out routing decisions)
outputDecl
    : emitDecl
    | routeDecl                               // Route can appear in output context
    ;

emitDecl
    : 'emit' 'to' IDENTIFIER
        schemaDecl?
        fanoutDecl?
    ;

fanoutDecl
    : 'fanout' ('broadcast' | 'round_robin')
    ;

// ----------------------------------------------------------------------------
// Completion Event Block (Flink Sink Callback Pattern)
// ----------------------------------------------------------------------------

// Completion block contains one or more completion declarations
completionBlock
    : completionDecl+
    ;

// Completion event declaration: on commit or on commit failure
completionDecl
    : onCommitDecl
    | onCommitFailureDecl
    ;

// Success completion: emitted after successful sink write
onCommitDecl
    : 'on' 'commit'
        'emit' 'completion' 'to' IDENTIFIER
            correlationDecl
            includeDecl?
            schemaDecl?
    ;

// Failure completion: emitted when sink write fails
onCommitFailureDecl
    : 'on' 'commit' 'failure'
        'emit' 'completion' 'to' IDENTIFIER
            correlationDecl
            includeDecl?
            schemaDecl?
    ;

// Correlation field declaration (required)
correlationDecl
    : 'correlation' fieldPath
    ;

// Include additional fields in completion event (optional)
includeDecl
    : 'include' fieldList
    ;

// ----------------------------------------------------------------------------
// State Block
// ----------------------------------------------------------------------------

stateBlock
    : 'state' stateDecl+
    ;

stateDecl
    : usesDecl
    | localDecl
    | bufferDecl                              // NEW: Named buffer declaration
    ;

usesDecl
    : 'uses' IDENTIFIER
    ;

// Local state with optional TTL and cleanup strategy
localDecl
    : 'local' IDENTIFIER 'keyed' 'by' fieldList
        'type' stateType
        ttlDecl?                              // NEW: Time-to-live
        cleanupDecl?                          // NEW: Cleanup strategy
    ;

stateType
    : 'counter'
    | 'gauge'
    | 'map'
    | 'list'
    ;

// NEW: TTL declaration for state expiration
ttlDecl
    : 'ttl' ttlType? duration
    ;

ttlType
    : 'sliding'                               // TTL resets on each access
    | 'absolute'                              // TTL from creation time
    ;

// NEW: Cleanup strategy for expired state
cleanupDecl
    : 'cleanup' cleanupStrategy
    ;

cleanupStrategy
    : 'on_checkpoint'                         // Clean during checkpoint (default)
    | 'on_access'                             // Clean when state is accessed
    | 'background'                            // Continuous background cleanup
    ;

// NEW: Named buffer declaration for hold patterns
bufferDecl
    : 'buffer' IDENTIFIER 'keyed' 'by' fieldList
        'type' bufferType
        ttlDecl?
    ;

bufferType
    : 'fifo'                                  // First-in-first-out
    | 'lifo'                                  // Last-in-first-out
    | 'priority' 'by' fieldPath              // Priority queue by field
    ;

// ----------------------------------------------------------------------------
// Resilience Block
// ----------------------------------------------------------------------------

resilienceBlock
    : errorBlock?
      checkpointBlock?
      backpressureBlock?
    ;

errorBlock
    : 'on' 'error' errorHandler+
    ;

errorHandler
    : errorType errorAction
    ;

errorType
    : 'transform' 'failure'
    | 'lookup' 'failure'
    | 'rule' 'failure'
    | 'correlation' 'failure'
    ;

errorAction
    : 'dead_letter' IDENTIFIER
    | 'skip'
    | 'retry' INTEGER                         // Retry count (details in L5)
    ;

checkpointBlock
    : 'checkpoint' 'every' duration
        'to' IDENTIFIER
    ;

backpressureBlock
    : 'when' 'slow'
        'strategy' backpressureStrategy
        alertDecl?
    ;

backpressureStrategy
    : 'block'
    | 'drop'
    | 'sample' NUMBER
    ;

alertDecl
    : 'alert' 'after' duration
    ;

// ----------------------------------------------------------------------------
// Common Rules
// ----------------------------------------------------------------------------

fieldPath
    : IDENTIFIER ('.' IDENTIFIER)*
    ;

fieldList
    : fieldPath (',' fieldPath)*
    ;

duration
    : INTEGER timeUnit
    | DURATION_LITERAL
    ;

timeUnit
    : 'seconds' | 'second'
    | 'minutes' | 'minute'
    | 'hours'   | 'hour'
    | 'days'    | 'day'
    ;

// ============================================================================
// LEXER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Keywords (alphabetical for reference)
// ----------------------------------------------------------------------------

// Structure: process, end
// Input: receive, from, schema, project, except
// Output: emit, to, fanout, broadcast, round_robin
// Processing: transform, enrich, route, aggregate, merge, using, on, select
// Execution: parallelism, hint, partition, by, mode, stream, batch, micro_batch
// Time: time, watermark, delay, late, data, allowed, lateness
// Window: window, tumbling, sliding, session, gap, every
// Join: join, with, within, type, inner, left, right, outer
// Correlation: await, until, arrives, matching, timeout, hold, buffer, store, in, match, complete, when, count, marker, received
// Completion: on, commit, failure, completion, correlation, include
// State: state, uses, local, keyed, counter, gauge, map, list, ttl, sliding, absolute, cleanup, on_checkpoint, on_access, background, fifo, lifo, priority
// Resilience: on, error, failure, dead_letter, skip, retry, checkpoint, strategy, block, drop, sample, alert, after

// Note: Keywords are matched case-sensitively as lowercase

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

INTEGER
    : [0-9]+
    ;

NUMBER
    : [0-9]+ ('.' [0-9]+)?
    ;

DURATION_LITERAL
    : [0-9]+ ('s' | 'm' | 'h' | 'd')
    ;

IDENTIFIER
    : [a-z_] [a-z0-9_]*
    ;

STRING
    : '"' (~["\r\n])* '"'
    ;

// ----------------------------------------------------------------------------
// Operators
// ----------------------------------------------------------------------------

GTE
    : '>='
    ;

// ----------------------------------------------------------------------------
// Comments and Whitespace
// ----------------------------------------------------------------------------

COMMENT
    : '//' ~[\r\n]* -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
