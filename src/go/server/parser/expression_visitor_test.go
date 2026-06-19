package parser

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

type (
	ExpressionVisitorTestData struct {
		source    string
		result    string
		has_trig  bool
		has_nl    bool
		n_vars    int
		subst_map map[string]string
		vars_list []string
	}
)

func initExpressionTestInputData() []ExpressionVisitorTestData {
	testData := make([]ExpressionVisitorTestData, 0)
	testData = append(testData,
		ExpressionVisitorTestData{
			source:    "a < b",
			result:    "a<b",
			has_trig:  false,
			has_nl:    false,
			n_vars:    2,
			subst_map: make(map[string]string, 0),
			vars_list: make([]string, 0),
		})
	testData[0].vars_list = append(testData[0].vars_list, "a")
	testData[0].vars_list = append(testData[0].vars_list, "b")

	testData = append(testData,
		ExpressionVisitorTestData{
			source:    "a < b(0) && (c<=d)",
			result:    "a<b(0)&&(c<=d)",
			has_trig:  false,
			has_nl:    false,
			n_vars:    4,
			subst_map: make(map[string]string, 0),
			vars_list: make([]string, 0),
		})
	testData[1].vars_list = append(testData[1].vars_list, "a")
	testData[1].vars_list = append(testData[1].vars_list, "b(0)")
	testData[1].vars_list = append(testData[1].vars_list, "c")
	testData[1].vars_list = append(testData[1].vars_list, "d")

	return testData
}

func TestExpressionVisitor(t *testing.T) {

	testData := initExpressionTestInputData()

	for _, d := range testData {
		p, listener := InitParser(d.source)

		tree := p.Expression()

		// Create and run the visitor
		visitor := NewEQExtractorVisitor(false)
		visitor.SetSubstitutionMap(d.subst_map)

		result := tree.Accept(visitor)

		assert.Equal(t, listener.HasError(), false, "There should be no errors in listener")

		assert.Equal(t, d.n_vars, len(visitor.GetVarList()), "Incorrect number of variables")
		assert.Equal(t, d.result, result.(string))
		vars := visitor.GetVarList()
		for _, v := range d.vars_list {
			b := false
			for _, vl := range vars {
				if vl == v {
					b = true
					break
				}
			}
			if !b {
				assert.Fail(t, "Variable '"+v+"' is absent in the result")
			}

		}
	}
}
