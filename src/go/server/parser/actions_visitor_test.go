package parser

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

type (
	ActionsVisitorTestData struct {
		source      string
		result      string
		n_actions   int
		has_logical []NameBooleanTestPair
	}
)

func initActionTestInputData() []ActionsVisitorTestData {
	testData := make([]ActionsVisitorTestData, 0)
	testData = append(testData,
		ActionsVisitorTestData{
			source:      "a2:a<b->c=0,a1: True-> ,",
			result:      "a2:a<b->c=0,a1:0<1->,",
			n_actions:   2,
			has_logical: make([]NameBooleanTestPair, 0),
		})
	testData[0].has_logical = append(testData[0].has_logical, NameBooleanTestPair{"a2", false})
	testData[0].has_logical = append(testData[0].has_logical, NameBooleanTestPair{"a1", false})

	testData = append(testData,
		ActionsVisitorTestData{
			source:      "a1: True-> ,a2:a<b->c=0,",
			result:      "a1:0<1->,a2:a<b->c=0,",
			n_actions:   2,
			has_logical: make([]NameBooleanTestPair, 0),
		})
	testData[1].has_logical = append(testData[1].has_logical, NameBooleanTestPair{"a2", false})
	testData[1].has_logical = append(testData[1].has_logical, NameBooleanTestPair{"a1", false})

	testData = append(testData,
		ActionsVisitorTestData{
			source:      "a1: True-> ,",
			result:      "a1:0<1->,",
			n_actions:   1,
			has_logical: make([]NameBooleanTestPair, 0),
		})
	testData[2].has_logical = append(testData[2].has_logical, NameBooleanTestPair{"a1", false})

	testData = append(testData,
		ActionsVisitorTestData{
			source:      "a(1): a > b -> c = a + b, a(2): a < b -> c = b - a, a(3): a == b -> a = c - b, a(4): 1 -> a = b + c,",
			result:      "a(1):a>b->c=a+b,a(2):a<b->c=b-a,a(3):a==b->a=c-b,a(4):0<1->a=b+c,",
			n_actions:   4,
			has_logical: make([]NameBooleanTestPair, 0),
		})
	testData[3].has_logical = append(testData[3].has_logical, NameBooleanTestPair{"a(1)", false})
	testData[3].has_logical = append(testData[3].has_logical, NameBooleanTestPair{"a(2)", false})
	testData[3].has_logical = append(testData[3].has_logical, NameBooleanTestPair{"a(3)", false})
	testData[3].has_logical = append(testData[3].has_logical, NameBooleanTestPair{"a(4)", false})

	testData = append(testData,
		ActionsVisitorTestData{
			source:      "a(1): a > b -> c = a + b; a == b, a(2): a < b -> c = b - a, a(3): a == b -> a = c - b, a(4): 1 -> a = b + c,",
			result:      "a(1):a>b->c=a+b;a==b,a(2):a<b->c=b-a,a(3):a==b->a=c-b,a(4):0<1->a=b+c,",
			n_actions:   4,
			has_logical: make([]NameBooleanTestPair, 0),
		})
	testData[4].has_logical = append(testData[4].has_logical, NameBooleanTestPair{"a(1)", true})
	testData[4].has_logical = append(testData[4].has_logical, NameBooleanTestPair{"a(2)", false})
	testData[4].has_logical = append(testData[4].has_logical, NameBooleanTestPair{"a(3)", false})
	testData[4].has_logical = append(testData[4].has_logical, NameBooleanTestPair{"a(4)", false})
	
	testData = append(testData,
		ActionsVisitorTestData{
			source:      "a1: 1-> 1,",
			result:      "a1:0<1->1,",
			n_actions:   1,
			has_logical: make([]NameBooleanTestPair, 0),
		})
	testData[5].has_logical = append(testData[5].has_logical, NameBooleanTestPair{"a1", false})	

	return testData
}

func TestActionsVisitor(t *testing.T) {

	testData := initActionTestInputData()

	for _, d := range testData {
		p, listener := initParser(d.source)

		tree := p.Actions()

		// Create and run the visitor
		visitor := NewActionsVisitor()

		result := tree.Accept(visitor)

		assert.Equal(t, listener.HasError(), false, "There should be no errors in listener")
		assert.Equal(t, visitor.HasError(), false, "There should be no errors in visitor")

		assert.Equal(t, d.n_actions, len(visitor.GetActions()), "Incorrect actions number")
		assert.Equal(t, d.result, result.(string))
		acts := visitor.GetActions()
		for _, p := range d.has_logical {
			a, err := acts[p.name]
			if !err {
				assert.Fail(t, "Action '"+p.name+"' is not present")
			}
			assert.Equal(t, p.flag, len(a.Logical) > 0, "Flag is not equal to expected")
		}
	}
}
