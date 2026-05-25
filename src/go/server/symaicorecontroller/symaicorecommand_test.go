package symaicorecontroller

import (
	"encoding/json"	
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"os"
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

	DoPropertyTestData struct {
		source     string
		result     string
		ctx_key    string
		ctx_result PropertyProcessingContext
		response   string
		is_error   bool
	}
)

func InitTestConfig(t *testing.T) *Client {
	var (
		lgr config.LoggerConfigStruct = config.LoggerConfigStruct{}
	)
	config.Config.InitDefaults()
	config.Config.SetPath("./symai.ini")

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
		response: "{\"content\":\"v==d\", \"filename\":\"environment.env\"}",			
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

func InitDoPropertyData(clnt *Client) []DoPropertyTestData {
	testData := make([]DoPropertyTestData, 0)
	testData = append(testData, DoPropertyTestData{
		source:  "{\"content\":\"v==d\"}",
		result:  "v==d",
		ctx_key: "property",
		ctx_result: PropertyProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "property.prop",
							Content:  "v==d",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "property.prop"),
						},
					},
        response: "{\"content\":\"v==d\", \"filename\":\"property.prop\"}",
		is_error: false,
	})
	testData = append(testData, DoPropertyTestData{
		source:  "{\"content\":\"v==d\",\"filename\":\"ttt.ggg\"}",
		result:  "v==d",
		ctx_key: "property",
		ctx_result: PropertyProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "ttt.ggg",
							Content:  "v==d",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "property.prop"),
						},
					},
		response: "{\"content\":\"v==d\", \"filename\":\"ttt.ggg\"}",			
		is_error: false,
	})
	testData = append(testData, DoPropertyTestData{
		source:  "",
		result:  "{\"filename\":\"property.prop\",\"content\":\"\"}",
		ctx_key: "property",
		ctx_result: PropertyProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "property.prop",
							Content:  "",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "property.prop"),
						},
					},
		response: "{\"content\":\"\", \"filename\":\"property.prop\"}",			
		is_error: false,
	})
	testData = append(testData, DoPropertyTestData{
		source:  ",,v==d",
		result:  "",
		ctx_key: "property",
		ctx_result: PropertyProcessingContext{
						FileBaseData: FileBaseData{
							Filename: "property.prop",
							Content:  "",
							Filepath: filepath.Join(clnt.getBaseTempDir(), "property.prop"),
						},
					},
		response: "{\"content\":\"v==d\", \"filename\":\"property.prop\"}",			
		is_error: true,
	})
	return testData
}

func TestDoProperty(t *testing.T) {
	var (
		r1, r2 JsonFile		
	)
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestDoProperty started")
	testData := InitDoPropertyData(clnt)

	for _, d := range testData {
		ReinitClientTest(clnt)
		res, err := doProperty(clnt, d.source)
		if d.is_error {
			assert.NotNil(t, err, "expected error for property command")
		} else {			
			assert.Equal(t, res, d.result, "unexpected response for property command")
			assert.Equal(t, clnt.ctx[d.ctx_key].(PropertyProcessingContext), d.ctx_result, "unexpected property context value")
			res, err = doProperty(clnt, "")
			assert.Nil(t, err, "error processing property command with empty source")

			err = json.Unmarshal([]byte(res), &r1)
			assert.Nil(t, err, "canot unmarshal response for property command with empty source: %v", err)
			err = json.Unmarshal([]byte(d.response), &r2)
			assert.Nil(t, err, "canot unmarshal expected response for property command with empty source: %v", err)	
			assert.True(t, r1.Content == r2.Content && r1.Filename == r2.Filename, "unexpected response for property command with empty source. Content and/or Filename fields do not match expected values")
		}
	}
}

func TestSolverCtx(t *testing.T) {
	var (
		cfg *config.SymAIConfig 
		err error
	)
	defer func() {
		os.Remove("./symai.ini")
		if r := recover(); r != nil {
			assert.Fail(t, "panic occurred in TestSolverCtx: %v", r)
		}
	}()
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestSolverCtx started")
	sctx := clnt.getSolverCtx()
	assert.NotNil(t, sctx, "solver context should not be nil")
	sctx.SetSolver("test_solver")
	assert.Equal(t, sctx.GetSolver(), "test_solver", "unexpected solver name in context")
    clnt.setSolverCtx(sctx)
	err = clnt.flushSolverCtx()
	assert.Nil(t, err, "error flushing solver: %v", err)
    cfg, err = config.Load("./symai.ini")
	assert.Nil(t, err, "error loading config: %v", err)
	assert.Equal(t, cfg.ExpressionSection.ExpressionSolver, "test_solver", "unexpected solver name in config after flush")
}

func TestAICtx(t *testing.T) {
	var (
		cfg *config.SymAIConfig 
		err error
	)
	defer func() {
		os.Remove("./symai.ini")
		if r := recover(); r != nil {
			assert.Fail(t, "panic occurred in TestAICtx: %v", r)
		}
	}()
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestAICtx started")
	ictx := clnt.getAICtx()
	assert.NotNil(t, ictx, "AI context should not be nil")
	ictx.SetAI(true)
	assert.Equal(t, ictx.GetAI(), true, "unexpected AI value in context")
    clnt.setAICtx(ictx)
	err = clnt.flushAICtx()
	assert.Nil(t, err, "error flushing AI context: %v", err)
    cfg, err = config.Load("./symai.ini")
	assert.Nil(t, err, "error loading config: %v", err)
	assert.Equal(t, cfg.SymAISection.AI, "true", "unexpected AI value in config after flush")
}

func TestDebugCtx(t *testing.T) {
	var (
		cfg *config.SymAIConfig 
		err error
	)
	defer func() {
		os.Remove("./symai.ini")
		if r := recover(); r != nil {
			assert.Fail(t, "panic occurred in TestDebugCtx: %v", r)
		}
	}()
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestDebugCtx started")
	ictx := clnt.getDebugCtx()
	assert.NotNil(t, ictx, "Debug context should not be nil")
	ictx.SetDebug(true)
	assert.Equal(t, ictx.GetDebug(), true, "unexpected debug value in context")
    clnt.setDebugCtx(ictx)
	err = clnt.flushDebugCtx()
	assert.Nil(t, err, "error flushing Debug context: %v", err)
    cfg, err = config.Load("./symai.ini")
	assert.Nil(t, err, "error loading config: %v", err)
	assert.Equal(t, cfg.SymAISection.Debug, "true", "unexpected debug value in config after flush")
}

func TestReenterCountCtx(t *testing.T) {
	var (
		cfg *config.SymAIConfig 
		err error
	)
	defer func() {
		os.Remove("./symai.ini")
		if r := recover(); r != nil {
			assert.Fail(t, "panic occurred in TestReenterCountCtx: %v", r)
		}
	}()
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestReenterCountCtx started")
	ictx := clnt.getReenterCountCtx()
	assert.NotNil(t, ictx, "ReenterCount context should not be nil")
	ictx.SetReenterCount(5)
	assert.Equal(t, ictx.GetReenterCount(), 5, "unexpected reenter count value in context")
    clnt.setReenterCountCtx(ictx)
	err = clnt.flushReenterCountCtx()
	assert.Nil(t, err, "error flushing ReenterCount context: %v", err)
    cfg, err = config.Load("./symai.ini")
	assert.Nil(t, err, "error loading config: %v", err)
	assert.Equal(t, cfg.SymAISection.ReenterCount, 5, "unexpected reenter count value in config after flush")
}

func TestMaxModelsCtx(t *testing.T) {
	var (
		cfg *config.SymAIConfig 
		err error
	)
	defer func() {
		os.Remove("./symai.ini")
		if r := recover(); r != nil {
			assert.Fail(t, "panic occurred in TestMaxModelsCtx: %v", r)
		}
	}()
	clnt := InitTestConfig(t)
	cnf.GetLogger().Info("TestMaxModelsCtx started")
	ictx := clnt.getMaxModelsCtx()
	assert.NotNil(t, ictx, "MaxModels context should not be nil")
	ictx.SetMaxModels(5)
	assert.Equal(t, ictx.GetMaxModels(), 5, "unexpected max models value in context")
    clnt.setMaxModelsCtx(ictx)
	err = clnt.flushMaxModelsCtx()
	assert.Nil(t, err, "error flushing MaxModels context: %v", err)
    cfg, err = config.Load("./symai.ini")
	assert.Nil(t, err, "error loading config: %v", err)
	assert.Equal(t, cfg.ExpressionSection.SolverMaxModels, 5, "unexpected max models value in config after flush")
}