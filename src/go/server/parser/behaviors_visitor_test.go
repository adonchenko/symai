package parser

import (
	"testing"

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
	ts := make([]string, 0)
	ts = append(ts, "a(1)")
	ts = append(ts, ".")
	ts = append(ts, "B(1)")
	ts = append(ts, "+")
	ts = append(ts, "a(2)")
	ts = append(ts, ".")
	ts = append(ts, "B(2)")
	ts = append(ts, "+")
	ts = append(ts, "a(5)")
	ts = append(ts, ".")
	ts = append(ts, "B(3)")
	tt := NameTerminalsTestPair{
		name:      "B(0)",
		terminals: ts,
	}
	testData[0].test_data = append(testData[0].test_data, tt)
	// B(1)=a(3).B(1)
	ts = make([]string, 0)
	ts = append(ts, "a(3)")
	ts = append(ts, ".")
	ts = append(ts, "B(1)")
	tt = NameTerminalsTestPair{
		name:      "B(1)",
		terminals: ts,
	}
	testData[0].test_data = append(testData[0].test_data, tt)
	// B(2)=a(4)
	ts = make([]string, 0)
	ts = append(ts, "a(4)")
	tt = NameTerminalsTestPair{
		name:      "B(2)",
		terminals: ts,
	}
	testData[0].test_data = append(testData[0].test_data, tt)
	// B(3)=a(6).B(3)+a(7)
	ts = make([]string, 0)
	ts = append(ts, "a(6)")
	ts = append(ts, ".")
	ts = append(ts, "B(3)")
	ts = append(ts, "+")
	ts = append(ts, "a(7)")
	tt = NameTerminalsTestPair{
		name:      "B(3)",
		terminals: ts,
	}
	testData[0].test_data = append(testData[0].test_data, tt)

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
		for _, p := range d.test_data {
			td, ok := behs[p.name]
			assert.Equal(t, true, ok, "No behaviors '"+p.name+"' in the result")
			assert.Equal(t, len(p.terminals), len(td.Terminals), "Behavior '"+p.name+"'.Number of processed terminals is not equal to the expected")
			b := true
			for i := 0; i < len(td.Terminals) && b; i++ {
				b = (td.Terminals[i] == p.terminals[i])
			}
			assert.NotEqual(t, false, b, "Expected and processed terminals sequences are not equal")
		}
	}
}
