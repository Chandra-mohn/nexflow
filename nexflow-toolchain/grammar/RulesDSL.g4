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
    : (decisionTableDef | proceduralRuleDef)+ EOF
    ;

// ----------------------------------------------------------------------------
// Decision Table Definition
// ----------------------------------------------------------------------------

decisionTableDef
    : DECISION_TABLE tableName
        hitPolicyDecl?
        descriptionDecl?
        givenBlock
        decideBlock
        (returnSpec | executeSpec | hybridSpec)?
      END
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
    : IDENTIFIER PIPE
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

// ----------------------------------------------------------------------------
// Procedural Rule Definition (Enhanced from rules-dsl)
// ----------------------------------------------------------------------------

proceduralRuleDef
    : RULE ruleName COLON
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
    | actionSequence
    | returnStatement
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
    : factor ((STAR | SLASH | PERCENT) factor)*
    ;

factor
    : MINUS? atom
    ;

atom
    : literal
    | fieldPath
    | functionCall
    | listLiteral
    | LPAREN valueExpr RPAREN
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
    : LBRACKET (literal (COMMA literal)*)? RBRACKET
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

// ----------------------------------------------------------------------------
// Keywords - Control Flow
// ----------------------------------------------------------------------------

IF     : 'if' ;
THEN   : 'then' ;
ELSEIF : 'elseif' ;
ELSE   : 'else' ;
ENDIF  : 'endif' ;

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
// Keywords - Types
// ----------------------------------------------------------------------------

TEXT_TYPE       : 'text' ;
NUMBER_TYPE     : 'number' ;
BOOLEAN_TYPE    : 'boolean' ;
DATE_TYPE       : 'date' ;
TIMESTAMP_TYPE  : 'timestamp' ;
MONEY_TYPE      : 'money' ;
PERCENTAGE_TYPE : 'percentage' ;

// ----------------------------------------------------------------------------
// Keywords - Other
// ----------------------------------------------------------------------------

DESCRIPTION : 'description' ;
PRIORITY    : 'priority' ;
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
