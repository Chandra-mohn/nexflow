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
        cacheDecl?
        inputSpec
        outputSpec
        validateInputBlock?
        applyBlock
        validateOutputBlock?
        onErrorBlock?
      'end'
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
    : 'list' '<' fieldType '>'
    | 'set' '<' fieldType '>'
    | 'map' '<' fieldType ',' fieldType '>'
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
    | 'default' ':' expression
    ;

// ----------------------------------------------------------------------------
// Apply Block (Transformation Logic)
// ----------------------------------------------------------------------------

applyBlock
    : 'apply' statement+ 'end'
    ;

statement
    : assignment
    | localAssignment
    ;

assignment
    : fieldPath '=' expression
    ;

localAssignment
    : IDENTIFIER '=' expression
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
    : 'on_error' errorAction+ 'end'
    ;

errorAction
    : 'action' ':' errorActionType
    | 'default' ':' expression
    | 'log_level' ':' logLevel
    | 'emit_to' ':' IDENTIFIER
    | 'error_code' ':' STRING
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
    : literal
    | fieldPath
    | functionCall
    | expression binaryOp expression
    | unaryOp expression
    | '(' expression ')'
    | whenExpression
    | betweenExpression
    | inExpression
    | isNullExpression
    | indexExpression
    | optionalChainExpression
    | coalesceExpression
    ;

// When-Otherwise conditional expression
whenExpression
    : 'when' expression ':' expression
      ('when' expression ':' expression)*
      'otherwise' ':' expression
    ;

// Between expression for range checks
betweenExpression
    : expression 'between' expression 'and' expression
    | expression 'not' 'between' expression 'and' expression
    ;

// In expression for set membership
inExpression
    : expression 'in' listLiteral
    | expression 'not' 'in' listLiteral
    ;

// Null check expression
isNullExpression
    : expression 'is' 'null'
    | expression 'is' 'not' 'null'
    ;

// Array/list index expression
indexExpression
    : fieldPath '[' expression ']'
    ;

// Optional chaining for null-safe access
optionalChainExpression
    : fieldPath ('?.' IDENTIFIER)+
    ;

// Null coalescing
coalesceExpression
    : expression '??' expression
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
    : '=' | '!=' | '<' | '>' | '<=' | '>='
    | '=?'                                    // Null-safe equality
    ;

logicalOp
    : 'and' | 'or'
    ;

unaryOp
    : 'not' | '-'
    ;

// Function call
functionCall
    : IDENTIFIER '(' (expression (',' expression)*)? ')'
    ;

// List literal for 'in' expressions
listLiteral
    : '[' (expression (',' expression)*)? ']'
    ;

// ----------------------------------------------------------------------------
// Common Rules
// ----------------------------------------------------------------------------

fieldPath
    : IDENTIFIER ('.' IDENTIFIER)*
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
LANGLE : '<' ;
RANGLE : '>' ;
EQ : '=' ;
NE : '!=' ;
LT : '<' ;
GT : '>' ;
LE : '<=' ;
GE : '>=' ;
NULLSAFE_EQ : '=?' ;
PLUS : '+' ;
MINUS : '-' ;
STAR : '*' ;
SLASH : '/' ;
PERCENT : '%' ;
DOTDOT : '..' ;
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
