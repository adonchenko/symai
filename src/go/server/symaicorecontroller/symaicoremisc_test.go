package symaicorecontroller

import (
	"github.com/stretchr/testify/assert"
	"os"
    "testing"

	"src/server/config"
)

type (

	DoSolverTestData struct {
		source      string
		result      string
		response    string
		ctx_key     string
		ctx_result  SolverProcessingContext
		is_error    bool
		check_ini   bool
		ini_value   string
	}
)

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

func InitDoSolverData(clnt *Client) []DoSolverTestData {
	testData := make([]DoSolverTestData, 0)
	testData = append(testData, DoSolverTestData{
		source:  "",
		result:  "Z3",
		ctx_key: "solver",
		ctx_result: SolverProcessingContext{
						Solver: "Z3",
					},
        response: "Z3",
		is_error: false,
		check_ini: false,
		ini_value: "Z3",		
	})
	testData = append(testData, DoSolverTestData{
		source:  "flush",
		result:  "",
		ctx_key: "solver",
		ctx_result: SolverProcessingContext{
						Solver: "Z3",
					},
        response: "Z3",
		is_error: false,
		check_ini: true,
		ini_value: "Z3",		
	})
	testData = append(testData, DoSolverTestData{
		source:  "SymPy",
		result:  "SymPy",
		ctx_key: "solver",
		ctx_result: SolverProcessingContext{
						Solver: "SymPy",
					},
        response: "SymPy",
		is_error: false,
		check_ini: false,
		ini_value: "SymPy",		
	})
	testData = append(testData, DoSolverTestData{
		source:  "SymPy flush",
		result:  "SymPy",
		ctx_key: "solver",
		ctx_result: SolverProcessingContext{
						Solver: "SymPy",
					},
        response: "SymPy",
		is_error: false,
		check_ini: true,
		ini_value: "SymPy",		
	})
	return testData
}

func TestDoSolver(t *testing.T) {
 	var (
 		cfg *config.SymAIConfig 
 	)
 	defer func() {
 		os.Remove("./symai.ini")
 		if r := recover(); r != nil {
 			assert.Fail(t, "panic occurred in TestDoSolver: %v", r)
		}
	}()
	clnt := InitTestConfig(t)
	testData := InitDoSolverData(clnt)

 	cnf.GetLogger().Info("TestDoSolver started")

	for _, d := range testData {
		ReinitClientTest(clnt)
		res, err := doSolver(clnt, d.source)
		if d.is_error && err == nil {
			assert.NotNil(t, err, "expected error for solver command")
		} else {			
			assert.Equal(t, res, d.result, "unexpected response for solver command")
			assert.Equal(t, clnt.getSolverCtx(), d.ctx_result, "unexpected solver context value")
			if d.check_ini {
				cfg, err = config.Load("./symai.ini")
				assert.Nil(t, err, "error loading config: %v", err)
				assert.Equal(t, cfg.ExpressionSection.ExpressionSolver, d.ini_value, "unexpected value in config after flush")
			}
		}
	}
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