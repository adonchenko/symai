package parser

import (
	"fmt"
	//	"os"
	"testing"

	"src/server/BehaviorsGrammar"

	"github.com/antlr4-go/antlr/v4"
	"github.com/stretchr/testify/assert"
)

func TestExpressionVisitor(t *testing.T) {
	inputStr := "a2:a<b->c=0,a1: True-> ,"

	listener := SymAIErrorListener{}
	input := antlr.NewInputStream(inputStr)
	lexer := BehaviorsGrammar.NewBehaviorsGrammarLexer(input)
	stream := antlr.NewCommonTokenStream(lexer, 0)
	p := BehaviorsGrammar.NewBehaviorsGrammarParser(stream)
	p.BuildParseTrees = true
	lexer.RemoveErrorListeners()
	p.RemoveErrorListeners()
	lexer.AddErrorListener(&listener)
	p.AddErrorListener(&listener)

	tree := p.Actions() // Start rule "AssignmentExpressionList" --- IGNORE ---

	// Create and run the visitor
	visitor := NewActionsVisitor()
	result := tree.Accept(visitor)

	fmt.Printf("Expression: %sResult: %s\n", inputStr, result.(string))
	assert.Equal(t, listener.hasError(), false, "There should be no errors")
}
