package parser

import (
	"testing"
	
	"github.com/stretchr/testify/assert"
)

type (
	EvalVisitorTestData struct {
		source    string
		result    interface{}
		is_error  bool
	}
)

func initEvalVisitorTestInputData() []EvalVisitorTestData {
	testData := make([]EvalVisitorTestData, 0)
	testData = append(testData,
		EvalVisitorTestData{
			source:    "(1+3)*2",
			result:    float64(8),
			is_error:  false,
		})
	testData = append(testData,
		EvalVisitorTestData{
			source:    "1+3*2/0",
			result:    float64(7),
			is_error:  true,
		})
	testData = append(testData,
		EvalVisitorTestData{
			source:    "3**2 - pow(3,2)",
			result:    float64(0),
			is_error:  false,
		})	
	return testData
}

 func TestEvalVisitor(t *testing.T) {

testData := initEvalVisitorTestInputData()

	for _, d := range testData {
		p, listener := initParser(d.source)

		tree := p.Expression()
		visitor := NewEvalVisitor()
		result := tree.Accept(visitor)
        
		if d.is_error {
			assert.Equal(t, true, listener.HasError() || visitor.HasError(), "There should be errors in listener or visitor")
		} else {
			assert.Equal(t, false, listener.HasError(), "There should be no errors in listener")
			assert.Equal(t, false, visitor.HasError(), "There should be no errors in visitor")
			assert.Equal(t, d.result, result, "The result should be the same as expected")
		}
	}
}
