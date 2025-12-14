/**
 * RulesDSL - Business Rules Domain-Specific Language
 *
 * ANTLR4 Grammar for L4 Business Rules DSL
 *
 * Version: 1.1.0
 * Specification: docs/L4-Business-Rules.md
 *
 * This grammar defines the syntax for business rules including:
 * - Decision Tables: Matrix-based logic for multi-condition scenarios
 * - Procedural Rules: Full if-then-elseif-else chains with nesting
 * - Hit Policies: first_match, single_hit, multi_hit
 * - Condition Types: equals, range, in_set, pattern, null_check
 * - Action Types: assign, calculate, lookup, call, emit
 *
 * MERGED FROM:
 * - docs/grammar/RulesDSL.g4 (decision tables, money/percentage literals)
 * - rules-dsl/Rules.g4 (rich procedural rules, dual quotes, nested blocks)
 *
 * SEMANTIC VALIDATION NOTES (enforced by compiler, not grammar):
 * - Decision tables should have exhaustive conditions (wildcard row)
 * - No overlapping conditions (except with explicit priority)
 * - Actions must be registered in action catalog
 * - Type checking for conditions against input types
 */

grammar RulesDSL;

// ============================================================================
// PARSER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Top-Level Structure
// ----------------------------------------------------------------------------

program
    : servicesBlock? actionsBlock? (decisionTableDef | proceduralRuleDef)+ EOF
    ;

// ----------------------------------------------------------------------------
// Services Block (External Service Declarations)
// ----------------------------------------------------------------------------

servicesBlock
    : SERVICES LBRACE serviceDecl+ RBRACE
    ;

serviceDecl
    : serviceName COLON serviceType serviceClassName DOT serviceMethodName
      LPAREN serviceParamList? RPAREN ARROW serviceReturnType
      serviceOptions?
    ;

serviceName
    : IDENTIFIER
    ;

serviceClassName
    : IDENTIFIER
    ;

serviceMethodName
    : IDENTIFIER
    | LOOKUP          // Allow 'lookup' as method name
    | EMIT            // Allow 'emit' as method name
    | MATCHES         // Allow 'matches' as method name
    | CONTAINS        // Allow 'contains' as method name
    ;

serviceType
    : SYNC
    | ASYNC
    | CACHED LPAREN duration RPAREN
    ;

serviceParamList
    : serviceParam (COMMA serviceParam)*
    ;

serviceParam
    : IDENTIFIER COLON paramType
    ;

serviceReturnType
    : paramType
    ;

serviceOptions
    : serviceOption+
    ;

serviceOption
    : TIMEOUT COLON duration
    | FALLBACK COLON literal
    | RETRY COLON INTEGER
    ;

duration
    : INTEGER durationUnit
    ;

durationUnit
    : MS
    | S
    | M
    | H
    ;

// ----------------------------------------------------------------------------
// Actions Block (Action Method Declarations)
// RFC REFERENCE: See docs/RFC-Method-Implementation-Strategy.md (Solution 5)
// ----------------------------------------------------------------------------

actionsBlock
    : ACTIONS LBRACE actionDecl+ RBRACE
    ;

actionDecl
    : actionDeclName LPAREN actionParamList? RPAREN ARROW actionTarget
    ;

actionDeclName
    : IDENTIFIER
    ;

actionParamList
    : actionParam (COMMA actionParam)*
    ;

actionParam
    : IDENTIFIER COLON paramType
    ;

actionTarget
    : emitTarget        // -> emit to output_name
    | stateTarget       // -> state state_name.operation(...)
    | auditTarget       // -> audit
    | callTarget        // -> call ServiceName.method
    ;

emitTarget
    : EMIT TO IDENTIFIER
    ;

stateTarget
    : STATE IDENTIFIER DOT stateOperation
    ;

stateOperation
    : IDENTIFIER                                    // Simple operation like 'add', 'clear'
    | IDENTIFIER LPAREN stateOperationArg RPAREN    // Operation with argument like 'add(flag)'
    ;

stateOperationArg
    : IDENTIFIER
    | DQUOTED_STRING
    ;

auditTarget
    : AUDIT
    ;

callTarget
    : CALL IDENTIFIER DOT IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Decision Table Definition
// ----------------------------------------------------------------------------

decisionTableDef
    : DECISION_TABLE tableName
        hitPolicyDecl?
        descriptionDecl?
        versionDecl?
        givenBlock
        decideBlock
        (returnSpec | executeSpec | hybridSpec)?
        postCalculateBlock?
        aggregateBlock?
      END
    ;

// Version declaration for decision tables
versionDecl
    : VERSION COLON VERSION_NUMBER
    ;

tableName
    : IDENTIFIER
    ;

hitPolicyDecl
    : HIT_POLICY hitPolicyType
    ;

hitPolicyType
    : FIRST_MATCH
    | SINGLE_HIT
    | MULTI_HIT
    | COLLECT_ALL
    ;

descriptionDecl
    : DESCRIPTION stringLiteral
    ;

stringLiteral
    : DQUOTED_STRING
    | SQUOTED_STRING
    ;

// ----------------------------------------------------------------------------
// Given Block (Input Parameters)
// ----------------------------------------------------------------------------

givenBlock
    : GIVEN COLON inputParam+
    ;

inputParam
    : paramName COLON paramType inlineComment?
    ;

paramName
    : IDENTIFIER
    | PRIORITY          // 'priority' can be a param name
    | DESCRIPTION       // 'description' can be a param name
    | TEXT_TYPE         // 'text' can be a param name
    | VERSION           // 'version' can be a param name
    ;

paramType
    : baseType
    | MONEY_TYPE
    | PERCENTAGE_TYPE
    | IDENTIFIER                              // Custom type reference
    ;

baseType
    : TEXT_TYPE
    | NUMBER_TYPE
    | BOOLEAN_TYPE
    | DATE_TYPE
    | TIMESTAMP_TYPE
    | BIZDATE_TYPE       // v0.6.0+: Business date type
    ;

inlineComment
    : LINE_COMMENT_INLINE
    ;

// ----------------------------------------------------------------------------
// Decide Block (Decision Matrix)
// ----------------------------------------------------------------------------

decideBlock
    : DECIDE COLON tableMatrix
    ;

tableMatrix
    : tableHeader tableSeparator tableRow+
    ;

tableHeader
    : PIPE priorityHeader? columnHeader+
    ;

priorityHeader
    : PRIORITY PIPE
    ;

columnHeader
    : columnName PIPE
    ;

columnName
    : IDENTIFIER
    | PRIORITY          // 'priority' can be a column name
    | DESCRIPTION       // 'description' can be a column name
    | TEXT_TYPE         // 'text' can be a column name
    | VERSION           // 'version' can be a column name
    | DEFAULT           // 'default' can be a column name
    | RETURN            // 'return' can be a column name
    ;

tableSeparator
    : PIPE SEP PIPE
    ;

tableRow
    : PIPE priorityCell? cell+
    ;

priorityCell
    : INTEGER PIPE
    ;

cell
    : cellContent PIPE
    ;

cellContent
    : condition
    | action
    ;

// ----------------------------------------------------------------------------
// Condition Types
// ----------------------------------------------------------------------------

condition
    : STAR                                    // * (any/wildcard)
    | exactMatch                              // Exact value
    | rangeCondition                          // 700-799, >= 700, < 0.3
    | setCondition                            // IN (a, b, c), NOT IN
    | patternCondition                        // matches "regex"
    | nullCondition                           // is null, is not null
    | comparisonCondition                     // > 1000, >= 700, != "closed"
    | expressionCondition                     // Complex boolean expression
    | markerStateCondition                    // v0.6.0+: marker eod_1 fired
    ;

exactMatch
    : literal
    ;

rangeCondition
    : numberLiteral TO numberLiteral          // 700 to 799 (inclusive range)
    | MONEY_LITERAL TO MONEY_LITERAL          // $100 to $500
    ;

setCondition
    : IN LPAREN valueList RPAREN
    | NOT IN LPAREN valueList RPAREN
    ;

patternCondition
    : MATCHES stringLiteral
    | ENDS_WITH stringLiteral
    | STARTS_WITH stringLiteral
    | CONTAINS stringLiteral
    ;

nullCondition
    : IS NULL
    | IS NOT NULL
    | IS_NULL
    | IS_NOT_NULL
    ;

comparisonCondition
    : comparisonOp valueExpr
    ;

expressionCondition
    : LPAREN booleanExpr RPAREN
    ;

// v0.6.0+: Marker state condition for phase-aware rules
markerStateCondition
    : MARKER IDENTIFIER FIRED                     // marker eod_1 fired
    | MARKER IDENTIFIER PENDING                   // marker eod_1 pending
    | BETWEEN_MARKERS IDENTIFIER AND IDENTIFIER   // between eod_1 and eod_2
    ;

// ----------------------------------------------------------------------------
// Action Types
// ----------------------------------------------------------------------------

action
    : STAR                                    // * (no action/wildcard)
    | assignAction                            // Literal value
    | calculateAction                         // Expression
    | lookupAction                            // lookup(table, key)
    | callAction                              // function(args)
    | emitAction                              // emit to stream
    ;

assignAction
    : literal
    ;

calculateAction
    : arithmeticExpr
    ;

lookupAction
    : LOOKUP LPAREN IDENTIFIER (COMMA valueExpr)* (COMMA DEFAULT COLON valueExpr)? RPAREN
    | LOOKUP LPAREN IDENTIFIER COMMA AS_OF COLON valueExpr RPAREN
    ;

callAction
    : IDENTIFIER LPAREN (actionArg (COMMA actionArg)*)? RPAREN
    ;

actionArg
    : valueExpr
    | IDENTIFIER COLON valueExpr              // Named argument
    ;

emitAction
    : EMIT TO IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Return/Execute Specifications
// ----------------------------------------------------------------------------

returnSpec
    : RETURN COLON returnParam+
    ;

returnParam
    : paramName COLON paramType
    ;

executeSpec
    : EXECUTE COLON executeType
    ;

executeType
    : YES
    | MULTI
    | IDENTIFIER
    ;

hybridSpec
    : returnSpec executeSpec
    ;

// Post-calculate block for derived computations after decision table
postCalculateBlock
    : POST_CALCULATE COLON postCalculateStatement+
    ;

postCalculateStatement
    : letStatement
    | assignmentStatement
    ;

// Assignment without 'let' or 'set' keyword: variable = expression
assignmentStatement
    : IDENTIFIER EQ valueExpr
    | IDENTIFIER EQ whenExpression
    ;

// Aggregate block for collect_all results
aggregateBlock
    : AGGREGATE COLON aggregateStatement+
    ;

aggregateStatement
    : IDENTIFIER EQ valueExpr
    ;

// When expression (inline conditional): when condition then result otherwise default
whenExpression
    : WHEN booleanExpr THEN valueExpr (WHEN booleanExpr THEN valueExpr)* OTHERWISE valueExpr
    ;

// ----------------------------------------------------------------------------
// Procedural Rule Definition (Enhanced from rules-dsl)
// ----------------------------------------------------------------------------

proceduralRuleDef
    : RULE ruleName COLON
        descriptionDecl?
        blockItem+
      END
    ;

ruleName
    : IDENTIFIER
    | DQUOTED_STRING
    | SQUOTED_STRING
    ;

blockItem
    : ruleStep
    | setStatement
    | letStatement
    | actionSequence
    | returnStatement
    ;

// Assignment statement: set variable = expression
setStatement
    : SET IDENTIFIER EQ valueExpr
    ;

// Local variable declaration: let variable = expression
letStatement
    : LET IDENTIFIER EQ valueExpr
    ;

ruleStep
    : IF booleanExpr THEN block
      (ELSEIF booleanExpr THEN block)*
      (ELSE block)?
      ENDIF
    ;

block
    : blockItem+
    ;

actionSequence
    : actionCall (COMMA actionCall)*
    ;

actionCall
    : IDENTIFIER (LPAREN parameterList? RPAREN)?
    | DQUOTED_STRING (LPAREN parameterList? RPAREN)?
    ;

parameterList
    : parameter (COMMA parameter)*
    ;

parameter
    : valueExpr
    ;

returnStatement
    : RETURN
    ;

// ----------------------------------------------------------------------------
// Boolean Expression Language
// ----------------------------------------------------------------------------

booleanExpr
    : booleanTerm ((AND | OR) booleanTerm)*
    ;

booleanTerm
    : NOT? booleanFactor
    ;

booleanFactor
    : comparisonExpr
    | LPAREN booleanExpr RPAREN
    | functionCall
    ;

comparisonExpr
    : valueExpr comparisonOp valueExpr
    | valueExpr IN LPAREN valueList RPAREN
    | valueExpr NOT IN LPAREN valueList RPAREN
    | valueExpr IN listLiteral
    | valueExpr NOT IN listLiteral
    | valueExpr IN fieldPath
    | valueExpr NOT IN fieldPath
    | valueExpr IS NULL
    | valueExpr IS NOT NULL
    | valueExpr IS_NULL
    | valueExpr IS_NOT_NULL
    ;

comparisonOp
    : EQ | NE | LT | GT | LE | GE
    ;

// ----------------------------------------------------------------------------
// Value Expression Language
// ----------------------------------------------------------------------------

valueExpr
    : term ((PLUS | MINUS) term)*
    ;

term
    : factor ((STAR | SLASH | PERCENT | MOD) factor)*
    ;

factor
    : MINUS? atom
    ;

atom
    : literal
    | fieldPath
    | collectionExpr       // Collection operations (any, all, sum, filter, etc.)
    | functionCall
    | listLiteral
    | objectLiteral
    | lambdaExpression
    | LPAREN valueExpr RPAREN
    ;

// ----------------------------------------------------------------------------
// Collection Expressions (RFC: Collection Operations Instead of Loops)
// ----------------------------------------------------------------------------

collectionExpr
    : predicateFunction LPAREN valueExpr COMMA collectionPredicate RPAREN      // any(items, amount > 100)
    | aggregateFunction LPAREN valueExpr (COMMA fieldPath)? RPAREN             // sum(items, price) or count(items)
    | transformFunction LPAREN valueExpr COMMA collectionPredicate RPAREN      // filter(items, active = true)
    ;

predicateFunction
    : ANY
    | ALL
    | NONE
    ;

aggregateFunction
    : SUM
    | COUNT
    | AVG
    | MAX_FN
    | MIN_FN
    ;

transformFunction
    : FILTER
    | FIND
    | DISTINCT
    ;

// Collection predicate - inline condition for collection operations
// Supports: field comparisons, set membership, compound conditions, lambdas
collectionPredicate
    : lambdaExpression                                           // Full lambda: t -> t.amount > 1000
    | collectionPredicateOr                                      // Inline predicate: amount > 1000
    ;

collectionPredicateOr
    : collectionPredicateAnd (OR collectionPredicateAnd)*
    ;

collectionPredicateAnd
    : collectionPredicateAtom (AND collectionPredicateAtom)*
    ;

collectionPredicateAtom
    : NOT collectionPredicateAtom                                // not active
    | fieldPath comparisonOp valueExpr                           // amount > 1000
    | fieldPath IN LPAREN valueList RPAREN                       // type in ("A", "B")
    | fieldPath NOT IN LPAREN valueList RPAREN                   // type not in ("X")
    | fieldPath IS NULL                                          // description is null
    | fieldPath IS NOT NULL                                      // value is not null
    | LPAREN collectionPredicateOr RPAREN                        // (amount > 100 and active)
    ;

// Lambda expression: x -> expression or (x, y) -> expression
lambdaExpression
    : IDENTIFIER ARROW valueExpr
    | LPAREN IDENTIFIER (COMMA IDENTIFIER)* RPAREN ARROW valueExpr
    ;

arithmeticExpr
    : valueExpr
    ;

functionCall
    : IDENTIFIER LPAREN (valueExpr (COMMA valueExpr)*)? RPAREN
    ;

fieldPath
    : attributeIdentifier (DOT attributeIdentifier)*
    | IDENTIFIER LBRACKET INTEGER RBRACKET (DOT attributeIdentifier)*
    ;

attributeIdentifier
    : IDENTIFIER
    | DQUOTED_STRING                          // For attribute names with special chars
    ;

valueList
    : valueExpr (COMMA valueExpr)*
    ;

listLiteral
    : LBRACKET (valueExpr (COMMA valueExpr)*)? RBRACKET
    ;

// Object literal: {key: value, key2: value2}
objectLiteral
    : LBRACE (objectField (COMMA objectField)*)? RBRACE
    ;

objectField
    : objectFieldName COLON valueExpr
    ;

objectFieldName
    : IDENTIFIER
    | DQUOTED_STRING
    | TEXT_TYPE         // 'text' can be a field name in objects
    | DESCRIPTION       // 'description' can be a field name in objects
    | PRIORITY          // 'priority' can be a field name in objects
    | RETURN            // 'return' can be a field name in objects
    | DEFAULT           // 'default' can be a field name in objects
    ;

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

literal
    : stringLiteral
    | numberLiteral
    | MONEY_LITERAL
    | PERCENTAGE_LITERAL
    | BOOLEAN
    | NULL
    ;

numberLiteral
    : INTEGER
    | DECIMAL
    | MINUS INTEGER
    | MINUS DECIMAL
    ;

// ============================================================================
// LEXER RULES
// ============================================================================

// ----------------------------------------------------------------------------
// Keywords - Structure
// ----------------------------------------------------------------------------

DECISION_TABLE : 'decision_table' ;
RULE           : 'rule' ;
END            : 'end' ;
GIVEN          : 'given' ;
DECIDE         : 'decide' ;
RETURN         : 'return' ;
EXECUTE        : 'execute' ;

// ----------------------------------------------------------------------------
// Keywords - Hit Policies
// ----------------------------------------------------------------------------

HIT_POLICY   : 'hit_policy' ;
FIRST_MATCH  : 'first_match' ;
SINGLE_HIT   : 'single_hit' ;
MULTI_HIT    : 'multi_hit' ;
COLLECT_ALL  : 'collect_all' ;

// ----------------------------------------------------------------------------
// Keywords - Control Flow
// ----------------------------------------------------------------------------

IF     : 'if' ;
THEN   : 'then' ;
ELSEIF : 'elseif' ;
ELSE   : 'else' ;
ENDIF  : 'endif' ;
SET    : 'set' ;
LET    : 'let' ;
WHEN   : 'when' ;
OTHERWISE : 'otherwise' ;
POST_CALCULATE : 'post_calculate' ;
AGGREGATE : 'aggregate' ;

// ----------------------------------------------------------------------------
// Keywords - Logic
// ----------------------------------------------------------------------------

AND : 'and' ;
OR  : 'or' ;
NOT : 'not' ;

// ----------------------------------------------------------------------------
// Keywords - Conditions
// ----------------------------------------------------------------------------

IN           : 'in' ;
IS           : 'is' ;
NULL         : 'null' ;
IS_NULL      : 'is_null' ;
IS_NOT_NULL  : 'is_not_null' ;
MATCHES      : 'matches' ;
CONTAINS     : 'contains' ;
STARTS_WITH  : 'starts_with' ;
ENDS_WITH    : 'ends_with' ;

// ----------------------------------------------------------------------------
// Keywords - Actions
// ----------------------------------------------------------------------------

LOOKUP  : 'lookup' ;
EMIT    : 'emit' ;
TO      : 'to' ;
DEFAULT : 'default' ;
AS_OF   : 'as_of' ;

// ----------------------------------------------------------------------------
// Keywords - Services
// ----------------------------------------------------------------------------

SERVICES : 'services' ;
SYNC     : 'sync' ;
ASYNC    : 'async' ;
CACHED   : 'cached' ;
TIMEOUT  : 'timeout' ;
FALLBACK : 'fallback' ;
RETRY    : 'retry' ;

// ----------------------------------------------------------------------------
// Keywords - Actions
// ----------------------------------------------------------------------------

ACTIONS  : 'actions' ;
STATE    : 'state' ;
AUDIT    : 'audit' ;
CALL     : 'call' ;

// ----------------------------------------------------------------------------
// Keywords - Collection Functions (RFC: Collection Operations)
// ----------------------------------------------------------------------------

ANY      : 'any' ;
ALL      : 'all' ;
NONE     : 'none' ;
SUM      : 'sum' ;
COUNT    : 'count' ;
AVG      : 'avg' ;
MAX_FN   : 'max' ;
MIN_FN   : 'min' ;
FILTER   : 'filter' ;
FIND     : 'find' ;
DISTINCT : 'distinct' ;

// ----------------------------------------------------------------------------
// Duration Units
// ----------------------------------------------------------------------------

MS : 'ms' ;
S  : 's' ;
M  : 'm' ;
H  : 'h' ;

// ----------------------------------------------------------------------------
// Keywords - Types
// ----------------------------------------------------------------------------

TEXT_TYPE       : 'text' ;
NUMBER_TYPE     : 'number' ;
BOOLEAN_TYPE    : 'boolean' ;
DATE_TYPE       : 'date' ;
TIMESTAMP_TYPE  : 'timestamp' ;
MONEY_TYPE      : 'money' ;
PERCENTAGE_TYPE : 'percentage' ;
BIZDATE_TYPE    : 'bizdate' ;  // v0.6.0+: Business date type

// ----------------------------------------------------------------------------
// Keywords - Markers (v0.6.0+)
// ----------------------------------------------------------------------------

MARKER          : 'marker' ;
FIRED           : 'fired' ;
PENDING         : 'pending' ;
BETWEEN_MARKERS : 'between' ;

// ----------------------------------------------------------------------------
// Keywords - Other
// ----------------------------------------------------------------------------

DESCRIPTION : 'description' ;
PRIORITY    : 'priority' ;
VERSION     : 'version' ;
YES         : 'yes' ;
MULTI       : 'multi' ;

// ----------------------------------------------------------------------------
// Operators - Comparison
// ----------------------------------------------------------------------------

EQ : '==' | '=' ;
NE : '!=' ;
LT : '<' ;
GT : '>' ;
LE : '<=' ;
GE : '>=' ;

// ----------------------------------------------------------------------------
// Operators - Arithmetic
// ----------------------------------------------------------------------------

PLUS    : '+' ;
MINUS   : '-' ;
STAR    : '*' ;
SLASH   : '/' ;
PERCENT : '%' ;
MOD     : 'mod' ;
ARROW   : '->' ;

// ----------------------------------------------------------------------------
// Punctuation
// ----------------------------------------------------------------------------

PIPE     : '|' ;
COLON    : ':' ;
COMMA    : ',' ;
DOT      : '.' ;
LPAREN   : '(' ;
RPAREN   : ')' ;
LBRACKET : '[' ;
RBRACKET : ']' ;
LBRACE   : '{' ;
RBRACE   : '}' ;

// ----------------------------------------------------------------------------
// Special Tokens
// ----------------------------------------------------------------------------

// Table separator: minimum 3 equals signs (===+)
SEP : '=' '=' '=' '='* ;

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

BOOLEAN
    : 'true' | 'false' | 'yes' | 'no'
    ;

// Version number like 1.0.0 or 2.1.3 (must come before INTEGER/DECIMAL)
VERSION_NUMBER
    : [0-9]+ '.' [0-9]+ '.' [0-9]+
    ;

INTEGER
    : [0-9]+
    ;

DECIMAL
    : [0-9]+ '.' [0-9]+
    ;

MONEY_LITERAL
    : '$' [0-9]+ (',' [0-9][0-9][0-9])* ('.' [0-9][0-9])?
    ;

PERCENTAGE_LITERAL
    : [0-9]+ ('.' [0-9]+)? '%'
    ;

// Double-quoted strings: for attribute names with special chars, rule names
DQUOTED_STRING
    : '"' (~["\r\n])* '"'
    ;

// Single-quoted strings: for string literals/constants
SQUOTED_STRING
    : '\'' (~['\r\n])* '\''
    ;

// Generic string (backward compat)
STRING
    : DQUOTED_STRING
    | SQUOTED_STRING
    ;

IDENTIFIER
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// ----------------------------------------------------------------------------
// Comments and Whitespace
// ----------------------------------------------------------------------------

LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;

// Inline comments captured for documentation (not skipped)
LINE_COMMENT_INLINE
    : '//' ~[\r\n]*
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
