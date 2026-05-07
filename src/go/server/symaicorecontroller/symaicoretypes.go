package symaicorecontroller

import (
	"errors"
	"os"
	"path/filepath"
	
	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"src/server/config"
	"src/server/parser"
)

type(
	// Client represents a single WebSocket connection
	Client struct {
		ctx map[string]interface{} // Context fields:
		// Possible context fields (to be extended as needed):
		// "symaiconfig" a SymAISection value @config for details
		// "environment" a FileBaseData value
		// "properties" a PropertyProcessingContext value
		// "actions" an ActionsProcessingContext value
		// "behaviors" a BehaviorsProcessingContext value
		conn *websocket.Conn
		UUID uuid.UUID
		send chan []byte
	}

	JsonFile struct {
		Filename string `json:"filename,omitempty"`
		Content  string `json:"content"`
	}

	EnvironmentProcessingContext struct {
		FileBaseData
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

)

//      ** FileBaseData methods **
func (f *FileBaseData) IsEqual(cmp FileBaseData) bool {
	return f.Filename == cmp.Filename && f.Content == cmp.Content
}

//	    ** ActionsProcessingContext methods **
func (a *ActionsProcessingContext) IsEqual(cmp ActionsProcessingContext) bool {
	if !a.FileBaseData.IsEqual(cmp.FileBaseData) {
		return false
	}

	if len(a.actions) != len(cmp.actions) {
		return false
	}

	for k, v := range a.actions {
		cv, ok := cmp.actions[k]
		if !ok || !v.IsEqual(cv) {
			return false
		}
	}

	return true
}

//      ** Client methods **
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

func (b *BehaviorsProcessingContext) GetBehavior(beh string) (parser.BehaviorBody, bool) {	
	r, exists := b.behaviors[beh]
	return r, exists
}

func (c *Client) newBehaviorsCtx() {
	c.ctx["behaviors"] = BehaviorsProcessingContext{
		FileBaseData: FileBaseData{
			Filename: "behaviors.beh",
			Content:  "",
			Filepath: filepath.Join(c.getBaseTempDir(), "behaviors.beh"),
		},
		behaviors: make(map[string]parser.BehaviorBody, 0),
	}
}

func (c *Client) getBehaviorsCtx() BehaviorsProcessingContext {
	r, ok := c.ctx["behaviors"]
	if !ok {
		c.newBehaviorsCtx()
		r, _ = c.ctx["behaviors"]
	}
	e := r.(BehaviorsProcessingContext)

	return e
}

func (c *Client) setBehaviorsCtx(ec BehaviorsProcessingContext) {
	c.ctx["behaviors"] = ec
}

func (c *Client) getBehaviorsFilename() string {
	return c.getBehaviorsCtx().Filename
}

func (c *Client) setBehaviorsFilename(fn string) {
	e := c.getBehaviorsCtx()
	e.Filename = fn
	c.setBehaviorsCtx(e)
}

func (c *Client) getBehaviorsFilepath() string {
	return c.getBehaviorsCtx().Filepath
}

func (c *Client) setBehaviorsFilepath(fn string) {
	e := c.getBehaviorsCtx()
	e.Filepath = fn
	c.setBehaviorsCtx(e)
}

func (c *Client) getBehaviorsContent() string {
	return c.getBehaviorsCtx().Content
}

func (c *Client) setBehaviorsContent(fn string) {
	e := c.getBehaviorsCtx()
	e.Content = fn
	c.setBehaviorsCtx(e)
}

func (c *Client) saveBehaviorsContent() error {
	err := WriteToFile(c.getBehaviorsFilepath(), c.getBehaviorsContent())

	if err != nil {
		err = errors.New("client " + c.UUID.String() + " error saving behaviors to the file '" + c.getBehaviorsFilepath() + "' " + err.Error())
	}

	return err
}

func (c *Client) getBehaviors() map[string]parser.BehaviorBody {
	return c.getBehaviorsCtx().behaviors
}

func (c *Client) setBehaviors(m map[string]parser.BehaviorBody) {
	ac := c.getBehaviorsCtx()
	ac.behaviors = m
	c.setBehaviorsCtx(ac)
}

