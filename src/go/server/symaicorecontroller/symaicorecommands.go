package symaicorecontroller

import (
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"syscall"

	"src/server/config"
	"src/server/parser"
)

type (
	EnvironmentProcessingContext struct {
		FileBaseData
	}

	JsonFile struct {
		Filename string `json:"filename,omitempty"`
		Content  string `json:"content"`
	}

	PropertyProcessingContext struct {
		FileBaseData
	}

	ActionsProcessingContext struct {
		FileBaseData
		actions map[string]parser.ActionBody
	}

	BehaviorsProcessingContext struct {
		FileBaseData
		behaviors map[string]parser.BehaviorBody
	}

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

func (c *Client) getExpressionModuleURL() (string, int, error) {
	sc, ok := c.ctx["symaiconfig"].(config.SymAISectionConfig)
	if ok {
		return sc.ExpressionHost, sc.ExpressionPort, nil
	}
	return "", -1, errors.New("cnf is nil or symaiconfig value is missing in client context")
}

func (c *Client) getFrontendModuleURL() (string, int, error) {
	if cnf != nil {
		return cnf.FrontendSection.Host, cnf.FrontendSection.Port, nil
	}
	return "", -1, errors.New("cnf is nil")
}

func (c *Client) getBaseTempDir() string {
	var res = ""
	sc, ok := c.ctx["symaiconfig"].(config.SymAISectionConfig)
	if ok {
		res = sc.TempDir
	}
	return filepath.Join(res, c.UUID.String())
}

func (c *Client) newEnvCtx() {
	c.ctx["environment"] = EnvironmentProcessingContext{
		FileBaseData: FileBaseData{
			Filename: "environment.env",
			Content:  "",
			Filepath: filepath.Join(c.getBaseTempDir(), "environment.env"),
		},
	}
}

func (c *Client) getEnvCtx() EnvironmentProcessingContext {
	r, ok := c.ctx["environment"]
	if !ok {
		c.newEnvCtx()
		r, _ = c.ctx["environment"]
	}
	e := r.(EnvironmentProcessingContext)

	return e
}

func (c *Client) setEnvCtx(ec EnvironmentProcessingContext) {
	c.ctx["environment"] = ec
}

func (c *Client) getEnvFilename() string {
	return c.getEnvCtx().Filename
}

func (c *Client) setEnvFilename(fn string) {
	e := c.getEnvCtx()
	e.Filename = fn
	c.setEnvCtx(e)
}

func (c *Client) getEnvFilepath() string {
	return c.getEnvCtx().Filepath
}

func (c *Client) setEnvFilepath(fn string) {
	e := c.getEnvCtx()
	e.Filepath = fn
	c.setEnvCtx(e)
}

func (c *Client) getEnvContent() string {
	return c.getEnvCtx().Content
}

func (c *Client) setEnvContent(fn string) {
	e := c.getEnvCtx()
	e.Content = fn
	c.setEnvCtx(e)
}

func (c *Client) saveEnvContent() error {
	err := WriteToFile(c.getEnvFilepath(), c.getEnvContent())

	if err != nil {
		err = errors.New("client " + c.UUID.String() + " error saving environment to the file '" + c.getEnvFilepath() + "' " + err.Error())
	}

	return err
}

func (c *Client) removeAllTempData() error {
	return os.RemoveAll(c.getBaseTempDir())
}

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

func (c *Client) newPropCtx() {
	c.ctx["property"] = PropertyProcessingContext{
		FileBaseData: FileBaseData{
			Filename: "property.prop",
			Content:  "",
			Filepath: filepath.Join(c.getBaseTempDir(), "property.prop"),
		},
	}
}

func (c *Client) getPropCtx() PropertyProcessingContext {
	r, ok := c.ctx["property"]
	if !ok {
		c.newPropCtx()
		r, _ = c.ctx["property"]
	}
	e := r.(PropertyProcessingContext)

	return e
}

func (c *Client) setPropCtx(ec PropertyProcessingContext) {
	c.ctx["property"] = ec
}

func (c *Client) getPropFilename() string {
	return c.getPropCtx().Filename
}

func (c *Client) setPropFilename(fn string) {
	e := c.getPropCtx()
	e.Filename = fn
	c.setPropCtx(e)
}

func (c *Client) getPropFilepath() string {
	return c.getPropCtx().Filepath
}

func (c *Client) setPropFilepath(fn string) {
	e := c.getPropCtx()
	e.Filepath = fn
	c.setPropCtx(e)
}

func (c *Client) getPropContent() string {
	return c.getPropCtx().Content
}

func (c *Client) setPropContent(fn string) {
	e := c.getPropCtx()
	e.Content = fn
	c.setPropCtx(e)
}

func (c *Client) savePropContent() error {
	err := WriteToFile(c.getPropFilepath(), c.getPropContent())

	if err != nil {
		err = errors.New("client " + c.UUID.String() + " error saving property to the file '" + c.getPropFilepath() + "' " + err.Error())
	}

	return err
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

func (c *Client) newActionsCtx() {
	c.ctx["actions"] = ActionsProcessingContext{
		FileBaseData: FileBaseData{
			Filename: "actions.act",
			Content:  "",
			Filepath: filepath.Join(c.getBaseTempDir(), "actions.act"),
		},
		actions: make(map[string]parser.ActionBody, 0),
	}
}

func (c *Client) getActionsCtx() ActionsProcessingContext {
	r, ok := c.ctx["actions"]
	if !ok {
		c.newActionsCtx()
		r, _ = c.ctx["actions"]
	}
	e := r.(ActionsProcessingContext)

	return e
}

func (c *Client) setActionsCtx(ec ActionsProcessingContext) {
	c.ctx["actions"] = ec
}

func (c *Client) getActionsFilename() string {
	return c.getActionsCtx().Filename
}

func (c *Client) setActionsFilename(fn string) {
	e := c.getActionsCtx()
	e.Filename = fn
	c.setActionsCtx(e)
}

func (c *Client) getActionsFilepath() string {
	return c.getActionsCtx().Filepath
}

func (c *Client) setActionsFilepath(fn string) {
	e := c.getActionsCtx()
	e.Filepath = fn
	c.setActionsCtx(e)
}

func (c *Client) getActionsContent() string {
	return c.getActionsCtx().Content
}

func (c *Client) setActionsContent(fn string) {
	e := c.getActionsCtx()
	e.Content = fn
	c.setActionsCtx(e)
}

func (c *Client) saveActionsContent() error {
	err := WriteToFile(c.getActionsFilepath(), c.getActionsContent())

	if err != nil {
		err = errors.New("client " + c.UUID.String() + " error saving actions to the file '" + c.getActionsFilepath() + "' " + err.Error())
	}

	return err
}

func (c *Client) getActions() map[string]parser.ActionBody {
	return c.getActionsCtx().actions
}

func (c *Client) setActions(m map[string]parser.ActionBody) {
	ac := c.getActionsCtx()
	ac.actions = m
	c.setActionsCtx(ac)
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
					res = ""
					
					c.setActionsContent(r.(string))
					//err = c.saveActionsContent() // Will be uncommented, if we'll need to keep actions permanently
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
	allCoreCommands["actions"] = SymAICoreCommand{
		exec: doActions,
	}
	allCoreCommands["property"] = SymAICoreCommand{
		exec: doProperty,
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
