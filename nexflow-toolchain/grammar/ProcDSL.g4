// Nexflow DSL Toolchain
// Author: Chandra Mohn

/**
 * ProcDSL - Process Orchestration Domain-Specific Language
 *
 * ANTLR4 Grammar for L1 Process Orchestration DSL
 *
 * Version: 0.5.0
 * Specification: ../L1-Process-Orchestration-DSL.md
 * Runtime Spec: ../L1-Runtime-Semantics.md
 *
 * This grammar defines the syntax for Nexflow, a controlled natural language
 * for defining streaming and batch data processing pipelines.
 *
 * v0.5.0 Changes:
 * - Added connector syntax (kafka, mongodb, elasticsearch, scheduler)
 * - Added inline aggregation functions (count(), sum(), etc.)
 * - Added evaluate block for L4 rules integration
 * - Added branch construct for conditional sub-pipelines
 * - Added parallel construct for fan-out processing
 * - Added metrics block for observability
 * - Added state_machine construct
 * - Added enhanced error handling (retry with backoff)
 * - Added lookup with cache, state_store sources
 * - Added schedule construct for delayed actions
 * - Added emit_audit_event for event sourcing
 * - Added deduplicate construct
 * - Added validate_input block
 * - Removed foreach iteration (use collection operations: any, all, filter, sum, count)
 * - Added inline transform with assignments
 * - Added call external for API integration
 *
 * SEMANTIC VALIDATION NOTES (enforced by compiler, not grammar):
 * - Every process MUST have at least one output: emit, route using, or aggregate
 * - Window blocks MUST be followed by aggregate
 * - Join requires exactly two aliased inputs
 * - Await requires exactly two receive blocks
 * - Batch mode cannot use watermark, window, or await
 * - Partition key field must exist in input schema
 */

grammar ProcDSL;

// ============================================================================
// PARSER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Top-Level Structure
// ----------------------------------------------------------------------------

program
    : importStatement* processDefinition+ EOF
    ;

// ----------------------------------------------------------------------------
// Import Statement (v0.7.0+)
// ----------------------------------------------------------------------------

importStatement
    : IMPORT importPath
    ;

importPath
    : importPathSegment+ importFileExtension  // Path ends with file extension
    ;

importPathSegment
    : DOTDOT | DOT | SLASH | IDENTIFIER | MINUS  // Allow: ./path, ../path, /abs/path, path-with-hyphens
    ;

importFileExtension
    : DOT (SCHEMA | TRANSFORM | 'flow' | 'rules')  // File extension marks end of import
    ;

processDefinition
    : PROCESS processName
        executionBlock?
        businessDateDecl?           // v0.6.0+: business_date from calendar
        processingDateDecl?         // v0.7.0+: processing_date auto (system time)
        markersBlock?               // v0.6.0+: EOD marker definitions
        stateMachineDecl?
        processBodyOrPhases         // v0.6.0+: either statements or phase blocks
        stateBlock?
        processTailBlocks?
      END
    ;

// v0.6.0+: Process body can be traditional statements OR phase blocks
processBodyOrPhases
    : bodyContent*                  // Traditional: interleaved statements
    | phaseBlock+                   // Phase-based: explicit phase blocks
    ;

// Allow metrics and resilience blocks in any order
processTailBlocks
    : metricsBlock resilienceBlock?     // metrics before on error
    | resilienceBlock metricsBlock?     // on error before metrics
    ;

// Body content allows interleaved processing and output
bodyContent
    : receiveDecl
    | processingBlock
    | emitDecl
    | correlationBlock
    | completionBlock
    ;

processName
    : IDENTIFIER
    ;

// Processing block contains declaration types
processingBlock
    : enrichDecl
    | transformDecl
    | routeDecl
    | aggregateDecl
    | windowDecl
    | joinDecl
    | mergeDecl
    | evaluateStatement
    | branchStatement
    | parallelStatement
    | transitionStatement
    | emitAuditStatement
    | deduplicateStatement
    | validateInputStatement
    | callStatement
    | scheduleStatement
    | setStatement
    | lookupStatement
    | signalStatement         // v0.6.0+: signal emission
    | sqlStatement            // v0.8.0+: embedded SQL block
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
    : PARALLELISM HINT? INTEGER
    ;

partitionDecl
    : PARTITION BY fieldList
    ;

timeDecl
    : TIME BY fieldPath
        watermarkDecl?
        lateDataDecl?
        latenessDecl?
    ;

watermarkDecl
    : WATERMARK DELAY duration
    ;

lateDataDecl
    : LATE DATA TO IDENTIFIER
    ;

latenessDecl
    : ALLOWED LATENESS duration
    ;

modeDecl
    : MODE modeType
    ;

modeType
    : STREAM
    | BATCH
    | MICRO_BATCH duration
    ;

// ----------------------------------------------------------------------------
// Business Date and Markers (v0.6.0+)
// ----------------------------------------------------------------------------

// Business date calendar reference
businessDateDecl
    : BUSINESS_DATE FROM IDENTIFIER     // business_date from trading_calendar
    ;

// Processing date - system time when record is processed (v0.7.0+)
processingDateDecl
    : PROCESSING_DATE AUTO              // processing_date auto (system clock)
    ;

// Markers block - EOD marker definitions
markersBlock
    : MARKERS
        markerDef+
      END
    ;

markerDef
    : IDENTIFIER COLON WHEN markerCondition
    ;

// Marker completion conditions
markerCondition
    : markerCondition AND markerCondition                       // Compound AND
    | markerCondition OR markerCondition                        // Compound OR
    | IDENTIFIER                                                // Signal name or marker reference
    | IDENTIFIER DOT DRAINED                                    // stream.drained
    | IDENTIFIER DOT COUNT comparisonOp INTEGER                 // stream.count >= 1000
    | AFTER timeSpec                                            // Time-based: after 18:00
    | API DOT IDENTIFIER DOT IDENTIFIER                         // api.service.ready
    | LPAREN markerCondition RPAREN                             // Parenthesized
    ;

timeSpec
    : TIME_LITERAL                                              // "18:00", "23:59"
    | END_OF_DAY                                                // end_of_day keyword
    ;

// Phase block - statements that execute within a phase
phaseBlock
    : PHASE phaseSpec
        bodyContent*                                            // Same statements as traditional body
        onCompleteClause*
      END
    ;

phaseSpec
    : BEFORE IDENTIFIER                                         // phase before eod_1
    | BETWEEN IDENTIFIER AND IDENTIFIER                         // phase between eod_1 and eod_2
    | AFTER IDENTIFIER                                          // phase after eod_3
    | ANYTIME                                                   // phase anytime
    ;

// Signal emission on phase completion
onCompleteClause
    : ON COMPLETE (WHEN expression)? SIGNAL IDENTIFIER (TO IDENTIFIER)?
    ;

// Standalone signal statement (for rollover, etc.)
signalStatement
    : SIGNAL IDENTIFIER TO IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// State Machine Declaration
// ----------------------------------------------------------------------------

stateMachineDecl
    : STATE_MACHINE IDENTIFIER
        schemaDecl?
        persistenceDecl?
        checkpointDecl?
    ;

persistenceDecl
    : PERSISTENCE IDENTIFIER
    ;

checkpointDecl
    : CHECKPOINT EVERY (INTEGER EVENTS (OR duration)? | duration)
        (TO IDENTIFIER)?    // Optional checkpoint destination (e.g., to s3_checkpoint)
    ;

// ----------------------------------------------------------------------------
// Input Block - Receive
// ----------------------------------------------------------------------------

receiveDecl
    : RECEIVE IDENTIFIER (FROM IDENTIFIER)?     // receive transactions from kafka_transactions OR receive transactions
        receiveClause*
    ;

receiveClause
    : schemaDecl
    | connectorClause
    | projectClause
    | receiveAction
    | FILTER expression     // Filter clause in receive
    ;

connectorClause
    : FROM connectorType connectorConfig        // from kafka "topic" | from kafka topic_reference
    | TO connectorType connectorConfig          // to kafka "topic" | to kafka topic_reference
    | TO IDENTIFIER                             // to connector_reference (named connector)
    ;

connectorType
    : KAFKA
    | MONGODB
    | REDIS
    | SCHEDULER
    | STATE_STORE
    | PARQUET
    | CSV
    | IDENTIFIER
    ;

connectorConfig
    : (STRING | IDENTIFIER) (COMMA (STRING | IDENTIFIER))* connectorOptions*
    ;

connectorOptions
    : GROUP STRING
    | OFFSET offsetType
    | ISOLATION isolationType
    | KEY fieldPath
    | FILTER expression
    | INDEX STRING
    | COMPACTION compactionType
    | RETENTION retentionType
    | UPSERT BY fieldPath
    | HEADERS COLON (paramBlock | headerBindings)
    | TEMPLATE STRING
    | CHANNEL COLON expression
    | timestampBounds                              // Kafka/Parquet timestamp bounds
    | parquetOptions                               // Parquet-specific options
    | csvOptions                                   // CSV-specific options
    | formatOverride                               // v0.8.0+: Serialization format override
    | registryOverride                             // v0.8.0+: Schema registry URL override
    ;

// v0.8.0+: Serialization format override (use sparingly)
formatOverride
    : FORMAT serializationFormat
    ;

// v0.8.0+: Schema registry URL override
registryOverride
    : REGISTRY STRING
    ;

// Serialization format for Kafka connectors
serializationFormat
    : JSON_FORMAT
    | AVRO
    | CONFLUENT_AVRO
    | PROTOBUF
    ;

// Timestamp bounds for bounded reads (Kafka/Parquet)
timestampBounds
    : FROM TIMESTAMP STRING (TO TIMESTAMP STRING)?   // from timestamp "2024-01-01T00:00:00Z" to timestamp "2024-12-31T23:59:59Z"
    | TO TIMESTAMP STRING                            // to timestamp "2024-12-31T23:59:59Z" (from earliest)
    ;

// Parquet-specific options
parquetOptions
    : PARTITION_BY fieldList                        // partition by year, month
    | SCHEMA_PATH STRING                            // schema_path "schemas/sales.avsc"
    ;

// CSV-specific options
csvOptions
    : DELIMITER STRING                              // delimiter ","
    | QUOTE STRING                                  // quote "\""
    | ESCAPE_CHAR STRING                            // escape_char "\\"
    | HEADER booleanLiteral                         // header true
    | NULL_VALUE STRING                             // null_value ""
    ;

headerBindings
    : headerBinding+
    ;

headerBinding
    : keywordOrIdentifier COLON expression
    ;

// Allow keywords to be used as field names in specific contexts
// This enables using common words as both keywords and identifiers
keywordOrIdentifier
    : IDENTIFIER
    | PRIORITY      // priority is both keyword and valid field name
    | REASON        // reason is both keyword and valid field name
    | LEVEL         // level is valid field name
    | TYPE          // type is both keyword and valid field name
    | PAYLOAD       // payload is common data reference
    | STATE         // state is common field name
    | DATA          // data is common field name
    | KEY           // key is common field name
    | COUNT         // count is common field name
    | TIME          // time is common field name
    | INPUT         // input is common field name
    | OUTPUT        // output is common field name
    | ERROR         // error is common field name in error handling
    ;

offsetType
    : LATEST
    | EARLIEST
    | IDENTIFIER
    ;

isolationType
    : READ_COMMITTED
    | READ_UNCOMMITTED
    ;

compactionType
    : NONE
    | IDENTIFIER
    ;

retentionType
    : INFINITE
    | duration
    ;

projectClause
    : PROJECT fieldList
    | PROJECT EXCEPT fieldList
    ;

schemaDecl
    : SCHEMA IDENTIFIER
    ;

receiveAction
    : storeAction
    | matchAction
    ;

storeAction
    : STORE IN IDENTIFIER
    ;

matchAction
    : MATCH FROM IDENTIFIER ON fieldList
    ;

// ----------------------------------------------------------------------------
// Processing Statements
// ----------------------------------------------------------------------------

processingStatement
    : transformDecl
    | evaluateStatement
    | routeDecl
    | windowDecl
    | joinDecl
    | mergeDecl
    | enrichDecl
    | aggregateDecl
    | lookupStatement
    | branchStatement
    | parallelStatement
    | transitionStatement
    | emitAuditStatement
    | deduplicateStatement
    | validateInputStatement
    | callStatement
    | scheduleStatement
    | setStatement
    | letStatement
    | ifStatement
    ;

// Transform with optional inline body or 'using' reference
transformDecl
    : TRANSFORM (USING IDENTIFIER | IDENTIFIER?)
        transformOptions?
        embeddedLookup?
        transformStateRef?
        (onSuccessBlock onFailureBlock?)?
        inlineTransformBody?
    ;

transformStateRef
    : STATE identifierList
    ;

transformOptions
    : transformOption+
    ;

transformOption
    : PARAMS COLON paramBlock
    | INPUT COLON arrayLiteral
    | LOOKUPS COLON (paramBlock | lookupsBlock)
    ;

lookupsBlock
    : lookupBinding+
    ;

lookupBinding
    : IDENTIFIER COLON expression
    ;

// Embedded lookup within transform
embeddedLookup
    : LOOKUP IDENTIFIER
        (FROM lookupSource)?
        (KEY fieldPath)?
        (CACHE TTL duration)?
    ;

onSuccessBlock
    : ON_SUCCESS actionContent END
    ;

onFailureBlock
    : ON_FAILURE actionContent END
    ;

actionContent
    : (processingStatement | emitDecl | CONTINUE | TERMINATE)+
    ;

// Note: END is required for on_success/on_failure blocks to avoid parsing ambiguity
// with following statements. Without END, the actionContent rule's + quantifier
// would greedily consume all subsequent processingStatements.

inlineTransformBody
    : assignment+
    ;

assignment
    : fieldPath ASSIGN expression
    ;

// Evaluate for L4 rules integration
evaluateStatement
    : EVALUATE USING IDENTIFIER
        evaluateOptions?
        (outputCapture)?
        evaluateActions?
    ;

evaluateOptions
    : (PARAMS COLON paramBlock)?
    ;

outputCapture
    : OUTPUT IDENTIFIER
    ;

// Actions after evaluate - either direct or conditional
evaluateActions
    : conditionalAction
    | directActions
    ;

// Direct actions without condition
directActions
    : (addFlagStatement | addMetadataStatement | adjustScoreStatement)+
    ;

conditionalAction
    : (WHEN expression | ON_CRITICAL_FRAUD | ON_DUPLICATE)
        conditionalBody
        END      // END is required to avoid parsing ambiguity with following statements
    ;

conditionalBody
    : (processingStatement | emitDecl | addFlagStatement | addMetadataStatement | adjustScoreStatement | CONTINUE | TERMINATE)+
    ;

addFlagStatement
    : ADD_FLAG STRING
    ;

addMetadataStatement
    : ADD_METADATA STRING ASSIGN expression
    ;

adjustScoreStatement
    : ADJUST_SCORE BY fieldPath
    ;

// Route with conditions, rule reference, or field path
routeDecl
    : ROUTE (USING routeSource | WHEN expression)
        routeDestination*
        otherwiseClause?
    ;

// Route source: either a rule name (IDENTIFIER) or field path (field.subfield)
routeSource
    : fieldPath    // route using result.decision or route using simple_approval
    ;

// Route destination: either "value to target" or just "to target" for conditional routes
routeDestination
    : (STRING | IDENTIFIER) TO IDENTIFIER  // Named: "approved" to approved_sink
    | TO IDENTIFIER                         // Direct: to target_sink
    ;

otherwiseClause
    : OTHERWISE (TO IDENTIFIER | CONTINUE)
    ;

// Window with inline aggregations
windowDecl
    : WINDOW windowType duration windowBody?
    ;

windowType
    : TUMBLING
    | SLIDING duration EVERY
    | SESSION GAP
    ;

windowBody
    : keyByClause?
      inlineAggregateBlock?
      stateClause?
      windowOptions?
    ;

keyByClause
    : KEY BY fieldPath
    ;

inlineAggregateBlock
    : AGGREGATE
        aggregationExpr+
      END
    ;

aggregationExpr
    : aggregateFunction AS IDENTIFIER
    ;

aggregateFunction
    : COUNT LPAREN RPAREN
    | SUM LPAREN fieldPath RPAREN
    | AVG LPAREN fieldPath RPAREN
    | MIN LPAREN fieldPath RPAREN
    | MAX LPAREN fieldPath RPAREN
    | COLLECT LPAREN fieldPath RPAREN
    | FIRST LPAREN fieldPath RPAREN
    | LAST LPAREN fieldPath RPAREN
    ;

stateClause
    : STATE IDENTIFIER
    ;

windowOptions
    : latenessDecl? lateDataDecl?
    ;

// Join
joinDecl
    : JOIN IDENTIFIER WITH IDENTIFIER
        ON fieldList
        WITHIN duration
        joinType?
    ;

joinType
    : TYPE (INNER | LEFT | RIGHT | OUTER)
    ;

// Merge
mergeDecl
    : MERGE IDENTIFIER (COMMA IDENTIFIER)+
        (INTO IDENTIFIER)?
    ;

// Enrich
enrichDecl
    : ENRICH USING IDENTIFIER
        ON fieldList
        selectClause?
    ;

selectClause
    : SELECT fieldList
    ;

// Aggregate (external reference)
aggregateDecl
    : AGGREGATE (USING IDENTIFIER | IDENTIFIER)
        aggregateOptions?
    ;

aggregateOptions
    : FROM identifierList
      (TIMEOUT duration)?
      onPartialTimeoutBlock?
    ;

onPartialTimeoutBlock
    : ON_PARTIAL_TIMEOUT
        (logWarningStatement | addFlagStatement)+
    ;

logWarningStatement
    : LOG_WARNING STRING
    ;

// Lookup with various sources
lookupStatement
    : LOOKUP IDENTIFIER
        (KEY fieldPath)?
        (FROM lookupSource)?
        (FILTER expression)?          // Filter for state store scans
        (CACHE TTL duration)?
    ;

lookupSource
    : STATE_STORE STRING
    | MONGODB STRING
    | IDENTIFIER
    ;

// Branch for conditional sub-pipelines
branchStatement
    : BRANCH IDENTIFIER
        branchBody
      END
    ;

branchBody
    : (processingStatement | emitDecl | TERMINATE)+
    ;

// Parallel fan-out
parallelStatement
    : PARALLEL IDENTIFIER
        parallelOptions?
        parallelBranch+
      END
    ;

parallelOptions
    : (TIMEOUT duration)?
      (REQUIRE_ALL booleanLiteral)?
      (MIN_REQUIRED INTEGER)?
    ;

parallelBranch
    : BRANCH IDENTIFIER
        branchBody
      END
    ;

// State transition
transitionStatement
    : TRANSITION TO STRING
    ;

// Audit event emission
emitAuditStatement
    : EMIT_AUDIT_EVENT STRING
        (ACTOR actorType)?
        (PAYLOAD COLON paramBlock)?
    ;

actorType
    : SYSTEM STRING
    | USER fieldPath
    ;

// Deduplication
deduplicateStatement
    : DEDUPLICATE BY fieldPath
        (WINDOW duration)?
        conditionalAction?
    ;

// Input validation
validateInputStatement
    : VALIDATE_INPUT
        validationRule+
    ;

validationRule
    : REQUIRE expression ELSE STRING
    ;

// External API calls
callStatement
    : CALL callType (IDENTIFIER | STRING)    // call ml_service "model_name" or call external service_id
        callOptions?
    ;

callType
    : EXTERNAL
    | ML_SERVICE
    ;

callOptions
    : callOption+
    ;

callOption
    : ENDPOINT STRING
    | TIMEOUT duration
    | FEATURES COLON (fieldPath | paramBlock)    // features: field OR features: { ... }
    | RETRY INTEGER TIMES
    | circuitBreakerClause
    ;

circuitBreakerClause
    : CIRCUIT_BREAKER
        (FAILURE_THRESHOLD INTEGER)?
        (RESET_TIMEOUT duration)?
    ;

// Scheduled actions
scheduleStatement
    : SCHEDULE IDENTIFIER
        AFTER scheduleDuration
        ACTION IDENTIFIER
        (REPEAT UNTIL expression)?
    ;

// Duration that can be static or dynamic (expression-based)
scheduleDuration
    : duration                        // Static: 30 seconds, 5 minutes
    | expression timeUnit             // Dynamic: routing_result.sla_hours hours
    ;

// ----------------------------------------------------------------------------
// SQL Statement (v0.8.0+)
// ----------------------------------------------------------------------------

// Embedded SQL block for Flink SQL / Spark SQL transformations
// Uses SQL keyword followed by multi-line string
sqlStatement
    : SQL SQL_BLOCK                   // sql ```...```
        (AS IDENTIFIER)?              // Optional output type: as SalesSummary
    ;

// Set statement for field updates
setStatement
    : SET fieldPath ASSIGN expression
    ;

// Let statement for local variables
letStatement
    : LET IDENTIFIER ASSIGN expression
    ;

// If statement
ifStatement
    : IF expression THEN
        ifBody
      (ELSEIF expression THEN ifBody)*
      (ELSE ifBody)?
      ENDIF
    ;

ifBody
    : (processingBlock | emitDecl | ifStatement)+
    ;

// ----------------------------------------------------------------------------
// Emit Declaration
// ----------------------------------------------------------------------------

emitDecl
    : EMIT TO sinkName
        emitClause*
    ;

// Sink name can be identifier or keyword (like 'output', 'state', etc.)
sinkName
    : keywordOrIdentifier
    ;

emitClause
    : schemaDecl
    | connectorClause
    | emitOptions
    | fanoutDecl
    | persistClause
    ;

// L5 Integration: Persist to MongoDB async
persistClause
    : PERSIST TO persistTarget persistOption*
    ;

persistTarget
    : IDENTIFIER
    ;

persistOption
    : ASYNC                             // async write (non-blocking)
    | SYNC                              // sync write (blocking)
    | BATCH SIZE INTEGER                // batch size override
    | FLUSH INTERVAL duration           // flush interval override
    | ON ERROR persistErrorAction       // error handling
    ;

persistErrorAction
    : CONTINUE                          // ignore errors
    | FAIL                              // fail pipeline on error
    | EMIT TO sinkName                  // send failed records to DLQ
    ;

fanoutDecl
    : BROADCAST
    | ROUND_ROBIN
    ;

emitOptions
    : REASON STRING
    | PRESERVE_STATE booleanLiteral
    | INCLUDE_ERROR_CONTEXT booleanLiteral
    | TEMPLATE STRING
    | CHANNEL COLON expression
    | PAYLOAD COLON paramBlock
    ;

// ----------------------------------------------------------------------------
// Correlation Block (Await/Hold)
// ----------------------------------------------------------------------------

correlationBlock
    : awaitDecl
    | holdDecl
    ;

awaitDecl
    : AWAIT IDENTIFIER
        UNTIL IDENTIFIER ARRIVES
            MATCHING ON fieldList
        TIMEOUT duration
            timeoutAction
    ;

holdDecl
    : HOLD IDENTIFIER (IN IDENTIFIER)?
        KEYED BY fieldList
        completionClause?
        TIMEOUT duration
            timeoutAction
    ;

completionClause
    : COMPLETE WHEN completionCondition
    ;

completionCondition
    : COUNT GE INTEGER
    | MARKER RECEIVED
    | USING IDENTIFIER
    ;

timeoutAction
    : EMIT TO IDENTIFIER
    | DEAD_LETTER IDENTIFIER
    | SKIP_ACTION
    ;

// ----------------------------------------------------------------------------
// Completion Event Block
// ----------------------------------------------------------------------------

completionBlock
    : completionDecl+
    ;

completionDecl
    : onCommitDecl
    | onCommitFailureDecl
    ;

onCommitDecl
    : ON COMMIT
        EMIT COMPLETION TO IDENTIFIER
            correlationDecl
            includeDecl?
            schemaDecl?
    ;

onCommitFailureDecl
    : ON COMMIT FAILURE
        EMIT COMPLETION TO IDENTIFIER
            correlationDecl
            includeDecl?
            schemaDecl?
    ;

correlationDecl
    : CORRELATION fieldPath
    ;

includeDecl
    : INCLUDE fieldList
    ;

// ----------------------------------------------------------------------------
// State Block
// ----------------------------------------------------------------------------

stateBlock
    : STATE stateDecl+
    ;

stateDecl
    : usesDecl
    | localDecl
    | bufferDecl
    ;

usesDecl
    : USES IDENTIFIER
    ;

localDecl
    : LOCAL IDENTIFIER KEYED BY fieldList
        TYPE stateType
        ttlDecl?
        cleanupDecl?
    ;

stateType
    : COUNTER
    | GAUGE
    | MAP
    | LIST
    ;

ttlDecl
    : TTL ttlType? duration
    ;

ttlType
    : SLIDING
    | ABSOLUTE
    ;

cleanupDecl
    : CLEANUP cleanupStrategy
    ;

cleanupStrategy
    : ON_CHECKPOINT
    | ON_ACCESS
    | BACKGROUND
    ;

bufferDecl
    : BUFFER IDENTIFIER KEYED BY fieldList
        TYPE bufferType
        ttlDecl?
    ;

bufferType
    : FIFO
    | LIFO
    | PRIORITY BY fieldPath
    ;

// ----------------------------------------------------------------------------
// Metrics Block
// ----------------------------------------------------------------------------

metricsBlock
    : METRICS
        metricDecl+
      END
    ;

metricDecl
    : COUNTER IDENTIFIER
    | HISTOGRAM IDENTIFIER
    | GAUGE IDENTIFIER
    | RATE IDENTIFIER (WINDOW duration)?
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
    : ON ERROR
        (errorHandler+ | simpleErrorHandler)
      END      // END is required to properly delimit the error block
    ;

// Simple error handler: supports various patterns in any order
// - log_error "message", emit_audit_event, retry, transition, emit
simpleErrorHandler
    : errorHandlerStatement+
    ;

errorHandlerStatement
    : logErrorStatement
    | emitAuditStatement
    | retryBlock thenBlock?
    | transitionStatement
    | emitDecl
    ;

errorHandler
    : errorType errorAction
    ;

errorType
    : TRANSFORM_ERROR           // transform_error
    | LOOKUP_ERROR              // lookup_error
    | RULE_ERROR                // rule_error
    | CORRELATION_ERROR         // correlation_error
    | TRANSFORM FAILURE         // transform failure (two-word syntax)
    | LOOKUP FAILURE            // lookup failure
    | RULE FAILURE              // rule failure
    | CORRELATION FAILURE       // correlation failure
    ;

errorAction
    : SKIP_ACTION
    | RETRY INTEGER (TIMES)?
    | DEAD_LETTER IDENTIFIER
    ;

checkpointBlock
    : CHECKPOINT EVERY duration (USING | TO) IDENTIFIER
    ;

backpressureBlock
    : BACKPRESSURE backpressureStrategy alertDecl?
    | WHEN SLOW backpressureStrategy alertDecl?     // when slow strategy drop
    ;

backpressureStrategy
    : STRATEGY? BLOCK
    | STRATEGY? DROP
    | STRATEGY? SAMPLE NUMBER
    ;

alertDecl
    : ALERT AFTER duration
    ;

// Logging statements - support both keyword and function-call style for flexibility
logErrorStatement
    : LOG_ERROR LPAREN STRING RPAREN      // log_error("message")
    | LOG_ERROR STRING                    // log_error "message"
    ;

logInfoStatement
    : LOG_INFO STRING                     // log_info "message"
    ;

retryBlock
    : RETRY (INTEGER TIMES | INDEFINITELY)
        retryOptions?
    ;

retryOptions
    : (DELAY duration)?
      (BACKOFF backoffType)?
      (MAX_DELAY duration)?
    ;

backoffType
    : EXPONENTIAL
    | LINEAR
    | IDENTIFIER
    ;

thenBlock
    : THEN
        thenContent
    ;

thenContent
    : (processingStatement | emitDecl | logErrorStatement)+
    ;

// ----------------------------------------------------------------------------
// Expressions
// ----------------------------------------------------------------------------

expression
    : orExpression
    ;

orExpression
    : andExpression (OR andExpression)*
    ;

andExpression
    : notExpression (AND notExpression)*
    ;

notExpression
    : NOT? comparisonExpression
    ;

comparisonExpression
    : additiveExpression (comparisonOp additiveExpression)?
    | additiveExpression IS NULL
    | additiveExpression IS NOT NULL
    | additiveExpression IN LPAREN valueList RPAREN           // x in (a, b, c)
    | additiveExpression IN LBRACKET valueList RBRACKET       // x in [a, b, c]
    | additiveExpression NOT IN LPAREN valueList RPAREN       // x not in (a, b, c)
    | additiveExpression NOT IN LBRACKET valueList RBRACKET   // x not in [a, b, c]
    | CONTAINS LPAREN fieldPath COMMA STRING RPAREN
    ;

comparisonOp
    : EQ | NE | LT | GT | LE | GE
    ;

additiveExpression
    : multiplicativeExpression ((PLUS | MINUS) multiplicativeExpression)*
    ;

multiplicativeExpression
    : unaryExpression ((STAR | SLASH | PERCENT) unaryExpression)*
    ;

unaryExpression
    : MINUS? primaryExpression
    ;

primaryExpression
    : literal
    | functionCall              // Must come before fieldPath (both start with IDENTIFIER)
    | fieldPath
    | objectLiteral             // Allow inline object construction: { key: value, ... }
    | arrayLiteral              // Allow inline array construction: [a, b, c]
    | LPAREN expression RPAREN
    | ternaryExpression
    | interpolatedString
    | durationLiteral           // Allow duration as primary expression for arithmetic
    ;

ternaryExpression
    : fieldPath QUESTION expression COLON expression
    ;

functionCall
    : functionName LPAREN (expression (COMMA expression)*)? RPAREN
    ;

functionName
    : IDENTIFIER
    | LOOKUP              // lookup() function
    | NOW                 // now() function
    | COUNT               // count() function
    ;

interpolatedString
    : INTERP_STRING
    ;

// ----------------------------------------------------------------------------
// Common Rules
// ----------------------------------------------------------------------------

fieldPath
    : keywordOrIdentifier (DOT keywordOrIdentifier)* (LBRACKET INTEGER RBRACKET)?
    ;

fieldList
    : fieldPath (COMMA fieldPath)*
    ;

identifierList
    : IDENTIFIER (COMMA IDENTIFIER)*
    ;

valueList
    : expression (COMMA expression)*
    ;

duration
    : INTEGER timeUnit
    | DURATION_LITERAL
    ;

// Duration literal for use in expressions (e.g., now() + 7 days or now() + field.hours hours)
durationLiteral
    : INTEGER timeUnit                      // Static: 7 days, 30 minutes
    | fieldPath timeUnit                    // Dynamic: routing_result.sla_hours hours
    ;

timeUnit
    : SECONDS | SECOND
    | MINUTES | MINUTE
    | HOURS   | HOUR
    | DAYS    | DAY
    | WEEKS   | WEEK
    ;

literal
    : INTEGER
    | NUMBER
    | STRING
    | booleanLiteral
    | NULL
    | objectLiteral
    ;

booleanLiteral
    : TRUE | FALSE
    ;

objectLiteral
    : LBRACE (objectField (COMMA objectField)*)? RBRACE
    ;

objectField
    : keywordOrIdentifier COLON expression    // Allow keywords as field names in object literals
    ;

arrayLiteral
    : LBRACKET (expression (COMMA expression)*)? RBRACKET
    ;

paramBlock
    : LBRACE (paramField (COMMA paramField)*)? RBRACE
    ;

paramField
    : keywordOrIdentifier COLON expression    // Allow keywords as field names in param blocks
    ;

// ============================================================================
// LEXER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Keywords - Structure
// ----------------------------------------------------------------------------

IMPORT        : 'import' ;  // v0.7.0+: For import statements
PROCESS       : 'process' ;
END           : 'end' ;

// ----------------------------------------------------------------------------
// Keywords - Execution
// ----------------------------------------------------------------------------

PARALLELISM   : 'parallelism' ;
HINT          : 'hint' ;
PARTITION     : 'partition' ;
BY            : 'by' ;
TIME          : 'time' ;
WATERMARK     : 'watermark' ;
DELAY         : 'delay' ;
LATE          : 'late' ;
DATA          : 'data' ;
ALLOWED       : 'allowed' ;
LATENESS      : 'lateness' ;
MODE          : 'mode' ;
STREAM        : 'stream' ;
BATCH         : 'batch' ;
MICRO_BATCH   : 'micro_batch' ;
EVENTS        : 'events' ;

// ----------------------------------------------------------------------------
// Keywords - Business Date, Processing Date and Markers (v0.6.0+, v0.7.0+)
// ----------------------------------------------------------------------------

BUSINESS_DATE   : 'business_date' ;
PROCESSING_DATE : 'processing_date' ;
AUTO            : 'auto' ;
MARKERS         : 'markers' ;
PHASE           : 'phase' ;
BEFORE        : 'before' ;
BETWEEN       : 'between' ;
// Note: AFTER, COMPLETE, COUNT already defined in other sections
ANYTIME       : 'anytime' ;
SIGNAL        : 'signal' ;
DRAINED       : 'drained' ;
API           : 'api' ;
END_OF_DAY    : 'end_of_day' ;

// Time literal for marker conditions: "18:00", "23:59"
TIME_LITERAL  : '"' [0-2] [0-9] ':' [0-5] [0-9] '"' ;

// ----------------------------------------------------------------------------
// Keywords - State Machine
// ----------------------------------------------------------------------------

STATE_MACHINE : 'state_machine' ;
PERSISTENCE   : 'persistence' ;
TRANSITION    : 'transition' ;

// ----------------------------------------------------------------------------
// Keywords - Input/Output
// ----------------------------------------------------------------------------

RECEIVE       : 'receive' ;
FROM          : 'from' ;
SCHEMA        : 'schema' ;
PROJECT       : 'project' ;
EXCEPT        : 'except' ;
EMIT          : 'emit' ;
TO            : 'to' ;
FANOUT        : 'fanout' ;
BROADCAST     : 'broadcast' ;
ROUND_ROBIN   : 'round_robin' ;
REASON        : 'reason' ;
PERSIST       : 'persist' ;
ASYNC         : 'async' ;
SYNC          : 'sync' ;
FLUSH         : 'flush' ;
FAIL          : 'fail' ;
SIZE          : 'size' ;
INTERVAL      : 'interval' ;

// ----------------------------------------------------------------------------
// Keywords - Connectors
// ----------------------------------------------------------------------------

KAFKA         : 'kafka' ;
MONGODB       : 'mongodb' ;
REDIS         : 'redis' ;
SCHEDULER     : 'scheduler' ;
STATE_STORE   : 'state_store' ;
PARQUET       : 'parquet' ;        // v0.8.0+: Parquet file source/sink
CSV           : 'csv' ;            // v0.8.0+: CSV file source/sink
GROUP         : 'group' ;
OFFSET        : 'offset' ;
LATEST        : 'latest' ;
EARLIEST      : 'earliest' ;
ISOLATION     : 'isolation' ;
READ_COMMITTED   : 'read_committed' ;
READ_UNCOMMITTED : 'read_uncommitted' ;
COMPACTION    : 'compaction' ;
RETENTION     : 'retention' ;
INFINITE      : 'infinite' ;
UPSERT        : 'upsert' ;
HEADERS       : 'headers' ;
INDEX         : 'index' ;
TEMPLATE      : 'template' ;
CHANNEL       : 'channel' ;
PAYLOAD       : 'payload' ;
TIMESTAMP     : 'timestamp' ;      // v0.8.0+: For timestamp bounds
PARTITION_BY  : 'partition_by' ;   // v0.8.0+: Parquet partitioning
SCHEMA_PATH   : 'schema_path' ;    // v0.8.0+: External schema reference
DELIMITER     : 'delimiter' ;      // v0.8.0+: CSV delimiter
QUOTE         : 'quote' ;          // v0.8.0+: CSV quote character
ESCAPE_CHAR   : 'escape_char' ;    // v0.8.0+: CSV escape character
HEADER        : 'header' ;         // v0.8.0+: CSV header flag
NULL_VALUE    : 'null_value' ;     // v0.8.0+: CSV null representation

// v0.8.0+: Serialization format keywords
FORMAT        : 'format' ;
REGISTRY      : 'registry' ;
JSON_FORMAT   : 'json' ;
AVRO          : 'avro' ;
CONFLUENT_AVRO: 'confluent_avro' ;
PROTOBUF      : 'protobuf' ;

// ----------------------------------------------------------------------------
// Keywords - Processing
// ----------------------------------------------------------------------------

TRANSFORM     : 'transform' ;
USING         : 'using' ;
ENRICH        : 'enrich' ;
ROUTE         : 'route' ;
AGGREGATE     : 'aggregate' ;
MERGE         : 'merge' ;
INTO          : 'into' ;
SELECT        : 'select' ;
ON            : 'on' ;
EVALUATE      : 'evaluate' ;
BRANCH        : 'branch' ;
PARALLEL      : 'parallel' ;
LOOKUP        : 'lookup' ;
CACHE         : 'cache' ;
CALL          : 'call' ;
EXTERNAL      : 'external' ;
ML_SERVICE    : 'ml_service' ;
ENDPOINT      : 'endpoint' ;
FEATURES      : 'features' ;
PARAMS        : 'params' ;
INPUT         : 'input' ;
OUTPUT        : 'output' ;
LOOKUPS       : 'lookups' ;

// ----------------------------------------------------------------------------
// Keywords - Window/Aggregation
// ----------------------------------------------------------------------------

WINDOW        : 'window' ;
TUMBLING      : 'tumbling' ;
SLIDING       : 'sliding' ;
SESSION       : 'session' ;
GAP           : 'gap' ;
EVERY         : 'every' ;
KEY           : 'key' ;
COUNT         : 'count' ;
NOW           : 'now' ;
SUM           : 'sum' ;
AVG           : 'avg' ;
MIN           : 'min' ;
MAX           : 'max' ;
COLLECT       : 'collect' ;
FIRST         : 'first' ;
LAST          : 'last' ;
AS            : 'as' ;

// ----------------------------------------------------------------------------
// Keywords - Join
// ----------------------------------------------------------------------------

JOIN          : 'join' ;
WITH          : 'with' ;
WITHIN        : 'within' ;
TYPE          : 'type' ;
INNER         : 'inner' ;
LEFT          : 'left' ;
RIGHT         : 'right' ;
OUTER         : 'outer' ;

// ----------------------------------------------------------------------------
// Keywords - Correlation
// ----------------------------------------------------------------------------

AWAIT         : 'await' ;
UNTIL         : 'until' ;
ARRIVES       : 'arrives' ;
MATCHING      : 'matching' ;
TIMEOUT       : 'timeout' ;
HOLD          : 'hold' ;
KEYED         : 'keyed' ;
COMPLETE      : 'complete' ;
MARKER        : 'marker' ;
RECEIVED      : 'received' ;

// ----------------------------------------------------------------------------
// Keywords - Completion
// ----------------------------------------------------------------------------

COMMIT        : 'commit' ;
FAILURE       : 'failure' ;
COMPLETION    : 'completion' ;
CORRELATION   : 'correlation' ;
INCLUDE       : 'include' ;

// ----------------------------------------------------------------------------
// Keywords - State
// ----------------------------------------------------------------------------

STATE         : 'state' ;
USES          : 'uses' ;
LOCAL         : 'local' ;
COUNTER       : 'counter' ;
GAUGE         : 'gauge' ;
MAP           : 'map' ;
LIST          : 'list' ;
TTL           : 'ttl' ;
ABSOLUTE      : 'absolute' ;
CLEANUP       : 'cleanup' ;
ON_CHECKPOINT : 'on_checkpoint' ;
ON_ACCESS     : 'on_access' ;
BACKGROUND    : 'background' ;
BUFFER        : 'buffer' ;
FIFO          : 'fifo' ;
LIFO          : 'lifo' ;
PRIORITY      : 'priority' ;
LEVEL         : 'level' ;
STORE         : 'store' ;
MATCH         : 'match' ;

// ----------------------------------------------------------------------------
// Keywords - Control Flow
// ----------------------------------------------------------------------------

WHEN          : 'when' ;
OTHERWISE     : 'otherwise' ;
IF            : 'if' ;
THEN          : 'then' ;
ELSE          : 'else' ;
ELSEIF        : 'elseif' ;
ENDIF         : 'endif' ;
IN            : 'in' ;
CONTINUE      : 'continue' ;
TERMINATE     : 'terminate' ;

// ----------------------------------------------------------------------------
// Keywords - Conditional Actions
// ----------------------------------------------------------------------------

ADD_FLAG      : 'add_flag' ;
ADD_METADATA  : 'add_metadata' ;
ADJUST_SCORE  : 'adjust_score' ;
ON_CRITICAL_FRAUD  : 'on_critical_fraud' ;
ON_DUPLICATE  : 'on_duplicate' ;
ON_SUCCESS    : 'on_success' ;
ON_FAILURE    : 'on_failure' ;
ON_PARTIAL_TIMEOUT : 'on_partial_timeout' ;

// ----------------------------------------------------------------------------
// Keywords - Resilience
// ----------------------------------------------------------------------------

ERROR         : 'error' ;
DEAD_LETTER   : 'dead_letter' ;
SKIP_ACTION   : 'skip' ;
RETRY         : 'retry' ;
TIMES         : 'times' ;
INDEFINITELY  : 'indefinitely' ;
BACKOFF       : 'backoff' ;
EXPONENTIAL   : 'exponential' ;
LINEAR        : 'linear' ;
MAX_DELAY     : 'max_delay' ;
CHECKPOINT    : 'checkpoint' ;
STRATEGY      : 'strategy' ;
BLOCK         : 'block' ;
DROP          : 'drop' ;
SAMPLE        : 'sample' ;
ALERT         : 'alert' ;
AFTER         : 'after' ;
CIRCUIT_BREAKER    : 'circuit_breaker' ;
FAILURE_THRESHOLD  : 'failure_threshold' ;
RESET_TIMEOUT      : 'reset_timeout' ;
PRESERVE_STATE     : 'preserve_state' ;
INCLUDE_ERROR_CONTEXT : 'include_error_context' ;
BACKPRESSURE       : 'backpressure' ;
SLOW               : 'slow' ;
TRANSFORM_ERROR    : 'transform_error' ;
LOOKUP_ERROR       : 'lookup_error' ;
RULE_ERROR         : 'rule_error' ;
RULE               : 'rule' ;
CORRELATION_ERROR  : 'correlation_error' ;

// ----------------------------------------------------------------------------
// Keywords - Parallel
// ----------------------------------------------------------------------------

REQUIRE_ALL   : 'require_all' ;
MIN_REQUIRED  : 'min_required' ;

// ----------------------------------------------------------------------------
// Keywords - Scheduling
// ----------------------------------------------------------------------------

SCHEDULE      : 'schedule' ;
ACTION        : 'action' ;
REPEAT        : 'repeat' ;

// ----------------------------------------------------------------------------
// Keywords - Audit
// ----------------------------------------------------------------------------

EMIT_AUDIT_EVENT : 'emit_audit_event' ;
ACTOR         : 'actor' ;
SYSTEM        : 'system' ;
USER          : 'user' ;

// ----------------------------------------------------------------------------
// Keywords - Deduplication
// ----------------------------------------------------------------------------

DEDUPLICATE   : 'deduplicate' ;

// ----------------------------------------------------------------------------
// Keywords - Validation
// ----------------------------------------------------------------------------

VALIDATE_INPUT : 'validate_input' ;
REQUIRE       : 'require' ;

// ----------------------------------------------------------------------------
// Keywords - Variables
// ----------------------------------------------------------------------------

LET           : 'let' ;
SET           : 'set' ;

// ----------------------------------------------------------------------------
// Keywords - Metrics
// ----------------------------------------------------------------------------

METRICS       : 'metrics' ;
HISTOGRAM     : 'histogram' ;
RATE          : 'rate' ;

// ----------------------------------------------------------------------------
// Keywords - Logging
// ----------------------------------------------------------------------------

LOG_ERROR     : 'log_error' ;
LOG_WARNING   : 'log_warning' ;
LOG_INFO      : 'log_info' ;

// ----------------------------------------------------------------------------
// Keywords - Boolean/Logic
// ----------------------------------------------------------------------------

AND           : 'and' ;
OR            : 'or' ;
NOT           : 'not' ;
TRUE          : 'true' ;
FALSE         : 'false' ;
NULL          : 'null' ;
IS            : 'is' ;
CONTAINS      : 'contains' ;
NONE          : 'none' ;
FILTER        : 'filter' ;

// ----------------------------------------------------------------------------
// Time Units
// ----------------------------------------------------------------------------

SECONDS       : 'seconds' ;
SECOND        : 'second' ;
MINUTES       : 'minutes' ;
MINUTE        : 'minute' ;
HOURS         : 'hours' ;
HOUR          : 'hour' ;
DAYS          : 'days' ;
DAY           : 'day' ;
WEEKS         : 'weeks' ;
WEEK          : 'week' ;

// ----------------------------------------------------------------------------
// Operators
// ----------------------------------------------------------------------------

ASSIGN        : '=' ;
EQ            : '==' ;
NE            : '!=' ;
LT            : '<' ;
GT            : '>' ;
LE            : '<=' ;
GE            : '>=' ;
PLUS          : '+' ;
MINUS         : '-' ;
STAR          : '*' ;
SLASH         : '/' ;
PERCENT       : '%' ;
QUESTION      : '?' ;

// ----------------------------------------------------------------------------
// Punctuation
// ----------------------------------------------------------------------------

LPAREN        : '(' ;
RPAREN        : ')' ;
LBRACE        : '{' ;
RBRACE        : '}' ;
LBRACKET      : '[' ;
RBRACKET      : ']' ;
COLON         : ':' ;
COMMA         : ',' ;
DOTDOT        : '..' ;  // v0.7.0+: Must come before DOT for correct lexing
DOT           : '.' ;

// ----------------------------------------------------------------------------
// SQL Block and Keywords (v0.8.0+)
// ----------------------------------------------------------------------------

// SQL keyword for embedded SQL statements
SQL           : 'sql' ;

// SQL block using triple backticks - captures entire SQL content as single token
SQL_BLOCK
    : '```' .*? '```'
    ;

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

INTEGER
    : [0-9]+
    ;

NUMBER
    : [0-9]+ '.' [0-9]+
    ;

DURATION_LITERAL
    : [0-9]+ ('s' | 'm' | 'h' | 'd')
    ;

STRING
    : '"' (~["\r\n] | '\\"')* '"'
    | '\'' (~['\r\n] | '\\\'')* '\''
    ;

INTERP_STRING
    : '"' (~["\r\n] | '\\' . | '${' ~[}]* '}')* '"'
    ;

IDENTIFIER
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// ----------------------------------------------------------------------------
// Comments and Whitespace
// ----------------------------------------------------------------------------

COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
