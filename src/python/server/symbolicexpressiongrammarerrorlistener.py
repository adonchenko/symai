from antlr4.error.ErrorListener import *

class SymbolicExpressionGrammarErrorListener( ErrorListener ):

    def __init__(self):
        super(SymbolicExpressionGrammarErrorListener, self).__init__()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception(f"Syntax error appeared on symbol '{offendingSymbol}' on line {line} column  {column} {msg}")

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        raise Exception("Ambiguity error appeared during parsing")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        raise Exception("Error appeared during parsing")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        raise Exception("Error appeared during parsing")
