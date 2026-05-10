package symaicorecontroller

import (
	"encoding/json"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/assert"

	"src/server/parser"
)

type (
	DoActionsTestData struct {
		source     string
		result     string
		ctx_key    string
		ctx_result ActionsProcessingContext
		response   string
		is_error   bool
	}
)

func InitDoActionsData(clnt *Client) []DoActionsTestData {
	testData := make([]DoActionsTestData, 0)

	testData = append(testData, DoActionsTestData{
		source:  "{\"content\":\"a2:a<b->c=0,a1: True-> (c<d),\",\"filename\":\"actions.act\"}",
		result:  "a2:a<b->c=0,a1:0<1->(c<d),",
		ctx_key: "actions",
		ctx_result: ActionsProcessingContext{
			FileBaseData: FileBaseData{
				Filename: "actions.act",
				Content:  "a2:a<b->c=0,a1:0<1->(c<d),",
				Filepath: filepath.Join(clnt.getBaseTempDir(), "actions.act"),
			},
			actions: make(map[string]parser.ActionBody),
		},
		response: "{\"content\":\"a2:a<b->c=0,a1:0<1->(c<d),\", \"filename\":\"actions.act\"}",
		is_error: false,
	})
	testData[len(testData)-1].ctx_result.actions["a1"] = parser.ActionBody{
		Logical:   "(c<d)",
		Condition: "0<1",
		Actions:   make([]string, 0),
	}
	testData[len(testData)-1].ctx_result.actions["a2"] = parser.ActionBody{
		Logical:   "",
		Condition: "a<b",
		Actions:   make([]string, 1),
	}
	testData[len(testData)-1].ctx_result.actions["a2"].Actions[0] = "c=0"

	testData = append(testData, DoActionsTestData{
		source:  "{\"content\":\"a2:a<b->c=0,a1: True-> ,\",\"filename\":\"actions.act\"}",
		result:  "a2:a<b->c=0,a1:0<1->,",
		ctx_key: "actions",
		ctx_result: ActionsProcessingContext{
			FileBaseData: FileBaseData{
				Filename: "actions.act",
				Content:  "a2:a<b->c=0,a1:0<1->,",
				Filepath: filepath.Join(clnt.getBaseTempDir(), "actions.act"),
			},
			actions: make(map[string]parser.ActionBody),
		},
		response: "{\"content\":\"a2:a<b->c=0,a1:0<1->,\", \"filename\":\"actions.act\"}",
		is_error: false,
	})
	testData[len(testData)-1].ctx_result.actions["a1"] = parser.ActionBody{
		Logical:   "",
		Condition: "0<1",
		Actions:   make([]string, 0),
	}
	testData[len(testData)-1].ctx_result.actions["a2"] = parser.ActionBody{
		Logical:   "",
		Condition: "a<b",
		Actions:   make([]string, 1),
	}
	testData[len(testData)-1].ctx_result.actions["a2"].Actions[0] = "c=0"
	return testData
}

func TestDoActions(t *testing.T) {
	var (
		r1, r2 JsonFile
	)
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestDoActions started")
	testData := InitDoActionsData(clnt)

	for _, d := range testData {
		ReinitClientTest(clnt)
		res, err := doActions(clnt, d.source)
		if d.is_error {
			assert.NotNil(t, err, "expected error for actions command")
		} else {
			assert.Equal(t, res, d.result, "unexpected response for actions command")
			res, err = doActions(clnt, "")
			assert.Nil(t, err, "error actions command with empty source")
			err = json.Unmarshal([]byte(res), &r1)
			assert.Nil(t, err, "canot unmarshal response for actions command with empty source: %v", err)

			err = json.Unmarshal([]byte(d.response), &r2)
			assert.Nil(t, err, "canot unmarshal expected response for actions command with empty source: %v", err)
			assert.True(t, r1.Content == r2.Content && r1.Filename == r2.Filename, "unexpected response for actions command with empty source. Content and/or Filename fields do not match expected values")
			t1, ok := clnt.ctx[d.ctx_key]
			assert.True(t, ok, "actions context key not found in client context")
			assert.IsType(t, ActionsProcessingContext{}, t1, "unexpected type for actions context value")
			a := clnt.ctx[d.ctx_key].(ActionsProcessingContext)
			assert.True(t, a.IsEqual(d.ctx_result), "unexpected actions context value")
		}
	}
}
