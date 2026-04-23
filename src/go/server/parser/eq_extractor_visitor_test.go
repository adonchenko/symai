package parser

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

type (
	EQExtractorVisitorTestData struct {
		source    string
		result    string
		extract   bool
		cvals     map[string]float64
		vals	  map[string]string
		vars 	  []string
	}
)

func initEQExtractorTestInputData() []EQExtractorVisitorTestData {
	testData := make([]EQExtractorVisitorTestData, 0)
	testData = append(testData,
		EQExtractorVisitorTestData{
			source:    "a==56!=c==d+3==q&&e==f",
			result:    "56!=c",
			extract:   true,
			cvals:     make(map[string]float64),
			vals:      make(map[string]string),	
			vars:      []string{},
		})
	testData[0].cvals["a"] = 56.0
    testData[0].vals["c"] = "d+3"
	testData[0].vals["q"] =	"d+3"
	testData[0].vals["e"] = "f"
	
	testData = append(testData,
		EQExtractorVisitorTestData{
			source:    "a==56!=c==d+3==q&&e==f",
			result:    "a==56&&d+3==q&&e==f",
			extract:   false,
			cvals:     make(map[string]float64),
			vals:      make(map[string]string),	
			vars:      []string{"c"},
		})
	
	testData = append(testData,
		EQExtractorVisitorTestData{
			source:    "a==56!=c==d+3==q&&e==f||g>=h<p",
			result:    "a==56&&d+3==q&&e==f||h<p",
			extract:   false,
			cvals:     make(map[string]float64),
			vals:      make(map[string]string),	
			vars:      []string{"c", "g"},
		})	
		
	return testData
}

func TestEQExtractorVisitor(t *testing.T) {

	testData := initEQExtractorTestInputData()

	for _, d := range testData {
		p, listener := initParser(d.source)

		tree := p.Expression()

		visitor := NewEQExtractorVisitor(d.extract, d.vars)

		result := tree.Accept(visitor)
		assert.Equal(t, d.result, result.(string), "The result should be the same as expected")

		assert.Equal(t, false, listener.HasError(), "There should be no errors in listener")

		if d.extract {
			assert.Equal(t, len(d.cvals), len(visitor.GetCvals()), "The number of extracted concrete values should match")
			assert.Equal(t, len(d.vals), len(visitor.GetVals()), "The number of extracted symbolic values should match")
		} else {
			assert.Equal(t, 0, len(visitor.GetCvals()), "There should be no concrete values extracted")
			assert.Equal(t, 0, len(visitor.GetVals()), "There should be no values extracted")
		}
	}
}
