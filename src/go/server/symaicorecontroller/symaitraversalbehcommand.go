package symaicorecontroller

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"

	"src/server/parser"
)

type TraversalbehParam struct {
	Solver       string `json:"solver,omitempty"`
	Behavior     string `json:"behavior,omitempty"`
	ReenterCount int    `json:"reenter_count,omitempty"`
	Debug        bool   `json:"debug,omitempty"`
	IsAI         bool   `json:"ai,omitempty"`
	MaxModels    int    `json:"max_models,omitempty"`
}

func NewTraversalbehParam() *TraversalbehParam {
	return &TraversalbehParam{
		Solver:       cnf.GetDefaultSolver(),
		Behavior:     "",
		ReenterCount: cnf.GetDefaultReenterCount(),
		Debug:        cnf.GetDefaultDebug(),
		IsAI:         cnf.GetDefaultAI(),
		MaxModels:    cnf.GetDefaultMaxModels(),
	}
}

func checkTraversalbehParam(c *Client, cmd *TraversalbehParam) error {
	traversalbehCtx := c.getTraversalbehCtx()
	traversalbehCtx.Solver = cmd.Solver
	// TODO: validate solver value if needed
	traversalbehCtx.ReenterCount = cmd.ReenterCount
	traversalbehCtx.Debug = cmd.Debug
	traversalbehCtx.IsAI = cmd.IsAI
	traversalbehCtx.MaxModels = cmd.MaxModels

	propCtx := c.getPropCtx()

	traversalbehCtx.Properties = propCtx.Content
	if len(propCtx.Content) <= 0 {
		return errors.New("traversalbeh command: properties context is empty")
	}

	envCtx := c.getEnvCtx()
	traversalbehCtx.Environment = envCtx.Content
	if len(envCtx.Content) <= 0 {
		return errors.New("traversalbeh command: environment context is empty")
	}

	actionsCtx := c.getActionsCtx()
	traversalbehCtx.Actions = actionsCtx.actions
	if len(actionsCtx.actions) <= 0 {
		return errors.New("traversalbeh command: actions context is empty")
	}

	traversalbehCtx.Behaviors = c.getBehaviorsCtx().behaviors
	if len(traversalbehCtx.Behaviors) <= 0 {
		return errors.New("traversalbeh command: behaviors context is empty")
	}
	if len(cmd.Behavior) <= 0 {
		for behName := range traversalbehCtx.Behaviors {
			cmd.Behavior = behName
			break
		}
	}
	if len(cmd.Behavior) <= 0 {
		return errors.New("traversalbeh command: behavior parameter is empty")
	}

	c.setTraversalbehCtx(traversalbehCtx)
	return nil
}

func doTraversalbeh(c *Client, params string) (string, error) {
	var (
		err error             = nil
		cmd TraversalbehParam = *NewTraversalbehParam()
		res string            = ""
	)
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("traverslabeh. Caught panic: %v", r)
			cnf.GetLogger().Error("client " + c.UUID.String() + " traversalbeh command error: " + err.Error())
			res = err.Error()
		}
	}()

	cnf.GetLogger().Info("client " + c.UUID.String() + " traversalbeh " + params + " command received")
	if len(params) > 0 {
		err = json.Unmarshal([]byte(params), &cmd)
		if err != nil {
			return res, err
		}
	}
	err = checkTraversalbehParam(c, &cmd)
	if err != nil {
		return res, err
	}
	c.setTraversalbehParam(cmd)
	res, err = c.traverseBehavior(cmd.Behavior)

	return res, err
}

func (c *Client) traverseBehavior(behavior string) (string, error) {
	var (
		err error  = nil
		res string = ""
	)
	cnf.GetLogger().Debug("client " + c.UUID.String() + " traverse behavior '" + behavior + "'")

	beh, exists := c.getBehavior(behavior)
	if !exists {
		err = errors.New("behavior '" + behavior + "' not found")
		cnf.GetLogger().Error("client " + c.UUID.String() + " traversalbeh command error: " + err.Error())
	} else {
		c.setTraversalbehTrace(*c.newTraversalbehTrace()) // reset trace for new traversal
		res, err = c.traverseBehaviorWithBody(beh)
	}

	return res, err
}

func (c *Client) splitAlternatives(beh []string) {
	tr := c.getTraversalbehTrace()
	cc, _ := tr.Exec.Pop()
	cc_dup := cc.Dup()
	for i := len(beh) - 1; i >= 0; i-- {
		if beh[i] == "+" {
			// End behavior processing, move to the next alternate or behavior in stack
			tr.Exec.Push(cc)
			c.setTraversalbehTrace(tr)			
			cc = *cc_dup
			continue
		}
		cc.Item.Push(beh[i])
	}
	tr.Exec.Push(cc)
	c.setTraversalbehTrace(tr)				
}

func (c *Client) traverseBehaviorWithBody(beh parser.BehaviorBody, args ...interface{}) (string, error) {
	var (
		err  error    = nil
		res  string   = ""
		tail []string = make([]string, 0)
	)
	if len(args) > 1 {
		err = errors.New("traverseBehaviorWithBody accepts at most one argument")
		cnf.GetLogger().Error("client " + c.UUID.String() + " traversalbeh command error: " + err.Error())
	} else if len(args) == 1 {
		tail = args[0].([]string)
	}

	tr := c.getTraversalbehTrace()
	tr.Exec.Push(ExecItem{
		Item: StringStack{
			Stack: *NewStack[string](),
		},
		Env: c.getTraversalbehCtx().Environment,
	})
	c.setTraversalbehTrace(tr)

	c.splitAlternatives(beh.Terminals)
	if tail != nil && len(tail) > 0 {	
		c.splitAlternatives(tail)
	}

	for !tr.Exec.IsEmpty(){
		tr = c.getTraversalbehTrace()
		cc, _ := tr.Exec.Pop()
		if cc.Item.IsEmpty() {
			tr.Exec.Pop()
			c.setTraversalbehTrace(tr)
			// TODO: Here we should append collected trace to the result if needed, for now we just continue processing
			continue
		}
		
		cur, _ := cc.Item.Pop()
		
		tr.Exec.Push(cc)
		c.setTraversalbehTrace(tr)
		
		if cur == "." {
			continue
		}
		if cur == "+" {
			// End behavior processing, move to the next alternate or behavior in stack
			continue
		}
		if strings.EqualFold(cur, "delta") {
			// delta terminal, skip, if needed, can be used to trigger some specific processing in the future
			continue
		}
		if beh, exists := c.getBehavior(cur); exists {
			// behavior terminal
			c.setTraversalbehTrace(tr)
			c.splitAlternatives(beh.Terminals)
			tr = c.getTraversalbehTrace()
			continue
		} else {
			// action terminal
		}
	}

	return res, err
}
