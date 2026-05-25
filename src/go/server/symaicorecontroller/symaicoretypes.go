package symaicorecontroller

import (
	"errors"
	"os"
	"path/filepath"

	"src/server/config"
	"src/server/parser"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
)

type (
	// Client represents a single WebSocket connection
	Client struct {
		ctx map[string]interface{} 
		// Context fields:
		// Possible context fields (to be extended as needed):
		// "symaiconfig" a SymAISection value @config for details
		// "environment" a FileBaseData value
		// "properties" a PropertyProcessingContext value
		// "actions" an ActionsProcessingContext value
		// "behaviors" a BehaviorsProcessingContext value
		// "traversalbeh" a TraversalbehProcessingContext value for traversal behavior definitions
		// "ai" an AIProcessingContext value for AI mode definition 
		// "debug" a DebugProcessingContext value for debugging purposes 
		// "reentercount" a ReenterCountProcessingContext value for defining reenter count values 
		// "solver" a SolverProcessingContext value for defining solver values
		// "maxmodels" a MaxModelsProcessingContext value for defining max models values 
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

	TraversalbehProcessingContext struct {
		TraversalbehParam		
	}

	SolverProcessingContext struct {
		Solver string
	}

	ReenterCountProcessingContext struct {
		ReenterCount int
	}

	DebugProcessingContext struct {
		Debug bool
	}

	AIProcessingContext struct {
		IsAI bool
	}

	MaxModelsProcessingContext struct {
		MaxModels int
	}
)

// ** FileBaseData methods **
func (f *FileBaseData) IsEqual(cmp FileBaseData) bool {
	return f.Filename == cmp.Filename && f.Content == cmp.Content
}

// ** ActionsProcessingContext methods **
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

func (a *ActionsProcessingContext) GetAction(act string) (parser.ActionBody, bool) {
	r, exists := a.actions[act]
	return r, exists
}

// ** BehaviorsProcessingContext methods **
func (a *BehaviorsProcessingContext) IsEqual(cmp BehaviorsProcessingContext) bool {
	if !a.FileBaseData.IsEqual(cmp.FileBaseData) {
		return false
	}

	if len(a.behaviors) != len(cmp.behaviors) {
		return false
	}

	for k, v := range a.behaviors {
		cv, ok := cmp.behaviors[k]
		if !ok || !v.IsEqual(cv) {
			return false
		}
	}

	return true
}

// ** SolverProcessingContext methods **
func (s *SolverProcessingContext) GetSolver() string {
	if s.Solver == "" {
		s.Solver = cnf.GetDefaultSolver()
	}
	return s.Solver
}

func (s *SolverProcessingContext) SetSolver(solver string) {
	s.Solver = solver
}

// ** AIProcessingContext methods **
func (s *AIProcessingContext) GetAI() bool {	
	return s.IsAI
}

func (s *AIProcessingContext) SetAI(isAI bool) {
	s.IsAI = isAI
}

// ** DebugProcessingContext methods **
func (s *DebugProcessingContext) GetDebug() bool {	
	return s.Debug
}

func (s *DebugProcessingContext) SetDebug(isDebug bool) {
	s.Debug = isDebug
}

// ** ReenterCountProcessingContext methods **
func (s *ReenterCountProcessingContext) GetReenterCount() int {
	return s.ReenterCount
}

func (s *ReenterCountProcessingContext) SetReenterCount(reenterCount int) {
	s.ReenterCount = reenterCount
}

// ** MaxModelsProcessingContext methods **
func (s *MaxModelsProcessingContext) GetMaxModels() int {
	return s.MaxModels
}

func (s *MaxModelsProcessingContext) SetMaxModels(maxModels int) {
	s.MaxModels = maxModels
}

// ** Client methods **
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

func (c *Client) getBehavior(beh string) (parser.BehaviorBody, bool) {
	r, exists := c.getAllBehaviors() [beh]
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

func (c *Client) getAllBehaviors() map[string]parser.BehaviorBody {
	return c.getBehaviorsCtx().behaviors
}

func (c *Client) setAllBehaviors(m map[string]parser.BehaviorBody) {
	ac := c.getBehaviorsCtx()
	ac.behaviors = m
	c.setBehaviorsCtx(ac)
}

func (c *Client) setTraversalbehParam(cmd TraversalbehParam) {
	tb := c.getTraversalbehCtx()
	tb.TraversalbehParam = cmd
	c.setTraversalbehCtx(tb)		
}

func (c *Client) getTraversalbehParam() TraversalbehParam {
	return c.getTraversalbehCtx().TraversalbehParam	
}

func (c *Client) setTraversalbehSolver(solver string) {
	tb := c.getTraversalbehCtx()
	tb.TraversalbehParam.Solver = solver
	c.setTraversalbehCtx(tb)
}

func (c *Client) getTraversalbehSolver() string {
	return c.getTraversalbehCtx().TraversalbehParam.Solver
}

func (c *Client) setTraversalbehBehavior(behavior string) {
	tb := c.getTraversalbehCtx()
	tb.TraversalbehParam.Behavior = behavior
	c.setTraversalbehCtx(tb)
}

func (c *Client) getTraversalbehBehavior() string {
	return c.getTraversalbehCtx().TraversalbehParam.Behavior
}

func (c *Client) setTraversalbehReenterCount(reenterCount int) {
	tb := c.getTraversalbehCtx()
	tb.TraversalbehParam.ReenterCount = reenterCount
	c.setTraversalbehCtx(tb)
}

func (c *Client) getTraversalbehReenterCount() int	{
	return c.getTraversalbehCtx().TraversalbehParam.ReenterCount
}

func (c *Client) setTraversalbehDebug(debug bool) {
	tb := c.getTraversalbehCtx()
	tb.TraversalbehParam.Debug = debug
	c.setTraversalbehCtx(tb)
}

func (c *Client) getTraversalbehDebug() bool{
	return c.getTraversalbehCtx().TraversalbehParam.Debug
}

func (c *Client) newTraversalbehCtx() {
	sc := c.getSolverCtx()
	c.ctx["traversalbeh"] = TraversalbehProcessingContext{
		TraversalbehParam: TraversalbehParam{
			Solver: sc.GetSolver(),
			Behavior: "",
			ReenterCount: cnf.GetDefaultReenterCount(),
			Debug: cnf.GetDefaultDebug(),
			IsAI:  cnf.GetDefaultAI(),
		},
	}
}

func (c *Client) getTraversalbehCtx() TraversalbehProcessingContext {
	r, ok := c.ctx["traversalbeh"]
	if !ok {
		c.newTraversalbehCtx()
		r, _ = c.ctx["traversalbeh"]
	}
	e := r.(TraversalbehProcessingContext)

	return e
}

func (c *Client) setTraversalbehCtx(ec TraversalbehProcessingContext) {
	c.ctx["traversalbeh"] = ec
}

func (c *Client) newSolverCtx() {
	c.ctx["solver"] = SolverProcessingContext{
		Solver: cnf.GetDefaultSolver(),
	}
}

func (c *Client) getSolverCtx() SolverProcessingContext {
	r, ok := c.ctx["solver"]
	if !ok {
		c.newSolverCtx()
		r, _ = c.ctx["solver"]
	}
	e := r.(SolverProcessingContext)

	return e
}

func (c *Client) setSolverCtx(ec SolverProcessingContext) {
	c.ctx["solver"] = ec
}

func (c *Client) flushSolverCtx() error{
	sctx := c.getSolverCtx()
	sc := sctx.GetSolver()
    cf := config.GetConfig()
    cf.SetDefaultSolver(sc)
	return config.Save(cf, cf.GetPath())
}

func (c *Client) newAICtx() {
	c.ctx["ai"] = AIProcessingContext{
		IsAI: cnf.GetDefaultAI(),
	}
}

func (c *Client) getAICtx() AIProcessingContext {
	r, ok := c.ctx["ai"]
	if !ok {
		c.newAICtx()
		r, _ = c.ctx["ai"]
	}
	e := r.(AIProcessingContext)

	return e
}

func (c *Client) setAICtx(ec AIProcessingContext) {
	c.ctx["ai"] = ec
}

func (c *Client) flushAICtx() error{
	ictx := c.getAICtx()
	sc := ictx.GetAI()
    cf := config.GetConfig()
    cf.SetDefaultAI(sc)
	return config.Save(cf, cf.GetPath())
}

func (c *Client) newDebugCtx() {
	c.ctx["debug"] = DebugProcessingContext{
		Debug: cnf.GetDefaultDebug(),
	}
}

func (c *Client) getDebugCtx() DebugProcessingContext {
	r, ok := c.ctx["debug"]
	if !ok {
		c.newDebugCtx()
		r, _ = c.ctx["debug"]
	}
	e := r.(DebugProcessingContext)

	return e
}

func (c *Client) setDebugCtx(ec DebugProcessingContext) {
	c.ctx["debug"] = ec
}

func (c *Client) flushDebugCtx() error{
	ictx := c.getDebugCtx()
	sc := ictx.GetDebug()
    cf := config.GetConfig()
    cf.SetDefaultDebug(sc)
	return config.Save(cf, cf.GetPath())
}

func (c *Client) newReenterCountCtx() {
	c.ctx["reentercount"] = ReenterCountProcessingContext{
		ReenterCount: cnf.GetDefaultReenterCount(),
	}
}

func (c *Client) getReenterCountCtx() ReenterCountProcessingContext {
	r, ok := c.ctx["reentercount"]
	if !ok {
		c.newReenterCountCtx()
		r, _ = c.ctx["reentercount"]
	}
	e := r.(ReenterCountProcessingContext)

	return e
}

func (c *Client) setReenterCountCtx(ec ReenterCountProcessingContext) {
	c.ctx["reentercount"] = ec
}

func (c *Client) flushReenterCountCtx() error{
	ictx := c.getReenterCountCtx()
	sc := ictx.GetReenterCount()
    cf := config.GetConfig()
    cf.SetDefaultReenterCount(sc)
	return config.Save(cf, cf.GetPath())
}

func (c *Client) newMaxModelsCtx() {
	c.ctx["maxmodels"] = MaxModelsProcessingContext{
		MaxModels: cnf.GetDefaultMaxModels(),
	}
}

func (c *Client) getMaxModelsCtx() MaxModelsProcessingContext {
	r, ok := c.ctx["maxmodels"]
	if !ok {
		c.newMaxModelsCtx()
		r, _ = c.ctx["maxmodels"]
	}
	e := r.(MaxModelsProcessingContext)

	return e
}

func (c *Client) setMaxModelsCtx(ec MaxModelsProcessingContext) {
	c.ctx["maxmodels"] = ec
}

func (c *Client) flushMaxModelsCtx() error{
	ictx := c.getMaxModelsCtx()
	sc := ictx.GetMaxModels()
    cf := config.GetConfig()
    cf.SetDefaultMaxModels(sc)
	return config.Save(cf, cf.GetPath())
}
