package parser
import (
	"src/server/BehaviorsGrammar"

	"github.com/antlr4-go/antlr/v4"
)

type (
	NameBooleanTestPair struct {
		name string
		flag bool
	}

	NameTerminalsTestPair struct {
		name string
		terminals []string
	}
)

func NewNameTerminalsTestPair() *NameTerminalsTestPair {
	return &NameTerminalsTestPair {
		name: "",
		terminals: make([]string, 0),
	}
}

func initParser(inputStr string) (*BehaviorsGrammar.BehaviorsGrammarParser, *SymAIErrorListener) {
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

	return p, &listener
}
