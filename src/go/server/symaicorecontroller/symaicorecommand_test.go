package symaicorecontroller

import (
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

func InitDoEnvironmentData(clnt *Client) []DoEnvironmentTestData {
	testData := make([]DoEnvironmentTestData, 0)
	testData = append(testData, DoEnvironmentTestData{
		source:   "{\"content\":\"v==d\"}",
		result:   "v==d",
		ctx_key: "environment",
		ctx_result: EnvironmentProcessingContext{
		FileBaseData: FileBaseData{
			Filename: "environment.env",
			Content:  "v==d",
			Filepath: filepath.Join(clnt.getBaseTempDir(), "environment.env"),
		}},
		is_error: false,	
	})
	testData = append(testData, DoEnvironmentTestData{
		source:   "{\"content\":\"v==d\",\"filename\":\"ttt.ggg\"}",
		result:   "v==d",
		ctx_key: "environment",
		ctx_result: EnvironmentProcessingContext{
		FileBaseData: FileBaseData{
			Filename: "ttt.ggg",
			Content:  "v==d",
			Filepath: filepath.Join(clnt.getBaseTempDir(), "environment.env"),
		}},
		is_error: false,	
	})
	return testData	
}


func TestDoEnvironment(t *testing.T) {
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestDoEnvironment started")
	testData := InitDoEnvironmentData(clnt)
    
	for _, d := range testData {
		res, err := doEnvironment(clnt, d.source)
		if d.is_error {
			assert.NotNil(t, err, "expected error for environment command")
		} else {
			assert.Nil(t, err, "error executing environment command: %v", err)
			assert.Equal(t, res, d.result, "unexpected response for environment command")
			assert.Equal(t, clnt.ctx[d.ctx_key].(EnvironmentProcessingContext), d.ctx_result,   "unexpected environment context value")
		}	
	}
}
