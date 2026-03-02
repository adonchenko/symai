package parser

import (
	//	"src/server/BehaviorsGrammar"
	"testing"

	//	"github.com/antlr4-go/antlr/v4"

	"github.com/stretchr/testify/assert"
)

type (
	BehaviorsVisitorTestData struct {
		source    string
		result    string
		n_terms   int
		test_data []NameTerminalsTestPair
	}
)

func initBehaviorsTestInputData() []BehaviorsVisitorTestData {
	testData := make([]BehaviorsVisitorTestData, 0)
	testData = append(testData,
		BehaviorsVisitorTestData{
			source:    "B(0) = a(1).B(1) +a(2).B(2)  +a(5).B(3),\nB(1) = a(3).B(1),\nB(2) = a(4),\nB(3) = a(6).B(3) +a(7),",
			result:    "B(0)=a(1).B(1)+a(2).B(2)+a(5).B(3),B(1)=a(3).B(1),B(2)=a(4),B(3)=a(6).B(3)+a(7),",
			n_terms:   4,
			test_data: make([]NameTerminalsTestPair, 0),
		})
	tt := NameTerminalsTestPair{
		name:      "B(0)",
		terminals: make([]string, 0),
	}
	testData[0].test_data = append(testData[0].test_data, tt)
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "a(1)")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, ".")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "B(1)")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "+")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "a(2)")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, ".")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "B(2)")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "+")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "a(5)")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, ".")
	testData[0].test_data[0].terminals = append(testData[0].test_data[0].terminals, "B(3)")

	return testData
}

func TestBehaviorsVisitor(t *testing.T) {

	testData := initBehaviorsTestInputData()

	for _, d := range testData {
		p, listener := initParser(d.source)

		tree := p.Behaviors()

		// Create and run the visitor
		visitor := NewBehaviorsVisitor()

		result := tree.Accept(visitor)

		assert.Equal(t, listener.hasError(), false, "There should be no errors in listener")
		assert.Equal(t, visitor.hasError(), false, "There should be no errors in visitor")

		behs := visitor.GetBehaviors()
		assert.Equal(t, d.n_terms, len(behs), "Incorrect terminals sequences number")
		assert.Equal(t, d.result, result.(string))

	}
}
