package symaicorecontroller

import (
	"encoding/json"	
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
    "path/filepath"	
	"testing"

	"src/server/config"
)

type (
	DoEnvironmentTestData struct {
		source     string
		result     string
		ctx_key    string
		ctx_result EnvironmentProcessingContext
		response   string
		is_error   bool
	}
)

func InitTestConfig(t *testing.T) *Client {
	var (
		lgr config.LoggerConfigStruct = config.LoggerConfigStruct{}
	)
	config.Config.InitDefaults()

	lgr.Handlers = "consoleHandler"
	lgr.Level = "DEBUG"
	lgr.Qualname = "test"
	lgr.Propagate = 0
	config.Config.LoggersFromComfig["test"] = lgr
	config.Config.LoggersSection.Keys = config.Config.LoggersSection.Keys + ",test"
	err := config.InitLogger("test")
	assert.Nil(t, err, "error initializing logger: %v", err)
	cnf = &config.Config

	clnt := &Client{
		ctx: make(map[string]interface{}),
		// Context fields:
		// Possible context fields (to be extended as needed):
		// "symaiconfig" a SymAISection value @config for details
		// "environment" a FileBaseData value
		// "properties" a PropertyProcessingContext value
		// "actions" an ActionsProcessingContext value
		// "behaviors" a BehaviorsProcessingContext value
		conn: nil,
		UUID: uuid.New(),
		send: make(chan []byte),
	}

	return clnt
}

func ReinitClientTest(clnt *Client) {
	clnt.ctx = make(map[string]interface{})
	clnt.send = make(chan []byte)	
}

func InitDoEnvironmentData(clnt *Client) []DoEnvironmentTestData {
	testData := make([]DoEnvironmentTestData, 0)
	testData = append(testData, DoEnvironmentTestData{
		source:  "{\"content\":\"v==d\"}",
		result:  "v==d",
		ctx_key: "environment",
		ctx_result: EnvironmentProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "environment.env",
							Content:  "v==d",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "environment.env"),
						},
					},
        response: "{\"content\":\"v==d\", \"filename\":\"environment.env\"}",
		is_error: false,
	})
	testData = append(testData, DoEnvironmentTestData{
		source:  "{\"content\":\"v==d\",\"filename\":\"ttt.ggg\"}",
		result:  "v==d",
		ctx_key: "environment",
		ctx_result: EnvironmentProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "ttt.ggg",
							Content:  "v==d",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "environment.env"),
						},
					},
		response: "{\"content\":\"v==d\", \"filename\":\"ttt.ggg\"}",			
		is_error: false,
	})
	testData = append(testData, DoEnvironmentTestData{
		source:  "",
		result:  "{\"filename\":\"environment.env\",\"content\":\"\"}",
		ctx_key: "environment",
		ctx_result: EnvironmentProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "environment.env",
							Content:  "",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "environment.env"),
						},
					},
		response: "{\"content\":\"\", \"filename\":\"environment.env\"}",			
		is_error: false,
	})
	testData = append(testData, DoEnvironmentTestData{
		source:  ",,v==d",
		result:  "",
		ctx_key: "environment",
		ctx_result: EnvironmentProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "environment.env",
							Content:  "",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "environment.env"),
						},
					},
	//	response: "{\"content\":\"v==d\", "filename\":\"environment.env\"}",			
		is_error: true,
	})
	return testData
}

func TestDoEnvironment(t *testing.T) {
	var (
		r1, r2 JsonFile		
	)
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestDoEnvironment started")
	testData := InitDoEnvironmentData(clnt)

	for _, d := range testData {
		ReinitClientTest(clnt)
		res, err := doEnvironment(clnt, d.source)
		if d.is_error {
			assert.NotNil(t, err, "expected error for environment command")
		} else {			
			assert.Equal(t, res, d.result, "unexpected response for environment command")
			assert.Equal(t, clnt.ctx[d.ctx_key].(EnvironmentProcessingContext), d.ctx_result, "unexpected environment context value")
			res, err = doEnvironment(clnt, "")
			assert.Nil(t, err, "error processing environment command with empty source")

			err = json.Unmarshal([]byte(res), &r1)
			assert.Nil(t, err, "canot unmarshal response for environment command with empty source: %v", err)
			err = json.Unmarshal([]byte(d.response), &r2)
			assert.Nil(t, err, "canot unmarshal expected response for environment command with empty source: %v", err)	
			assert.True(t, r1.Content == r2.Content && r1.Filename == r2.Filename, "unexpected response for environment command with empty source. Content and/or Filename fields do not match expected values")
		}
	}
}
