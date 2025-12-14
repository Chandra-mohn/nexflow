// Nexflow DSL Toolchain
// Author: Chandra Mohn

/**
 * SchemaDSL - Schema Registry Domain-Specific Language
 *
 * ANTLR4 Grammar for L2 Schema Registry DSL
 *
 * Version: 1.0.0
 * Specification: ../L2-Schema-Registry.md
 *
 * This grammar defines the syntax for schema definitions including:
 * - Data mutation patterns (9 patterns)
 * - Type system (base, constrained, domain, collection types)
 * - Streaming annotations (key fields, time semantics, watermarks)
 * - Schema evolution (versioning, compatibility)
 *
 * SEMANTIC VALIDATION NOTES (enforced by compiler, not grammar):
 * - identity block required for most patterns
 * - streaming block required for event_log pattern
 * - state transitions must form valid graph for state_machine
 * - compatibility mode validated against previous version
 */

grammar SchemaDSL;

// ============================================================================
// PARSER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Top-Level Structure
// ----------------------------------------------------------------------------

program
    : importStatement* (schemaDefinition | typeAliasBlock)+ EOF
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
    : DOTDOT | DOT | SLASH | IDENTIFIER | UPPER_IDENTIFIER | MINUS  // Allow: ./path, ../path, /abs/path, PascalCase, path-with-hyphens
    ;

importFileExtension
    : DOT ('schema' | 'transform' | 'flow' | 'rules')  // File extension marks end of import
    ;

schemaDefinition
    : 'schema' schemaName
        patternDecl?
        versionBlock?
        compatibilityDecl?              // Allow standalone evolution/compatibility declaration
        retentionDecl?
        identityBlock?
        streamingBlock?
        fieldsBlock?
        nestedObjectBlock*
        computedBlock?                  // Computed/derived fields
        constraintsBlock?               // Business rule constraints
        immutableDecl?                  // immutable true/false for audit schemas (can appear after fields)
        stateMachineBlock?
        parametersBlock?
        entriesBlock?
        ruleBlock*
        migrationBlock?
      'end'
    ;

schemaName
    : IDENTIFIER
    | mutationPattern                   // Allow pattern keywords as schema names
    | timeSemanticsType                 // Allow event_time, processing_time as names
    ;

// ----------------------------------------------------------------------------
// Pattern Declaration (The 9 Mutation Patterns)
// ----------------------------------------------------------------------------

patternDecl
    : 'pattern' mutationPattern (',' mutationPattern)*
    ;

mutationPattern
    : 'master_data'                   // SCD Type 2 with full history
    | 'immutable_ledger'              // Append-only financial records
    | 'versioned_configuration'       // Immutable versions with effective dates
    | 'operational_parameters'        // Hot-reloadable parameters
    | 'event_log'                     // Append-only event stream
    | 'state_machine'                 // Workflow state tracking
    | 'temporal_data'                 // Effective-dated values
    | 'reference_data'                // Lookup tables
    | 'business_logic'                // Compiled rules
    | 'command'                       // Command/request pattern
    | 'response'                      // Response pattern
    | 'aggregate'                     // Aggregate/summary pattern
    | 'document'                      // Document/output pattern
    | 'audit_event'                   // Audit trail events
    ;

// ----------------------------------------------------------------------------
// Version Block (Schema Evolution)
// ----------------------------------------------------------------------------

versionBlock
    : 'version' VERSION_NUMBER
      compatibilityDecl?
      previousVersionDecl?
      deprecationDecl?
      migrationGuideDecl?
    ;

compatibilityDecl
    : ('compatibility' | 'evolution') compatibilityMode
    ;

compatibilityMode
    : 'backward'                      // New reads old
    | 'forward'                       // Old reads new
    | 'full'                          // Both directions
    | 'none'                          // Breaking changes allowed
    | 'backward_compatible'           // Alias for backward
    | 'forward_compatible'            // Alias for forward
    ;

previousVersionDecl
    : 'previous_version' VERSION_NUMBER
    ;

deprecationDecl
    : 'deprecated' ':' STRING
      ('deprecated_since' ':' STRING)?
      ('removal_version' ':' VERSION_NUMBER)?
    ;

migrationGuideDecl
    : 'migration_guide' ':' (STRING | MULTILINE_STRING)
    ;

// ----------------------------------------------------------------------------
// Retention Declaration
// ----------------------------------------------------------------------------

retentionDecl
    : 'retention' duration
    ;

// ----------------------------------------------------------------------------
// Immutable Declaration (for audit schemas)
// ----------------------------------------------------------------------------

immutableDecl
    : 'immutable' BOOLEAN
    ;

// ----------------------------------------------------------------------------
// Constraints Block (business rule validation)
// ----------------------------------------------------------------------------

constraintsBlock
    : 'constraints' constraintDecl+ 'end'
    ;

constraintDecl
    : condition 'as' STRING             // field > 0 as "Message"
    ;

// ----------------------------------------------------------------------------
// Identity Block
// ----------------------------------------------------------------------------

identityBlock
    : 'identity' identityField+ 'end'
    ;

identityField
    : fieldName ':' fieldType fieldQualifier* ','?
    ;

// ----------------------------------------------------------------------------
// Streaming Block
// ----------------------------------------------------------------------------

streamingBlock
    : 'streaming' streamingDecl+ 'end'
    ;

streamingDecl
    : keyFieldsDecl
    | timeFieldDecl
    | timeSemanticsDecl
    | watermarkDecl
    | lateDataDecl
    | allowedLatenessDecl
    | idleDecl
    | sparsityDecl
    | retentionBlockDecl
    ;

keyFieldsDecl
    : 'key_fields' ':' fieldArray
    ;

timeFieldDecl
    : 'time_field' ':' (fieldPath | timeSemanticsType)  // Allow time_field: event_time (common naming pattern)
    ;

timeSemanticsDecl
    : 'time_semantics' ':' timeSemanticsType
    ;

timeSemanticsType
    : 'event_time'
    | 'processing_time'
    | 'ingestion_time'
    ;

watermarkDecl
    : 'watermark_delay' ':' duration
    | 'watermark_strategy' ':' watermarkStrategy
    | 'max_out_of_orderness' ':' duration
    | 'watermark_interval' ':' duration
    | 'watermark_field' ':' fieldPath
    ;

watermarkStrategy
    : 'bounded_out_of_orderness'
    | 'periodic'
    | 'punctuated'
    ;

lateDataDecl
    : 'late_data_handling' ':' lateDataStrategy
    | 'late_data_stream' ':' IDENTIFIER
    ;

lateDataStrategy
    : 'side_output'
    | 'drop'
    | 'update'
    ;

allowedLatenessDecl
    : 'allowed_lateness' ':' duration
    ;

idleDecl
    : 'idle_timeout' ':' duration
    | 'idle_behavior' ':' idleBehavior
    ;

idleBehavior
    : 'mark_idle'
    | 'advance_to_infinity'
    | 'keep_waiting'
    ;

sparsityDecl
    : 'sparsity' sparsityBlock 'end'
    ;

sparsityBlock
    : ('dense' ':' fieldArray)?
      ('moderate' ':' fieldArray)?
      ('sparse' ':' fieldArray)?
    ;

retentionBlockDecl
    : 'retention' retentionOptions 'end'
    ;

retentionOptions
    : ('time' ':' duration)?
      ('size' ':' sizeSpec)?
      ('policy' ':' retentionPolicy)?
    ;

retentionPolicy
    : 'delete_oldest'
    | 'archive'
    | 'compact'
    ;

// ----------------------------------------------------------------------------
// Fields Block
// ----------------------------------------------------------------------------

fieldsBlock
    : 'fields' fieldDecl+ 'end'
    ;

fieldDecl
    : fieldName ':' fieldType fieldQualifier* ','?
    ;

fieldName
    : IDENTIFIER
    | timeSemanticsType                 // Allow event_time, processing_time as field names
    | stateQualifier                    // Allow initial, terminal as field names
    ;

// ----------------------------------------------------------------------------
// Nested Object Block
// ----------------------------------------------------------------------------

nestedObjectBlock
    : fieldName ':' 'object' fieldDecl* nestedObjectBlock* 'end'
    | fieldName ':' 'list' LANGLE 'object' RANGLE fieldDecl* nestedObjectBlock* 'end'
    ;

// ----------------------------------------------------------------------------
// Computed Block (derived fields calculated from other fields)
// ----------------------------------------------------------------------------

computedBlock
    : 'computed' computedField+ 'end'
    ;

computedField
    : fieldName '=' computedExpression
    ;

// Computed expressions support arithmetic, when/then/else, and field references
computedExpression
    : computedExpression (STAR | SLASH) computedExpression      // Multiplication/Division (highest precedence)
    | computedExpression (PLUS | MINUS) computedExpression      // Addition/Subtraction
    | computedExpression comparisonOp computedExpression        // Comparisons
    | computedExpression 'and' computedExpression               // Logical AND
    | computedExpression 'or' computedExpression                // Logical OR
    | 'not' computedExpression                                  // Logical NOT
    | '(' computedExpression ')'                                // Parenthesized expression
    | computedWhenExpression                                    // Conditional expression
    | functionCall                                              // Function call
    | fieldPath                                                 // Field reference
    | literal                                                   // Literal value
    ;

computedWhenExpression
    : 'when' computedExpression 'then' computedExpression
      ('when' computedExpression 'then' computedExpression)*
      'else' computedExpression
    ;

// ----------------------------------------------------------------------------
// State Machine Block (for state_machine pattern)
// ----------------------------------------------------------------------------

stateMachineBlock
    : forEntityDecl?
      statesBlock
      initialStateDecl?
      transitionsBlock?
      onTransitionBlock?
    ;

// Explicit initial state declaration (alternative to inline :initial qualifier)
initialStateDecl
    : 'initial_state' ':' IDENTIFIER
    ;

forEntityDecl
    : 'for_entity' ':' IDENTIFIER
    ;

// New intuitive states block: states ... end with optional qualifiers
statesBlock
    : 'states' (statesDecl | stateDefList) 'end'?
    ;

// Original compact syntax: states: [s1, s2, s3]
statesDecl
    : ':' stateArray
    ;

// New intuitive syntax: each state on its own line
stateDefList
    : stateDef+
    ;

stateDef
    : IDENTIFIER (':' stateQualifier)?     // received: initial OR just received
    ;

stateQualifier
    : 'initial'
    | 'terminal'
    | 'final'                              // alias for terminal
    ;

stateArray
    : '[' IDENTIFIER (',' IDENTIFIER)* ']'
    ;

// Transitions block supports both syntaxes
transitionsBlock
    : 'transitions' (transitionDecl | transitionArrowDecl)+ 'end'
    ;

// Original syntax: from state: [target1, target2]
transitionDecl
    : 'from' IDENTIFIER ':' stateArray
    ;

// New arrow syntax: state -> state: trigger_event
transitionArrowDecl
    : (IDENTIFIER | '*') ARROW IDENTIFIER (':' IDENTIFIER)?  // from -> to: trigger
    ;

onTransitionBlock
    : 'on_transition' transitionAction+ 'end'
    ;

transitionAction
    : 'to' IDENTIFIER ':' actionCall
    ;

actionCall
    : IDENTIFIER '(' (STRING (',' STRING)*)? ')'
    ;

// ----------------------------------------------------------------------------
// Parameters Block (for operational_parameters pattern)
// ----------------------------------------------------------------------------

parametersBlock
    : 'parameters' parameterDecl+ 'end'
    ;

parameterDecl
    : fieldName ':' fieldType
        parameterOption*
    ;

parameterOption
    : 'default' ':' literal
    | 'range' ':' rangeSpec
    | 'can_schedule' ':' BOOLEAN
    | 'change_frequency' ':' IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Entries Block (for reference_data pattern)
// ----------------------------------------------------------------------------

entriesBlock
    : 'entries' entryDecl+ 'end'
    ;

entryDecl
    : IDENTIFIER ':'
        entryField+
    ;

entryField
    : fieldName ':' literal
    | 'deprecated' ':' BOOLEAN
    | 'deprecated_reason' ':' STRING
    ;

// ----------------------------------------------------------------------------
// Rule Block (for business_logic pattern)
// ----------------------------------------------------------------------------

ruleBlock
    : 'rule' IDENTIFIER
        givenBlock
        calculateBlock?
        returnBlock
      'end'
    ;

givenBlock
    : 'given' ruleFieldDecl+ 'end'
    ;

ruleFieldDecl
    : fieldName ':' fieldType
    ;

calculateBlock
    : 'calculate' calculation+ 'end'
    ;

calculation
    : fieldName '=' expression
    ;

returnBlock
    : 'return' ruleFieldDecl+ 'end'
    ;

// ----------------------------------------------------------------------------
// Migration Block
// ----------------------------------------------------------------------------

migrationBlock
    : 'migration' migrationStatement+ 'end'
    ;

migrationStatement
    : fieldPath '=' expression
    | '(' fieldList ')' '=' functionCall
    ;

// ----------------------------------------------------------------------------
// Type Alias Block
// ----------------------------------------------------------------------------

typeAliasBlock
    : 'types' typeAlias+ 'end'
    ;

typeAlias
    : aliasName ':' fieldType constraint*
    | aliasName ':' 'object' fieldDecl* 'end'
    ;

aliasName
    : UPPER_IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Type System
// ----------------------------------------------------------------------------

fieldType
    : baseType constraint*                      // string, integer, etc.
    | collectionType                            // list<T>, set<T>, map<K,V>
    | inlineObjectType                          // object { fieldDecl* }
    | IDENTIFIER                                // Custom/domain type
    | UPPER_IDENTIFIER                          // Type alias reference
    ;

// Inline object type: object { field: type, ... }
inlineObjectType
    : 'object' LBRACE inlineFieldDecl* RBRACE
    ;

inlineFieldDecl
    : fieldName ':' fieldType fieldQualifier*
    ;

baseType
    : 'string'
    | 'integer'
    | 'decimal'
    | 'boolean'
    | 'date'
    | 'timestamp'
    | 'uuid'
    | 'bytes'
    | 'bizdate'      // Business date - validated against calendar
    ;

collectionType
    : 'list' LANGLE fieldType RANGLE
    | 'set' LANGLE fieldType RANGLE
    | 'map' LANGLE fieldType ',' fieldType RANGLE
    ;

constraint
    : '[' constraintSpec (',' constraintSpec)* ']'
    ;

constraintSpec
    : 'range' ':' rangeSpec
    | 'length' ':' lengthSpec
    | 'pattern' ':' STRING
    | 'values' ':' valueList
    | 'precision' ':' INTEGER (',' 'scale' ':' INTEGER)?
    | 'scale' ':' INTEGER
    ;

rangeSpec
    : numberLiteral '..' numberLiteral          // Inclusive range
    | '..' numberLiteral                        // Max only
    | numberLiteral '..'                        // Min only
    ;

lengthSpec
    : INTEGER                                   // Exact length
    | INTEGER '..' INTEGER                      // Length range
    | '..' INTEGER                              // Max length
    | INTEGER '..'                              // Min length
    ;

valueList
    : IDENTIFIER (',' IDENTIFIER)*
    | STRING (',' STRING)*
    ;

// ----------------------------------------------------------------------------
// Field Qualifiers
// ----------------------------------------------------------------------------

fieldQualifier
    : 'required'
    | 'optional'
    | 'unique'
    | 'cannot_change'
    | 'encrypted'
    | piiModifier
    | defaultClause
    | deprecatedClause
    ;

// ----------------------------------------------------------------------------
// PII Modifier (Voltage Encryption)
// ----------------------------------------------------------------------------
// Syntax: pii.profile_name or just pii (defaults to full encryption)
// Examples:
//   ssn: string required pii.ssn           // SSN format - last 4 clear
//   card_number: string pii.pan            // Credit card - first 4 + last 4 clear
//   email: string pii.email                // Email format preserving
//   secret: string pii                     // Full encryption (default)
//   custom_field: string pii.my_profile    // Custom profile from config

piiModifier
    : PII DOT IDENTIFIER                    // pii.ssn, pii.pan, pii.custom
    | PII                                   // pii (defaults to full encryption)
    ;

defaultClause
    : 'default' ':' (literal | functionCall)
    ;

deprecatedClause
    : 'deprecated' ':' STRING
    | 'removal' ':' VERSION_NUMBER
    ;

// ----------------------------------------------------------------------------
// Expressions (for calculations and migrations)
// ----------------------------------------------------------------------------

expression
    : literal
    | fieldPath
    | functionCall
    | timeUnit                          // Allow time units as expression (e.g., years, days)
    | expression operator expression
    | '(' expression ')'
    | whenExpression
    ;

whenExpression
    : 'when' condition ':' expression
      ('when' condition ':' expression)*
      'otherwise' ':' expression
    ;

condition
    : expression comparisonOp expression
    | expression 'and' condition
    | expression 'or' condition
    | '(' condition ')'
    ;

comparisonOp
    : EQ | NE | LANGLE | RANGLE | LE | GE
    ;

operator
    : '+' | '-' | '*' | '/'
    ;

functionCall
    : IDENTIFIER '(' (expression (',' expression)*)? ')'
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

fieldArray
    : '[' fieldPath (',' fieldPath)* ']'
    | '[' ']'                                   // Empty array (broadcast)
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
    | 'weeks'   | 'week'
    | 'months'  | 'month'
    | 'years'   | 'year'
    | 'milliseconds' | 'millisecond'
    ;

sizeSpec
    : INTEGER sizeUnit
    ;

sizeUnit
    : 'bytes' | 'KB' | 'MB' | 'GB' | 'TB'
    ;

literal
    : STRING
    | numberLiteral
    | BOOLEAN
    | 'null'
    ;

numberLiteral
    : INTEGER
    | DECIMAL
    | '-' INTEGER
    | '-' DECIMAL
    ;

// ============================================================================
// LEXER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Keywords (grouped by category)
// ----------------------------------------------------------------------------

// Structure: schema, end, types
// Patterns: master_data, immutable_ledger, versioned_configuration,
//           operational_parameters, event_log, state_machine, temporal_data,
//           reference_data, business_logic
// Version: version, compatibility, backward, forward, full, none,
//          previous_version, deprecated, deprecated_since, removal_version,
//          migration_guide
// Blocks: identity, streaming, fields, parameters, entries, rule, migration,
//         transitions, on_transition, given, calculate, return
// Types: string, integer, decimal, boolean, date, timestamp, uuid, bytes,
//        list, set, map, object
// Streaming: key_fields, time_field, time_semantics, event_time, processing_time,
//            ingestion_time, watermark_delay, watermark_strategy, watermark_field,
//            max_out_of_orderness, watermark_interval, bounded_out_of_orderness,
//            periodic, punctuated, late_data_handling, late_data_stream,
//            side_output, drop, update, allowed_lateness, idle_timeout,
//            idle_behavior, mark_idle, advance_to_infinity, keep_waiting,
//            sparsity, dense, moderate, sparse, retention, time, size, policy,
//            delete_oldest, archive, compact
// Qualifiers: required, optional, unique, cannot_change, encrypted, default
// Constraints: range, length, pattern, values, precision, scale
// State machine: for_entity, states, initial_state, from, to
// Expressions: when, otherwise, and, or, null
// Other: retention, pattern

// ----------------------------------------------------------------------------
// Keywords
// ----------------------------------------------------------------------------

// Import (v0.7.0+)
IMPORT : 'import' ;

PII : 'pii' ;

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

VERSION_NUMBER
    : [0-9]+ '.' [0-9]+ '.' [0-9]+
    ;

INTEGER
    : [0-9]+
    ;

DECIMAL
    : [0-9]+ '.' [0-9]+
    ;

DURATION_LITERAL
    : [0-9]+ ('ms' | 's' | 'm' | 'h' | 'd' | 'w')
    ;

BOOLEAN
    : 'true' | 'false'
    ;

IDENTIFIER
    : [a-z_] [a-z0-9_]*
    ;

UPPER_IDENTIFIER
    : [A-Z] [a-zA-Z0-9_]*
    ;

STRING
    : '"' (~["\r\n])* '"'
    ;

MULTILINE_STRING
    : '"""' .*? '"""'
    ;

// ----------------------------------------------------------------------------
// Operators
// ----------------------------------------------------------------------------

COLON : ':' ;
COMMA : ',' ;
DOTDOT : '..' ;                       // Must come before DOT for correct lexing
DOT : '.' ;
LBRACKET : '[' ;
RBRACKET : ']' ;
LPAREN : '(' ;
RPAREN : ')' ;
LANGLE : '<' ;
RANGLE : '>' ;
EQ : '=' | '==' ;                     // Support both = and == for equality
NE : '!=' ;
LE : '<=' ;
GE : '>=' ;
PLUS : '+' ;
MINUS : '-' ;
STAR : '*' ;
SLASH : '/' ;
ARROW : '->' ;
LBRACE : '{' ;
RBRACE : '}' ;

// ----------------------------------------------------------------------------
// Comments and Whitespace
// ----------------------------------------------------------------------------

COMMENT
    : '//' ~[\r\n]* -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
