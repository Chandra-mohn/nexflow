/**
 * RulesDSL - Business Rules Domain-Specific Language
 *
 * ANTLR4 Grammar for L4 Business Rules DSL
 *
 * Version: 1.0.0
 * Specification: ../L4-Business-Rules.md
 *
 * This grammar defines the syntax for business rules including:
 * - Decision Tables: Matrix-based logic for multi-condition scenarios
 * - Procedural Rules: If-then-else chains for sequential logic
 * - Hit Policies: first_match, single_hit, multi_hit
 * - Condition Types: equals, range, in_set, pattern, null_check
 * - Action Types: assign, calculate, lookup, call, emit
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
    : (decisionTableDef | proceduralRuleDef)+ EOF
    ;

// ----------------------------------------------------------------------------
// Decision Table Definition
// ----------------------------------------------------------------------------

decisionTableDef
    : 'decision_table' tableName
        hitPolicyDecl?
        descriptionDecl?
        givenBlock
        decideBlock
        (returnSpec | executeSpec | hybridSpec)?
      'end'
    ;

tableName
    : IDENTIFIER
    ;

hitPolicyDecl
    : 'hit_policy' hitPolicyType
    ;

hitPolicyType
    : 'first_match'                           // Default: stop at first match
    | 'single_hit'                            // Exactly one must match
    | 'multi_hit'                             // Execute all matching
    ;

descriptionDecl
    : 'description' STRING
    ;

// ----------------------------------------------------------------------------
// Given Block (Input Parameters)
// ----------------------------------------------------------------------------

givenBlock
    : 'given' ':' inputParam+ 'end'?
    ;

inputParam
    : '-' paramName ':' paramType
    ;

paramName
    : IDENTIFIER
    ;

paramType
    : baseType
    | 'money'
    | 'percentage'
    | IDENTIFIER                              // Custom type reference
    ;

baseType
    : 'text'
    | 'number'
    | 'boolean'
    | 'date'
    | 'timestamp'
    ;

// ----------------------------------------------------------------------------
// Decide Block (Decision Matrix)
// ----------------------------------------------------------------------------

decideBlock
    : 'decide' ':' tableMatrix
    ;

tableMatrix
    : tableHeader tableSeparator tableRow+
    ;

tableHeader
    : '|' priorityHeader? conditionHeader+ actionHeader+ '|'
    ;

priorityHeader
    : 'priority' '|'
    ;

conditionHeader
    : IDENTIFIER '|'
    ;

actionHeader
    : IDENTIFIER '|'
    ;

tableSeparator
    : '|' SEP+ '|'
    ;

tableRow
    : '|' priorityCell? conditionCell+ actionCell+ '|'
    ;

priorityCell
    : INTEGER '|'
    ;

conditionCell
    : condition '|'
    ;

actionCell
    : action '|'
    ;

// ----------------------------------------------------------------------------
// Condition Types
// ----------------------------------------------------------------------------

condition
    : WILDCARD                                // * (any)
    | exactMatch                              // Exact value
    | rangeCondition                          // 700-799, >= 700, < 0.3
    | setCondition                            // IN (a, b, c), NOT IN
    | patternCondition                        // matches "regex"
    | nullCondition                           // is null, is not null
    | comparisonCondition                     // > 1000, >= 700, != "closed"
    | expressionCondition                     // Complex boolean expression
    ;

exactMatch
    : literal
    ;

rangeCondition
    : numberLiteral '-' numberLiteral         // 700-799 (inclusive range)
    | MONEY_LITERAL '-' MONEY_LITERAL         // $100-$500
    ;

setCondition
    : 'IN' '(' valueList ')'
    | 'NOT' 'IN' '(' valueList ')'
    ;

patternCondition
    : 'matches' STRING
    | 'ends_with' STRING
    | 'starts_with' STRING
    | 'contains' STRING
    ;

nullCondition
    : 'is' 'null'
    | 'is' 'not' 'null'
    ;

comparisonCondition
    : comparisonOp valueExpr
    ;

expressionCondition
    : '(' booleanExpr ')'
    ;

booleanExpr
    : booleanTerm (('AND' | 'OR') booleanTerm)*
    ;

booleanTerm
    : 'NOT'? (comparisonExpr | '(' booleanExpr ')' | functionCall)
    ;

comparisonExpr
    : valueExpr comparisonOp valueExpr
    | valueExpr 'IN' '(' valueList ')'
    | valueExpr 'NOT' 'IN' '(' valueList ')'
    | valueExpr 'is' 'null'
    | valueExpr 'is' 'not' 'null'
    ;

comparisonOp
    : '=' | '!=' | '<' | '>' | '<=' | '>='
    ;

// ----------------------------------------------------------------------------
// Action Types
// ----------------------------------------------------------------------------

action
    : WILDCARD                                // - (no action)
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
    : 'lookup' '(' IDENTIFIER (',' valueExpr)* (',' 'default' ':' valueExpr)? ')'
    | 'lookup' '(' IDENTIFIER ',' 'as_of' ':' valueExpr ')'
    ;

callAction
    : IDENTIFIER '(' (actionArg (',' actionArg)*)? ')'
    ;

actionArg
    : valueExpr
    | IDENTIFIER ':' valueExpr                // Named argument
    ;

emitAction
    : 'emit' 'to' IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Return/Execute Specifications
// ----------------------------------------------------------------------------

returnSpec
    : 'return' ':' returnParam+
    ;

returnParam
    : '-' paramName ':' paramType
    ;

executeSpec
    : 'execute' ':' executeType
    ;

executeType
    : 'yes'                                   // Execute all action columns
    | 'multi'                                 // Multi-hit execution
    | IDENTIFIER                              // Execute specific column
    ;

hybridSpec
    : returnSpec executeSpec
    ;

// ----------------------------------------------------------------------------
// Procedural Rule Definition
// ----------------------------------------------------------------------------

proceduralRuleDef
    : 'rule' ruleName ':'
        ruleStatement+
      'end'
    ;

ruleName
    : IDENTIFIER
    ;

ruleStatement
    : 'if' booleanExpr 'then' actionName
    ;

actionName
    : IDENTIFIER
    ;

// ----------------------------------------------------------------------------
// Expression Language
// ----------------------------------------------------------------------------

valueExpr
    : literal
    | fieldPath
    | functionCall
    | valueExpr arithmeticOp valueExpr
    | '(' valueExpr ')'
    ;

arithmeticExpr
    : valueExpr (arithmeticOp valueExpr)*
    ;

arithmeticOp
    : '+' | '-' | '*' | '/' | '%'
    ;

functionCall
    : IDENTIFIER '(' (valueExpr (',' valueExpr)*)? ')'
    ;

fieldPath
    : IDENTIFIER ('.' IDENTIFIER)*
    | IDENTIFIER '[' INTEGER ']' ('.' IDENTIFIER)*
    ;

valueList
    : valueExpr (',' valueExpr)*
    ;

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

literal
    : STRING
    | numberLiteral
    | MONEY_LITERAL
    | PERCENTAGE_LITERAL
    | BOOLEAN
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
// Keywords
// ----------------------------------------------------------------------------

// Structure: decision_table, rule, end, given, decide, return, execute
// Hit policies: hit_policy, first_match, single_hit, multi_hit
// Condition keywords: IN, NOT, matches, ends_with, starts_with, contains, is, null
// Logic: AND, OR, if, then
// Actions: lookup, emit, to, default, as_of
// Types: text, number, boolean, date, timestamp, money, percentage
// Other: description, priority

// ----------------------------------------------------------------------------
// Operators and Symbols
// ----------------------------------------------------------------------------

// ARROW token removed - decision tables use positional columns
// Condition columns declared in 'conditions' block, remaining columns are actions

WILDCARD
    : '*'
    | '-'                                     // Used in action columns
    ;

SEP
    : '-'+
    ;

// ----------------------------------------------------------------------------
// Literals
// ----------------------------------------------------------------------------

INTEGER
    : [0-9]+
    ;

DECIMAL
    : [0-9]+ '.' [0-9]+
    ;

MONEY_LITERAL
    : '$' [0-9]+ (',' [0-9]{3})* ('.' [0-9]{2})?
    ;

PERCENTAGE_LITERAL
    : [0-9]+ ('.' [0-9]+)? '%'
    ;

BOOLEAN
    : 'true' | 'false' | 'yes' | 'no'
    ;

IDENTIFIER
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

STRING
    : '"' (~["\r\n])* '"'
    ;

// ----------------------------------------------------------------------------
// Comparison Operators
// ----------------------------------------------------------------------------

EQ : '=' ;
NE : '!=' ;
LT : '<' ;
GT : '>' ;
LE : '<=' ;
GE : '>=' ;

// ----------------------------------------------------------------------------
// Arithmetic Operators
// ----------------------------------------------------------------------------

PLUS : '+' ;
MINUS : '-' ;
STAR : '*' ;
SLASH : '/' ;
PERCENT : '%' ;

// ----------------------------------------------------------------------------
// Punctuation
// ----------------------------------------------------------------------------

PIPE : '|' ;
COLON : ':' ;
COMMA : ',' ;
DOT : '.' ;
LPAREN : '(' ;
RPAREN : ')' ;
LBRACKET : '[' ;
RBRACKET : ']' ;

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
