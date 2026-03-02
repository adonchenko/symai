grammar BehaviorsGrammar;
// SymAI behaviors grammar parser
// java -jar ./bin/antlr-4.13.1-complete.jar antlr4/BehaviorsGrammar.g4 -Dlanguage=Python3 -encoding UTF8 -package BehaviorsGrammar -o BehaviorsGrammar

primaryExpression
    : Identifier
    | Constant
    | '(' expression ')'
    ;

postfixExpression
    : primaryExpression
     ('(' argumentExpressionList? ')'
       | '.' Identifier)*
    ;

argumentExpressionList
    : assignmentExpression (',' assignmentExpression)*
    ;

unaryExpression
    : unaryOperator? postfixExpression
    ;

unaryOperator
    : '+'
    | '-'
    | '!'
    ;

multiplicativeExpression
    : unaryExpression (('*' | '/' | '%'|'**') unaryExpression)*
    ;

additiveExpression
    : multiplicativeExpression (('+' | '-') multiplicativeExpression)*
    ;

relationalExpression
    : additiveExpression (('<' | '>' | '<=' | '>=') additiveExpression)*
    ;

equalityExpression
    : relationalExpression (('==' | '!=') relationalExpression)*
    ;

logicalAndExpression
    : equalityExpression ('&&' equalityExpression)*
    ;

logicalOrExpression
    : logicalAndExpression ('||' logicalAndExpression)*
    ;

assignmentExpression
    : logicalOrExpression
    | unaryExpression assignmentOperator assignmentExpression
    ;

assignmentOperator
    : '='
    ;

expression
    : assignmentExpression (',' assignmentExpression)*
    ;

assignmentExpressionList
    : assignmentExpression (';' assignmentExpression)*
    ;

actions
    : (postfixExpression ':' logicalOrExpression '->' (assignmentExpressionList)? ',')+
    ;

behaviors
    : system_of_eqs
    ;

system_of_eqs
    :  (eqs ',')+
    ;

eqs
    : prim_name '=' items_list
    ;

prim_name
    : '!'? Identifier ('(' argumentExpressionList? ')')?
    ;

comp_name
    : prim_name
    | '(' postfix_item ')'
    ;

postfix_item
    :  comp_name
       ( ('.' | '+') comp_name)*
    ;

items_list
    : postfix_item (';' postfix_item )*
    ;

par_item
    : items_list ('||' items_list)?
    ;

Equal
    : '=='
    ;

NotEqual
    : '!='
    ;

LeftParen
    : '('
    ;

RightParen
    : ')'
    ;

Less
    : '<'
    ;

LessEqual
    : '<='
    ;

Greater
    : '>'
    ;

GreaterEqual
    : '>='
    ;

Plus
    : '+'
    ;

Minus
    : '-'
    ;

Star
    : '*'
    ;

Div
    : '/'
    ;

Mod
    : '%'
    ;

Pow
    : '**'
    ;

AndAnd
    : '&&'
    ;

Colon
    : ':'
    ;

Semicolon
    : ';'
    ;

OrOr
    : '||'
    ;

Not
    : '!'
    ;

Comma
    : ','
    ;

Assign
    : '='
    ;

Dot
    : '.'
    ;

Identifier
    : IdentifierNondigit (IdentifierNondigit | Digit)*
    ;

fragment IdentifierNondigit
    : Nondigit
    // |   // other implementation-defined characters...
    ;

fragment Nondigit
    : [a-zA-Z_]
    ;

fragment Digit
    : [0-9]
    ;

fragment HexQuad
    : HexadecimalDigit HexadecimalDigit HexadecimalDigit HexadecimalDigit
    ;

Constant
    : IntegerConstant
    | FloatingConstant
    ;

fragment IntegerConstant
    : DecimalConstant IntegerSuffix?
    | OctalConstant IntegerSuffix?
    | HexadecimalConstant IntegerSuffix?
    | BinaryConstant
    ;


fragment BinaryConstant
    : '0' [bB] [0-1]+
    ;

fragment DecimalConstant
    : NonzeroDigit Digit*
    ;

fragment OctalConstant
    : '0' OctalDigit*
    ;

fragment HexadecimalConstant
    : HexadecimalPrefix HexadecimalDigit+
    ;

fragment HexadecimalPrefix
    : '0' [xX]
    ;

fragment NonzeroDigit
    : [1-9]
    ;

fragment OctalDigit
    : [0-7]
    ;

fragment HexadecimalDigit
    : [0-9a-fA-F]
    ;

fragment IntegerSuffix
    : UnsignedSuffix LongSuffix?
    | UnsignedSuffix LongLongSuffix
    | LongSuffix UnsignedSuffix?
    | LongLongSuffix UnsignedSuffix?
    ;

fragment UnsignedSuffix
    : [uU]
    ;

fragment LongSuffix
    : [lL]
    ;

fragment LongLongSuffix
    : 'll'
    | 'LL'
    ;

fragment FloatingConstant
    : DecimalFloatingConstant
    | HexadecimalFloatingConstant
    ;

fragment DecimalFloatingConstant
    : FractionalConstant ExponentPart? FloatingSuffix?
    | DigitSequence ExponentPart FloatingSuffix?
    ;

fragment HexadecimalFloatingConstant
    : HexadecimalPrefix (HexadecimalFractionalConstant | HexadecimalDigitSequence) BinaryExponentPart FloatingSuffix?
    ;

fragment FractionalConstant
    : DigitSequence? '.' DigitSequence
    | DigitSequence '.'
    ;

fragment ExponentPart
    : [eE] Sign? DigitSequence
    ;

fragment Sign
    : [+-]
    ;

DigitSequence
    : Digit+
    ;

fragment HexadecimalFractionalConstant
    : HexadecimalDigitSequence? '.' HexadecimalDigitSequence
    | HexadecimalDigitSequence '.'
    ;

fragment BinaryExponentPart
    : [pP] Sign? DigitSequence
    ;

fragment HexadecimalDigitSequence
    : HexadecimalDigit+
    ;

fragment FloatingSuffix
    : [flFL]
    ;

fragment SChar
    : ~["\\\r\n]
    | '\\\n'   // Added line
    | '\\\r\n' // Added line
    ;

// ignore the following asm blocks:
Whitespace
    : [ \t]+ -> channel(HIDDEN)
    ;

Newline
    : ('\r' '\n'? | '\n') -> channel(HIDDEN)
    ;

