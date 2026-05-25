package symaicorecontroller

import (
	"encoding/json"
	"errors"
	"strconv"
	"strings"
	"syscall"

	"src/server/config"
	"src/server/parser"
)

type (
	SymAICoreCommandProcessing func(c *Client, params string) (string, error)

	SymAICoreCommand struct {
		exec  SymAICoreCommandProcessing
		help  string
		descr string
	}
)

var (
	allCoreCommands map[string]SymAICoreCommand = make(map[string]SymAICoreCommand, 0)
	cnf             *config.SymAIConfig         = nil
)

func doEnvironment(c *Client, params string) (string, error) {

	var (
		res       = ""
		err error = nil
		fd        = FileData{}
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " environment " + params + " command received")
	if len(params) <= 0 {
		fs := JsonFile{
			Filename: c.getEnvCtx().Filename,
			Content:  c.getEnvCtx().Content,
		}

		r := make([]byte, 0)
		r, err = json.Marshal(fs)
		res = string(r)
	} else {
		fd, err = processFile(params)
		if err == nil {
			p, l := InitParser(fd.Content)
			tree := p.Expression()
			if len(l.GetErrorList()) > 0 {
				errMsg := ""
				for _, e := range l.GetErrorList() {
					if len(errMsg) > 0 {
						errMsg = errMsg + "\n"
					}
					errMsg = errMsg + e
				}
				err = errors.New(errMsg)
			} else {
				visitor := parser.NewEQExtractorVisitor()

				r := tree.Accept(visitor)
				if r == nil || len(visitor.GetErrorList()) > 0 {
					errMsg := ""
					for _, e := range visitor.GetErrorList() {
						if len(errMsg) > 0 {
							errMsg = errMsg + "\n"
						}
						errMsg = errMsg + e
					}
					if len(errMsg) <= 0 {
						errMsg = "environment parsing error"
					}
					err = errors.New(errMsg)
				} else {
					fn := strings.TrimSpace(fd.Filename)
					if len(fn) <= 0 {
						fn = "environment.env"
					}
					c.setEnvFilename(fn)
					res = r.(string)
					c.setEnvContent(res)
					//err = c.saveEnvContent() // Will be uncommented, if we'll need to keep environment permanently
				}
			}
		}
	}

	return res, err
}

func doShutdown(c *Client, params string) (string, error) {
	if cnf == nil {
		config.GetConfig().GetLogger().Error("cnf is nil")
		return "", errors.New("cnf is nil")
	}
	cnf.GetLogger().Info("client " + c.UUID.String() + " shutdown command received")

	stopChan <- syscall.SIGQUIT
	// TODO: stop expression and frontend services here as well!!!

	return "", nil
}

func doStop(c *Client, params string) (string, error) {
	if cnf == nil {
		config.GetConfig().GetLogger().Error("cnf is nil")
		return "", errors.New("cnf is nil")
	}
	cnf.GetLogger().Info("client " + c.UUID.String() + " stop command received")
	hub.unregister <- c
	return "", nil
}

func doProperty(c *Client, params string) (string, error) {

	var (
		res       = ""
		err error = nil
		fd        = FileData{}
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " property " + params + " command received")

	if len(params) <= 0 {
		fs := JsonFile{
			Filename: c.getPropCtx().Filename,
			Content:  c.getPropCtx().Content,
		}

		r := make([]byte, 0)
		r, err = json.Marshal(fs)
		res = string(r)
	} else {
		fd, err = processFile(params)
		if err == nil {
			p, l := InitParser(fd.Content)
			tree := p.Expression()
			if len(l.GetErrorList()) > 0 {
				errMsg := ""
				for _, e := range l.GetErrorList() {
					if len(errMsg) > 0 {
						errMsg = errMsg + "\n"
					}
					errMsg = errMsg + e
				}
				err = errors.New(errMsg)
			} else {
				visitor := parser.NewEQExtractorVisitor()

				r := tree.Accept(visitor)
				if r == nil || len(visitor.GetErrorList()) > 0 {
					errMsg := ""
					for _, e := range visitor.GetErrorList() {
						if len(errMsg) > 0 {
							errMsg = errMsg + "\n"
						}
						errMsg = errMsg + e
					}
					if len(errMsg) <= 0 {
						errMsg = "property parsing error"
					}
					err = errors.New(errMsg)
				} else {
					fn := strings.TrimSpace(fd.Filename)
					if len(fn) <= 0 {
						fn = "property.prop"
					}
					c.setPropFilename(fn)
					res = r.(string)
					c.setPropContent(res)
					//err = c.savePropContent() // Will be uncommented, if we'll need to keep property permanently
				}
			}
		}
	}

	return res, err
}

func doActions(c *Client, params string) (string, error) {

	var (
		res       = ""
		err error = nil
		fd        = FileData{}
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " actions " + params + " command received")

	if len(params) <= 0 {
		fs := JsonFile{
			Filename: c.getActionsCtx().Filename,
			Content:  c.getActionsCtx().Content,
		}

		r := make([]byte, 0)
		r, err = json.Marshal(fs)
		res = string(r)
	} else {
		fd, err = processFile(params)
		if err == nil {
			p, l := InitParser(fd.Content)
			tree := p.Actions()
			if len(l.GetErrorList()) > 0 {
				errMsg := ""
				for _, e := range l.GetErrorList() {
					if len(errMsg) > 0 {
						errMsg = errMsg + "\n"
					}
					errMsg = errMsg + e
				}
				err = errors.New(errMsg)
			} else {
				visitor := parser.NewActionsVisitor()

				r := tree.Accept(visitor)
				if r == nil || len(visitor.GetErrorList()) > 0 {
					errMsg := ""
					for _, e := range visitor.GetErrorList() {
						if len(errMsg) > 0 {
							errMsg = errMsg + "\n"
						}
						errMsg = errMsg + e
					}
					if len(errMsg) <= 0 {
						errMsg = "actions parsing error"
					}
					err = errors.New(errMsg)
				} else {
					c.setActions(visitor.GetActions())
					fn := strings.TrimSpace(fd.Filename)
					if len(fn) <= 0 {
						fn = "actions.act"
					}
					c.setActionsFilename(fn)
					s := strings.TrimSpace(r.(string))
					res = s

					c.setActionsContent(s)
					//err = c.saveActionsContent() // Will be uncommented, if we'll need to keep actions permanently
				}
			}
		}
	}

	return res, err
}

func doBehaviors(c *Client, params string) (string, error) {
	var (
		res       = ""
		err error = nil
		fd        = FileData{}
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " behaviors " + params + " command received")

	if len(params) <= 0 {
		fs := JsonFile{
			Filename: c.getBehaviorsCtx().Filename,
			Content:  c.getBehaviorsCtx().Content,
		}

		r := make([]byte, 0)
		r, err = json.Marshal(fs)
		res = string(r)
	} else {
		fd, err = processFile(params)
		if err == nil {
			p, l := InitParser(fd.Content)
			tree := p.Behaviors()
			if len(l.GetErrorList()) > 0 {
				errMsg := ""
				for _, e := range l.GetErrorList() {
					if len(errMsg) > 0 {
						errMsg = errMsg + "\n"
					}
					errMsg = errMsg + e
				}
				err = errors.New(errMsg)
			} else {
				visitor := parser.NewBehaviorsVisitor()

				r := tree.Accept(visitor)
				if r == nil || len(visitor.GetErrorList()) > 0 {
					errMsg := ""
					for _, e := range visitor.GetErrorList() {
						if len(errMsg) > 0 {
							errMsg = errMsg + "\n"
						}
						errMsg = errMsg + e
					}
					if len(errMsg) <= 0 {
						errMsg = "behaviors parsing error"
					}
					err = errors.New(errMsg)
				} else {
					c.setAllBehaviors(visitor.GetBehaviors())
					fn := strings.TrimSpace(fd.Filename)
					if len(fn) <= 0 {
						fn = "behaviors.beh"
					}
					c.setBehaviorsFilename(fn)
					s := strings.TrimSpace(r.(string))
					res = s

					c.setBehaviorsContent(s)
					//err = c.saveBehaviorsContent() // Will be uncommented, if we'll need to keep behaviors permanently
				}
			}
		}
	}

	return res, err
}

func doSolver(c *Client, params string) (string, error) {
	var (
		res            = ""
		err     error  = nil
		isFlush bool   = false
		val     string = ""
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " solver " + params + " command received")
	sctx := c.getSolverCtx()
	params = strings.TrimSpace(params)
	if len(params) <= 0 {
		res = sctx.GetSolver()
	} else {
		flds := strings.Fields(params)
		if len(flds) > 2 {
			err = errors.New("solver command syntax error: too many parameters")
		} else {
			for _, f := range flds {
				if strings.EqualFold(f, "flush") {
					if isFlush {
						err = errors.New("solver command syntax error: 'flush' parameter is duplicated")
						break
					}
					isFlush = true
				} else {
					if len(val) > 0 {
						err = errors.New("solver command syntax error: too many parameters")
						break
					}
					val = f
				}
			}
			if err == nil {
				if len(val) > 0 {
					sctx.SetSolver(val)
					c.setSolverCtx(sctx)
					cnf.GetLogger().Info("client " + c.UUID.String() + "solver set to '" + val + "' successfully")
				}
				if isFlush {
					err = c.flushSolverCtx()
					if err != nil {
						err = errors.New("error flushing solver context: " + err.Error())
						cnf.GetLogger().Error("client " + c.UUID.String() + " error flushing solver context: " + err.Error())
					} else {
						cnf.GetLogger().Info("client " + c.UUID.String() + "solver context flushed successfully")
					}
				}
			}
		}
	}

	return res, err
}

func doAI(c *Client, params string) (string, error) {
	var (
		res            = ""
		err     error  = nil
		isFlush bool   = false
		val     string = ""
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " ai " + params + " command received")
	sctx := c.getAICtx()
	params = strings.TrimSpace(params)
	if len(params) <= 0 {
		res = strconv.FormatBool(sctx.GetAI())
	} else {
		flds := strings.Fields(params)
		if len(flds) > 2 {
			err = errors.New("ai command syntax error: too many parameters")
		} else {
			for _, f := range flds {
				if strings.EqualFold(f, "flush") {
					if isFlush {
						err = errors.New("ai command syntax error: 'flush' parameter is duplicated")
						break
					}
					isFlush = true
				} else {
					if len(val) > 0 {
						err = errors.New("ai command syntax error: too many parameters")
						break
					}
					val = f
				}
			}
			if err == nil {
				if len(val) > 0 {
					aiVal, parseErr := strconv.ParseBool(val)
					if parseErr != nil {
						err = errors.New("ai command syntax error: invalid boolean value '" + val + "'")
						aiVal = false
						cnf.GetLogger().Error("client " + c.UUID.String() + " ai command syntax error: invalid boolean value '" + val + "'")
					} else {
						sctx.SetAI(aiVal)
						c.setAICtx(sctx)
						cnf.GetLogger().Info("client " + c.UUID.String() + "ai set to '" + val + "' successfully")
					}
				}
				if isFlush {
					err = c.flushAICtx()
					if err != nil {
						err = errors.New("error flushing ai context: " + err.Error())
						cnf.GetLogger().Error("client " + c.UUID.String() + " error flushing ai context: " + err.Error())
					} else {
						cnf.GetLogger().Info("client " + c.UUID.String() + "ai context flushed successfully")
					}
				}
			}
		}
	}

	return res, err
}

func doDebug(c *Client, params string) (string, error) {
	var (
		res            = ""
		err     error  = nil
		isFlush bool   = false
		val     string = ""
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " debug " + params + " command received")
	sctx := c.getDebugCtx()
	params = strings.TrimSpace(params)
	if len(params) <= 0 {
		res = strconv.FormatBool(sctx.GetDebug())
	} else {
		flds := strings.Fields(params)
		if len(flds) > 2 {
			err = errors.New("debug command syntax error: too many parameters")
		} else {
			for _, f := range flds {
				if strings.EqualFold(f, "flush") {
					if isFlush {
						err = errors.New("debug command syntax error: 'flush' parameter is duplicated")
						break
					}
					isFlush = true
				} else {
					if len(val) > 0 {
						err = errors.New("debug command syntax error: too many parameters")
						break
					}
					val = f
				}
			}
			if err == nil {
				if len(val) > 0 {
					debugVal, parseErr := strconv.ParseBool(val)
					if parseErr != nil {
						err = errors.New("debug command syntax error: invalid boolean value '" + val + "'")
						debugVal = false
						cnf.GetLogger().Error("client " + c.UUID.String() + " debug command syntax error: invalid boolean value '" + val + "'")
					} else {
						sctx.SetDebug(debugVal)
						c.setDebugCtx(sctx)
						cnf.GetLogger().Info("client " + c.UUID.String() + "debug set to '" + val + "' successfully")
					}
				}
				if isFlush {
					err = c.flushDebugCtx()
					if err != nil {
						err = errors.New("error flushing debug context: " + err.Error())
						cnf.GetLogger().Error("client " + c.UUID.String() + " error flushing debug context: " + err.Error())
					} else {
						cnf.GetLogger().Info("client " + c.UUID.String() + "debug context flushed successfully")
					}
				}
			}
		}
	}

	return res, err
}

func doMaxModels(c *Client, params string) (string, error) {
	var (
		res            = ""
		err     error  = nil
		isFlush bool   = false
		val     string = ""
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " max_models " + params + " command received")
	sctx := c.getMaxModelsCtx()
	params = strings.TrimSpace(params)
	if len(params) <= 0 {
		res = strconv.FormatInt(int64(sctx.GetMaxModels()), 10)
	} else {
		flds := strings.Fields(params)
		if len(flds) > 2 {
			err = errors.New("max_models command syntax error: too many parameters")
		} else {
			for _, f := range flds {
				if strings.EqualFold(f, "flush") {
					if isFlush {
						err = errors.New("max_models command syntax error: 'flush' parameter is duplicated")
						break
					}
					isFlush = true
				} else {
					if len(val) > 0 {
						err = errors.New("max_models command syntax error: too many parameters")
						break
					}
					val = f
				}
			}
			if err == nil {
				if len(val) > 0 {
					maxModelsVal, parseErr := strconv.ParseInt(val, 10, 64)
					if parseErr != nil {
						err = errors.New("max_models command syntax error: invalid integer value '" + val + "'")
						maxModelsVal = 0
						cnf.GetLogger().Error("client " + c.UUID.String() + " max_models command syntax error: invalid integer value '" + val + "'")
					} else {
						sctx.SetMaxModels(int(maxModelsVal))
						c.setMaxModelsCtx(sctx)
						cnf.GetLogger().Info("client " + c.UUID.String() + "max_models set to '" + val + "' successfully")
					}
				}
				if isFlush {
					err = c.flushMaxModelsCtx()
					if err != nil {
						err = errors.New("error flushing max_models context: " + err.Error())
						cnf.GetLogger().Error("client " + c.UUID.String() + " error flushing max_models context: " + err.Error())
					} else {
						cnf.GetLogger().Info("client " + c.UUID.String() + "max_models context flushed successfully")
					}
				}
			}
		}
	}

	return res, err
}

func doReenterCount(c *Client, params string) (string, error) {
	var (
		res            = ""
		err     error  = nil
		isFlush bool   = false
		val     string = ""
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " reenter_count " + params + " command received")
	sctx := c.getReenterCountCtx()
	params = strings.TrimSpace(params)
	if len(params) <= 0 {
		res = strconv.FormatInt(int64(sctx.GetReenterCount()), 10)
	} else {
		flds := strings.Fields(params)
		if len(flds) > 2 {
			err = errors.New("reenter_count command syntax error: too many parameters")
		} else {
			for _, f := range flds {
				if strings.EqualFold(f, "flush") {
					if isFlush {
						err = errors.New("reenter_count command syntax error: 'flush' parameter is duplicated")
						break
					}
					isFlush = true
				} else {
					if len(val) > 0 {
						err = errors.New("reenter_count command syntax error: too many parameters")
						break
					}
					val = f
				}
			}
			if err == nil {
				if len(val) > 0 {
					reenterCountVal, parseErr := strconv.ParseInt(val, 10, 64)
					if parseErr != nil {
						err = errors.New("reenter_count command syntax error: invalid integer value '" + val + "'")
						reenterCountVal = 0
						cnf.GetLogger().Error("client " + c.UUID.String() + " reenter_count command syntax error: invalid integer value '" + val + "'")
					} else {
						sctx.SetReenterCount(int(reenterCountVal))
						c.setReenterCountCtx(sctx)
						cnf.GetLogger().Info("client " + c.UUID.String() + "reenter_count set to '" + val + "' successfully")
					}
				}
				if isFlush {
					err = c.flushReenterCountCtx()
					if err != nil {
						err = errors.New("error flushing reenter_count context: " + err.Error())
						cnf.GetLogger().Error("client " + c.UUID.String() + " error flushing reenter_count context: " + err.Error())
					} else {
						cnf.GetLogger().Info("client " + c.UUID.String() + "reenter_count context flushed successfully")
					}
				}
			}
		}
	}

	return res, err
}

func initCoreCommands(c *config.SymAIConfig) *map[string]SymAICoreCommand {
	cnf = c
	allCoreCommands = make(map[string]SymAICoreCommand, 0)
	allCoreCommands["shutdown"] = SymAICoreCommand{
		exec: doShutdown,
		help: "Syntax: shutdown\nStops all services of SymAI system, closes all opened sessions. All temporary data will be destroyed.",
	}
	allCoreCommands["stop"] = SymAICoreCommand{
		exec: doStop,
	}
	allCoreCommands["environment"] = SymAICoreCommand{
		exec: doEnvironment,
	}
	allCoreCommands["property"] = SymAICoreCommand{
		exec: doProperty,
	}
	allCoreCommands["behaviors"] = SymAICoreCommand{
		exec: doBehaviors,
	}
	allCoreCommands["actions"] = SymAICoreCommand{
		exec: doActions,
	}
	allCoreCommands["solver"] = SymAICoreCommand{
		exec: doSolver,
	}
	allCoreCommands["ai"] = SymAICoreCommand{
		exec: doAI,
	}
	allCoreCommands["debug"] = SymAICoreCommand{
		exec: doDebug,
	}
	allCoreCommands["max_models"] = SymAICoreCommand{
		exec: doMaxModels,
	}
	allCoreCommands["reenter_count"] = SymAICoreCommand{
		exec: doReenterCount,
	}
	allCoreCommands["traversalbeh"] = SymAICoreCommand{
		exec: doTraversalbeh,
	}
	allCoreCommands["help"] = SymAICoreCommand{
		exec:  doHelp,
		help:  "help [command]",
		descr: "help on all commands or on using parameters of particular command",
	}
	return &allCoreCommands
}

func doHelp(c *Client, params string) (string, error) {
	var (
		err error  = nil
		res string = ""
	)
	cnf.GetLogger().Info("client " + c.UUID.String() + " help " + params + " command received")
	if len(strings.TrimSpace(params)) > 0 {
		cmd, ok := allCoreCommands[strings.TrimSpace(params)]
		if !ok {
			err = errors.New("help: unknown command '" + strings.TrimSpace(params) + "'")
		} else {
			res = "command " + strings.TrimSpace(params) + "\n" + cmd.descr
		}
	} else {
		for k, v := range allCoreCommands {
			res = res + "\n" + k + " command\n"

			res = res + v.help
		}
	}
	return res, err
}
