package symaicorecontroller

import (
	"encoding/json"
	"errors"
	"fmt"

	"src/server/parser"
)

type TraversalbehParam struct {
	Solver       string `json:"solver,omitempty"`
	Behavior     string `json:"behavior,omitempty"`
	ReenterCount int    `json:"reenter_count,omitempty"`
	Debug        bool   `json:"debug,omitempty"`
	IsAI         bool   `json:"ai,omitempty"`
}

func checkTraversalbehParam(c *Client, cmd TraversalbehParam) error {
	if len(cmd.Solver) <= 0 {
		cmd.Solver = "Z3"
	}
	if len(cmd.Behavior) <= 0 {
		return errors.New("behavior parameter is required")
	}

	return nil
}

func doTraversalbeh(c *Client, params string) (string, error) {
	var (
		err error             = nil
		cmd TraversalbehParam = TraversalbehParam{
			Solver:       cnf.GetDefaultSolver(),
			Behavior:     "",
			ReenterCount: cnf.GetDefaultReenterCount(),
			Debug:        cnf.GetDefaultDebug(),
			IsAI:         cnf.GetDefaultAI(),
		}
		res string = ""
	)
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("traverslabeh. Caught panic: %v", r)
			cnf.GetLogger().Error("client " + c.UUID.String() + " traversalbeh command error: " + err.Error())	
			res = ""
		}
	}()

	cnf.GetLogger().Info("client " + c.UUID.String() + " traversalbeh " + params + " command received")
	if len(params) > 0 {
		err = json.Unmarshal([]byte(params), &cmd)
		if err != nil {
			return res, err
		}
	}
	err = checkTraversalbehParam(c, cmd)
	if err != nil {
		return res, err
	}
    c.setTraversalbehParam(cmd)
	res, err = c.traverseBehavior(cmd.Behavior)

	return res, err
}

func (c *Client) traverseBehavior(behavior string) (string, error) {
	var (
		err error = nil
		res string = ""
	)	
	cnf.GetLogger().Info("client " + c.UUID.String() + " traverse behavior '" + behavior + "'")

    beh, exists := c.getBehavior(behavior)
	if !exists {
		err = errors.New("behavior '" + behavior + "' not found in client context")
		cnf.GetLogger().Error("client " + c.UUID.String() + " traversalbeh command error: " + err.Error())		
	} else {
		beh = beh
		res, err = c.traverseBehaviorWithBody(beh)
	}	

	return res, err
}

func (c *Client) traverseBehaviorWithBody(beh parser.BehaviorBody, args ...interface{}) (string, error) {
	var (
		err error = nil
		res string = ""		
	)	
	if len(args) > 1 {
		err = errors.New("traverseBehaviorWithBody accepts at most one argument")
		cnf.GetLogger().Error("client " + c.UUID.String() + " traversalbeh command error: " + err.Error())		
	} else if len(args) == 1 {
		//
	} else {
		//res, err = c.traverseBehaviorWithArgs(beh, nil)
	}
	return res, err
}