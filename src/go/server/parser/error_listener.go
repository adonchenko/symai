package parser

import (
	"fmt"

	"github.com/antlr4-go/antlr/v4"
)

// SymAIErrorListener collects syntax errors
type SymAIErrorListener struct {
	ErrorProcessing
}

// SyntaxError is called by the parser when a syntax error occurs
func (l *SymAIErrorListener) SyntaxError(recognizer antlr.Recognizer, offendingSymbol interface{}, line, column int, msg string, e antlr.RecognitionException) {
	errorMsg := fmt.Sprintf("line %d:%d %s", line, column, msg)
	l.addError(errorMsg)
}

// Other required methods to implement (can be empty or use BaseErrorListener)
func (l *SymAIErrorListener) ReportAmbiguity(antlr.Parser, *antlr.DFA, int, int, bool, *antlr.BitSet, *antlr.ATNConfigSet) {
	// Optional: implement if needed
	l.addError("ReportAmbiguity error")
}

func (l *SymAIErrorListener) ReportAttemptingFullContext(antlr.Parser, *antlr.DFA, int, int, *antlr.BitSet, *antlr.ATNConfigSet) {
	// Optional: implement if needed
	l.addError("AttemptingFullContext error")
}

func (l *SymAIErrorListener) ReportContextSensitivity(antlr.Parser, *antlr.DFA, int, int, int, *antlr.ATNConfigSet) {
	// Optional: implement if needed
	l.addError("ReportContextSensitivity error")
}
