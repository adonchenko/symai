package symaicorecontroller

import (
	"encoding/json"	
	"github.com/stretchr/testify/assert"
    "path/filepath"	
	"testing"

	"src/server/parser"
)

type (
	DoBehaviorsTestData struct {
		source     string
		result     string
		ctx_key    string
		ctx_result BehaviorsProcessingContext
		response   string
		is_error   bool
	}
)

func InitDoBehaviorsData(clnt *Client) []DoBehaviorsTestData {
	testData := make([]DoBehaviorsTestData, 0)

	testData = append(testData, DoBehaviorsTestData{
		source:      "{\"content\":\"B1 = a1.a(2) + B2,\",\"filename\":\"behaviors.act\"}",
		result:      "B1=a1.a(2)+B2,",
		ctx_key: "behaviors",
		ctx_result: BehaviorsProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "behaviors.act",
							Content:  "B1=a1.a(2)+B2,",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "behaviors.act"),
						},
						behaviors: make(map[string]parser.BehaviorBody),
					},
        response: "{\"content\":\"B1=a1.a(2)+B2,\", \"filename\":\"behaviors.act\"}",
		is_error: false,
	})
	testData[len(testData) - 1].ctx_result.behaviors["B1"] = parser.BehaviorBody{
		Terminals: make([]string, 5),
	}
	testData[len(testData) - 1].ctx_result.behaviors["B1"].Terminals[0] = "a1"
	testData[len(testData) - 1].ctx_result.behaviors["B1"].Terminals[1] = "."
	testData[len(testData) - 1].ctx_result.behaviors["B1"].Terminals[2] = "a(2)"
	testData[len(testData) - 1].ctx_result.behaviors["B1"].Terminals[3] = "+"
	testData[len(testData) - 1].ctx_result.behaviors["B1"].Terminals[4] = "B2"

	return testData
}

func TestDoBehaviors(t *testing.T) {
	var (
		r1, r2 JsonFile		
	)
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestDoBehaviors started")
	testData := InitDoBehaviorsData(clnt)

	for _, d := range testData {
		ReinitClientTest(clnt)
		res, err := doBehaviors(clnt, d.source)
		if d.is_error {
			assert.NotNil(t, err, "expected error for behaviors command")
		} else {			
			assert.Equal(t, res, d.result, "unexpected response for behaviors command")
			res, err = doBehaviors(clnt, "")			
			assert.Nil(t, err, "error behaviors command with empty source")
			err = json.Unmarshal([]byte(res), &r1)			
			assert.Nil(t, err, "canot unmarshal response for behaviors command with empty source: %v", err)

			err = json.Unmarshal([]byte(d.response), &r2)
			assert.Nil(t, err, "canot unmarshal expected response for behaviors command with empty source: %v", err)	
			assert.True(t, r1.Content == r2.Content && r1.Filename == r2.Filename, "unexpected response for Behaviors command with empty source. Content and/or Filename fields do not match expected values")
			t1, ok :=  clnt.ctx[d.ctx_key]
			assert.True(t, ok, "behaviors context key not found in client context")
			assert.IsType(t, BehaviorsProcessingContext{}, t1, "unexpected type for behaviors context value")
			a := clnt.ctx[d.ctx_key].(BehaviorsProcessingContext)
			assert.True(t, a.IsEqual(d.ctx_result), "unexpected behaviors context value")			
		}
	}
}
