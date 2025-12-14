/**
 * TransformDSL - Transform Catalog Domain-Specific Language
 *
 * ANTLR4 Grammar for L3 Transform Catalog DSL
 *
 * Version: 1.0.0
 * Specification: ../L3-Transform-Catalog.md
 *
 * This grammar defines the syntax for data transformations including:
 * - Field-level transforms (single field operations)
 * - Expression-level transforms (multi-input calculations)
 * - Block-level transforms (50+ field mappings)
 * - Transform composition (sequential, parallel, conditional)
 * - Type-safe expressions with null handling
 * - Input/output validation patterns
 *
 * SEMANTIC VALIDATION NOTES (enforced by compiler, not grammar):
 * - Input/output types must be compatible with L2 schemas
 * - Pure transforms cannot have external calls or side effects
 * - Compose references must resolve to existing transforms
 * - Expression types must be consistent across operations
 */

grammar TransformDSL;

// ============================================================================
// PARSER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Top-Level Structure
// ----------------------------------------------------------------------------

program
    : (transformDef | transformBlockDef)+ EOF
    ;

// ----------------------------------------------------------------------------
// Transform Definition (Field/Expression Level)
// ----------------------------------------------------------------------------

transformDef
    : 'transform' transformName
        transformMetadata?
        purityDecl?
        idempotentDecl?
        cacheDecl?
        inputSpec
        lookupDecl?
        lookupsBlock?
        stateDecl?
        paramsBlock?
        outputSpec
        validateInputBlock?
        applyBlock
        validateOutputBlock?
        onErrorBlock?
      'end'
    ;

// Idempotent declaration (safe to retry)
idempotentDecl
    : 'idempotent' ':' BOOLEAN
    ;

// Lookup declaration (external data source)
lookupDecl
    : 'lookup' ':' IDENTIFIER
    ;

// Multiple lookups block
lookupsBlock
    : 'lookups' ':' lookupFieldDecl+ 'end'?
    ;

lookupFieldDecl
    : IDENTIFIER ':' IDENTIFIER
    ;

// State declaration (stateful transforms)
stateDecl
    : 'state' ':' IDENTIFIER
    ;

// Parameters block (parameterized transforms)
paramsBlock
    : 'params' ':' paramDecl+ 'end'?
    ;

paramDecl
    : IDENTIFIER ':' fieldType paramQualifiers?
    ;

paramQualifiers
    : 'required' paramDefault?
    | 'optional' paramDefault?
    | paramDefault
    ;

paramDefault
    : DEFAULT_KW ':' expression
    ;

transformName
    : IDENTIFIER
    ;

transformMetadata
    : versionDecl?
      descriptionDecl?
      previousVersionDecl?
      compatibilityDecl?
    ;

versionDecl
    : 'version' ':' VERSION_NUMBER
    ;

descriptionDecl
    : 'description' ':' STRING
    ;

previousVersionDecl
    : 'previous_version' ':' VERSION_NUMBER
    ;

compatibilityDecl
    : 'compatibility' ':' compatibilityMode
    ;

compatibilityMode
    : 'backward'
    | 'forward'
    | 'full'
    | 'none'
    ;

purityDecl
    : 'pure' ':' BOOLEAN
    ;

cacheDecl
    : 'cache' cacheTtl? cacheKey? 'end'?
    | 'cache' ':' duration                    // Short form
    ;

cacheTtl
    : 'ttl' ':' duration
    ;

cacheKey
    : 'key' ':' fieldArray
    ;

// ----------------------------------------------------------------------------
// Transform Block Definition (Multi-Field Mapping)
// ----------------------------------------------------------------------------

transformBlockDef
    : 'transform_block' transformName
        transformMetadata?
        useBlock?
        inputSpec
        outputSpec
        validateInputBlock?
        invariantBlock?
        (mappingsBlock | composeBlock)
        validateOutputBlock?
        onChangeBlock?
        onErrorBlock?
      'end'
    ;

useBlock
    : 'use' IDENTIFIER+ 'end'
    ;

// ----------------------------------------------------------------------------
// Input Specification
// ----------------------------------------------------------------------------

inputSpec
    : 'input' ':' fieldType qualifiers?       // Single input
    | 'input' inputFieldDecl+ 'end'           // Multiple inputs
    ;

inputFieldDecl
    : fieldName ':' fieldType qualifiers?
    ;

// ----------------------------------------------------------------------------
// Output Specification
// ----------------------------------------------------------------------------

outputSpec
    : 'output' ':' fieldType qualifiers?      // Single output
    | 'output' outputFieldDecl+ 'end'         // Multiple outputs
    ;

outputFieldDecl
    : fieldName ':' fieldType qualifiers?
    ;

// ----------------------------------------------------------------------------
// Type System
// ----------------------------------------------------------------------------

fieldType
    : baseType constraint*                    // string, integer, etc.
    | collectionType                          // list<T>, set<T>, map<K,V>
    | IDENTIFIER                              // Schema reference or custom type
    | UPPER_IDENTIFIER                        // Type alias reference
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
    : numberLiteral '..' numberLiteral        // Inclusive range
    | '..' numberLiteral                      // Max only
    | numberLiteral '..'                      // Min only
    ;

lengthSpec
    : INTEGER                                 // Exact length
    | INTEGER '..' INTEGER                    // Length range
    | '..' INTEGER                            // Max length
    | INTEGER '..'                            // Min length
    ;

valueList
    : IDENTIFIER (',' IDENTIFIER)*
    | STRING (',' STRING)*
    ;

qualifiers
    : ',' qualifier (',' qualifier)*
    ;

qualifier
    : 'nullable'
    | 'required'
    | DEFAULT_KW ':' expression
    ;

// ----------------------------------------------------------------------------
// Apply Block (Transformation Logic)
// ----------------------------------------------------------------------------

applyBlock
    : 'apply' statement+ 'end'
    ;

statement
    : assignment
    | letAssignment
    ;

assignment
    : fieldPath '=' expression
    | IDENTIFIER '=' expression           // Simple identifier assignment
    ;

letAssignment
    : 'let' IDENTIFIER '=' expression     // let x = value for local variables
    ;

// ----------------------------------------------------------------------------
// Mappings Block (Block-Level Transforms)
// ----------------------------------------------------------------------------

mappingsBlock
    : 'mappings' mapping+ 'end'
    ;

mapping
    : fieldPath '=' expression
    ;

// ----------------------------------------------------------------------------
// Compose Block (Transform Composition)
// ----------------------------------------------------------------------------

composeBlock
    : 'compose' composeType? composeRef+ 'end' thenBlock?
    ;

composeType
    : 'sequential'
    | 'parallel'
    | 'conditional'
    ;

composeRef
    : IDENTIFIER                              // Transform reference
    | 'when' expression ':' IDENTIFIER        // Conditional reference
    | 'otherwise' ':' IDENTIFIER              // Default for conditional
    ;

thenBlock
    : 'then' composeType? composeRef+ 'end'
    ;

// ----------------------------------------------------------------------------
// Validation Blocks
// ----------------------------------------------------------------------------

validateInputBlock
    : 'validate_input' validationRule+ 'end'
    ;

validateOutputBlock
    : 'validate_output' validationRule+ 'end'
    ;

validationRule
    : expression ':' validationMessage
    | 'when' expression ':' validationRule+ 'end'
    | 'require' expression 'else' validationMessage   // require ... else syntax
    ;

validationMessage
    : STRING
    | validationMessageObject
    ;

validationMessageObject
    : 'message' ':' STRING
      ('code' ':' STRING)?
      ('severity' ':' severityLevel)?
    ;

severityLevel
    : 'error'
    | 'warning'
    | 'info'
    ;

invariantBlock
    : 'invariant' validationRule+ 'end'
    ;

// ----------------------------------------------------------------------------
// Error Handling
// ----------------------------------------------------------------------------

onErrorBlock
    : 'on_error' errorStatement+ 'end'
    ;

errorStatement
    : errorAction
    | logErrorCall
    | emitStatement
    | rejectStatement
    ;

errorAction
    : 'action' ':' errorActionType
    | DEFAULT_KW ':' expression
    | 'log_level' ':' logLevel
    | 'emit_to' ':' IDENTIFIER
    | 'error_code' ':' STRING
    ;

// log_error("message") function call
logErrorCall
    : 'log_error' '(' STRING ')'
    ;

// emit with defaults/partial data
emitStatement
    : 'emit' 'with' emitMode
    ;

emitMode
    : 'defaults'
    | 'partial' 'data'?
    ;

// reject with code/message
rejectStatement
    : 'reject' 'with' rejectArg
    ;

rejectArg
    : 'code' STRING
    | STRING
    ;

errorActionType
    : 'reject'
    | 'skip'
    | 'use_default'
    | 'raise'
    ;

logLevel
    : 'error'
    | 'warning'
    | 'info'
    | 'debug'
    ;

// On Invalid Block (for validation failures)
onInvalidBlock
    : 'on_invalid' invalidAction+ 'end'
    ;

invalidAction
    : 'reject' ':' BOOLEAN
    | 'error_code' ':' STRING
    | 'error_message' ':' expression
    | 'emit_to' ':' IDENTIFIER
    | 'emit_all_errors' ':' BOOLEAN
    ;

// ----------------------------------------------------------------------------
// On Change Block (Recalculation Triggers)
// ----------------------------------------------------------------------------

onChangeBlock
    : 'on_change' fieldArray recalculateBlock 'end'
    ;

recalculateBlock
    : 'recalculate' assignment+ 'end'
    ;

// ----------------------------------------------------------------------------
// Expression Language
// ----------------------------------------------------------------------------

expression
    : unaryOp expression                                          // Unary operators
    | expression arithmeticOp expression                          // Arithmetic
    | expression comparisonOp expression                          // Comparison
    | expression logicalOp expression                             // Logical
    | expression (DEFAULT_KW | '??') expression                    // Null coalescing
    | expression 'between' expression 'and' expression            // Between
    | expression 'not' 'between' expression 'and' expression      // Not between
    | expression 'in' listLiteral                                 // In set (with brackets)
    | expression 'in' LBRACKET listElements RBRACKET              // In set with curly-style brackets
    | expression 'not' 'in' listLiteral                           // Not in set
    | expression 'is' 'null'                                      // Is null
    | expression 'is' 'not' 'null'                                // Is not null
    | expression 'matches' STRING                                 // Regex matching
    | primaryExpression                                           // Primary (terminals)
    ;

primaryExpression
    : literal
    | fieldPath
    | functionCall
    | '(' expression ')'
    | whenExpression
    | indexExpression
    | optionalChainExpression
    | objectLiteral                                               // Inline object { field: value }
    | lambdaExpression                                            // Lambda: x -> expr
    | listLiteral                                                 // List [a, b, c]
    ;

// Inline object literal { field: value, ... }
objectLiteral
    : LBRACE objectField (',' objectField)* RBRACE
    | LBRACE RBRACE                                               // Empty object
    ;

objectField
    : objectFieldName ':' expression
    ;

// Object field names can be identifiers, strings, or contextual keywords
objectFieldName
    : IDENTIFIER
    | STRING
    | 'input' | 'output' | 'state' | 'error' | 'message' | 'code' | 'key'
    | 'values' | 'pattern' | 'length' | 'range' | 'params' | 'lookup'
    | 'severity' | 'action' | 'data'
    ;

// Lambda expression: x -> expr or (x, y) -> expr
lambdaExpression
    : IDENTIFIER ARROW expression                                  // Single param: x -> expr
    | '(' IDENTIFIER (',' IDENTIFIER)* ')' ARROW expression       // Multi param: (x, y) -> expr
    ;

// List elements (for object-style lists)
listElements
    : expression (',' expression)*
    ;

// When-Otherwise conditional expression
// Supports both forms:
//   when cond : result otherwise : default          (colon style)
//   when cond then result otherwise default         (then/otherwise style)
whenExpression
    : 'when' expression ':' expression
      ('when' expression ':' expression)*
      'otherwise' ':' expression
    | 'when' expression 'then' expression
      ('when' expression 'then' expression)*
      'otherwise' expression
    ;

// Array/list index expression with optional field access after index
indexExpression
    : fieldPath '[' expression ']' ('.' fieldOrKeyword)*
    ;

// Optional chaining for null-safe access
optionalChainExpression
    : fieldPath ('?.' fieldOrKeyword)+               // Optional chain: a?.b?.c
    ;

// Binary operators
binaryOp
    : arithmeticOp
    | comparisonOp
    | logicalOp
    ;

arithmeticOp
    : '+' | '-' | '*' | '/' | '%'
    ;

comparisonOp
    : EQ | '=' | NE | LANGLE | RANGLE | LE | GE   // Allow both == and = for equality
    | NULLSAFE_EQ                             // Null-safe equality
    ;

logicalOp
    : 'and' | 'or'
    ;

unaryOp
    : 'not' | '-'
    ;

// Function call (including method calls like state.get_window(...))
functionCall
    : functionName '(' (expression (',' expression)*)? ')'
    | fieldPath '.' functionName '(' (expression (',' expression)*)? ')'  // Method call on object
    ;

functionName
    : IDENTIFIER
    | 'lookup'      // Allow lookup as function name (also a keyword)
    | 'state'       // Allow state as function name (also a keyword)
    | 'length'      // Allow length as function name (also a keyword)
    | 'values'      // Allow values as function name (also a keyword)
    | 'map'         // Allow map as function name (also collection type)
    | 'list'        // Allow list as function name (also collection type)
    | 'set'         // Allow set as function name (also collection type)
    | 'range'       // Allow range as function name (also constraint keyword)
    | 'pattern'     // Allow pattern as function name (also constraint keyword)
    | 'date'        // Allow date as function name (also base type)
    | 'string'      // Allow string as function name (also base type)
    | 'integer'     // Allow integer as function name (also base type)
    | 'decimal'     // Allow decimal as function name (also base type)
    // Collection functions (RFC: Collection Operations Instead of Loops)
    | 'any'         // any(collection, predicate) -> boolean
    | 'all'         // all(collection, predicate) -> boolean
    | 'none'        // none(collection, predicate) -> boolean
    | 'sum'         // sum(collection, field) -> BigDecimal
    | 'count'       // count(collection) or count(collection, predicate) -> int
    | 'avg'         // avg(collection, field) -> BigDecimal
    | 'max'         // max(collection, field) -> Optional<T>
    | 'min'         // min(collection, field) -> Optional<T>
    | 'filter'      // filter(collection, predicate) -> List<T>
    | 'find'        // find(collection, predicate) -> Optional<T>
    | 'distinct'    // distinct(collection) -> List<T>
    // Calendar functions (Business Date Operations)
    | 'current_business_date'     // current_business_date() -> bizdate
    | 'previous_business_date'    // previous_business_date() -> bizdate
    | 'next_business_date'        // next_business_date() -> bizdate
    | 'add_business_days'         // add_business_days(date, n) -> bizdate
    | 'is_business_day'           // is_business_day(date) -> boolean
    | 'is_holiday'                // is_holiday(date) -> boolean
    | 'business_days_between'     // business_days_between(start, end) -> integer
    ;

// List literal for 'in' expressions
listLiteral
    : '[' (expression (',' expression)*)? ']'
    ;

// ----------------------------------------------------------------------------
// Common Rules
// ----------------------------------------------------------------------------

fieldPath
    : fieldOrKeyword ('.' fieldOrKeyword)*
    ;

// Allow contextual keywords to be used as field names in expressions
fieldOrKeyword
    : IDENTIFIER
    | 'input'       // Keywords also used as field references
    | 'output'
    | 'state'
    | 'error'
    | 'message'
    | 'code'
    | 'key'
    | 'values'
    | 'pattern'
    | 'length'
    | 'range'
    | 'params'      // Parameter references
    | 'lookup'      // Lookup object references
    | 'lookups'     // Lookups block reference
    | 'severity'    // Alert severity level
    | 'action'      // Action field
    | 'data'        // Data field
    ;

fieldArray
    : '[' fieldPath (',' fieldPath)* ']'
    ;

fieldName
    : IDENTIFIER
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

// Structure: transform, transform_block, end, input, output, apply, mappings
// Composition: compose, sequential, parallel, conditional, use, then
// Validation: validate_input, validate_output, invariant, on_invalid, on_error
// Metadata: version, description, previous_version, compatibility, backward, forward, full, none
// Purity: pure, cache, ttl, key
// Types: string, integer, decimal, boolean, date, timestamp, uuid, bytes, list, set, map
// Constraints: range, length, pattern, values, precision, scale
// Qualifiers: nullable, required, default
// Expressions: when, otherwise, between, in, is, not, and, or, null
// Actions: action, reject, skip, use_default, raise, emit_to, emit_all_errors
// Recalculation: on_change, recalculate
// Error handling: error_code, error_message, log_level, severity
// Severity levels: error, warning, info, debug
// Compatibility modes: backward, forward, full, none

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
    : 'true' | 'false' | 'yes' | 'no'
    ;

// Keywords that must be recognized before IDENTIFIER
DEFAULT_KW
    : 'default'
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

// ----------------------------------------------------------------------------
// Operators
// ----------------------------------------------------------------------------

COLON : ':' ;
COMMA : ',' ;
DOT : '.' ;
LBRACKET : '[' ;
RBRACKET : ']' ;
LPAREN : '(' ;
RPAREN : ')' ;
LBRACE : '{' ;
RBRACE : '}' ;
LANGLE : '<' ;
RANGLE : '>' ;
EQ : '==' | '=' ;                        // Support both == and = for comparison
NE : '!=' ;
LE : '<=' ;
GE : '>=' ;
NULLSAFE_EQ : '=?' ;
PLUS : '+' ;
MINUS : '-' ;
STAR : '*' ;
SLASH : '/' ;
PERCENT : '%' ;
DOTDOT : '..' ;
ARROW : '->' ;                           // Lambda arrow
OPTIONAL_CHAIN : '?.' ;
COALESCE : '??' ;

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
