package parser

import (
	"reflect"
	"strconv"
	"strings"

	"github.com/antlr4-go/antlr/v4"

	"src/server/BehaviorsGrammar"
	"src/server/utils"
)

// A complete Visitor for a parse tree produced by ActionsParser.
type (
	ActionBody struct {
		Logical   string
		Condition string
		Actions   []string
	}

	ActionsVisitor struct {
		ExpressionVisitor		

		// Actions related staff
		actions          map[string]ActionBody
		hasLogical       bool
		actionExpression []string
	}
)

func NewActionBody() ActionBody {
	return ActionBody{
		Logical:   "",
		Condition: "",
		Actions:   make([]string, 0),		
	}
}

func (a *ActionBody) hasLogical() bool {
	return a.Logical != ""
}

func NewActionsVisitor() *ActionsVisitor {
	return &ActionsVisitor{
		ExpressionVisitor: ExpressionVisitor{
			hasTrigonometric: false,
			hasNonLinear:     false,
			varList:          make([]string, 0),
			substitutionMap:  make(map[string]string, 0),
			ErrorProcessing: ErrorProcessing{
						errorList: make([]string, 0),
			},
		},
		actions:    make(map[string]ActionBody, 0),
		hasLogical: false,
	}
}

func (v *ActionsVisitor) GetActions() map[string]ActionBody {
	return v.actions
}

func (v *ActionsVisitor) SetActions(m map[string]ActionBody) {
	v.actions = m
}

// Visit a parse tree produced by ExpressionGrammarParser#assignmentExpressionList.
func (v *ActionsVisitor) VisitAssignmentExpressionList(ctx *BehaviorsGrammar.AssignmentExpressionListContext) interface{} {
	res := ""
	v.hasLogical = false
	v.actionExpression = make([]string, 0)
	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			vt := ctx.GetChild(i).(antlr.ParseTree)
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				s := t.(string)
				res = res + s
				if utils.IsConstant(s) {
					if utils.IsBoolean(s) {
						s = ""
					}
					if utils.IsInteger(s) {
						s = ""
					}
				}
				if len(s) > 0 {
					v.actionExpression = append(v.actionExpression, s)
				}
			}
			if vt.GetChildCount() < 2 {
				v.hasLogical = true
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionGrammarParser#actions.
func (v *ActionsVisitor) VisitActions(ctx *BehaviorsGrammar.ActionsContext) interface{} {
	res := ""
	for i := 0; i < ctx.GetChildCount(); {
        v.hasLogical = false
	    v.actionExpression = make([]string, 0)
	
		t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
		if t == nil {
			if !v.HasError() {
				v.addError("Actions description error detected. Action name expected")
			}
			break
		}
		nm := t.(string)
		res = res + nm + ":"
		i = i + 2
		// ":" skipped. Here should be a logicalAnd expression. Note: it can be presented as 1 or as 0 or as true or as false constants
		t = ctx.GetChild(i).(antlr.ParseTree).Accept(v)
		if t == nil {
			if !v.HasError() {
				v.addError("Actions description error detected. Action '" + nm + "' missing condition")
			}
			break
		}
		cnd := t.(string)
		if utils.IsConstant(cnd) {
			cnd = "0>1"
			if utils.IsBoolean(t.(string)) {
				b, _ := strconv.ParseBool(strings.ToLower(t.(string)))
				if b {
					cnd = "0<1"
				}
			} else {
				if utils.IsInteger(t.(string)) {
					j, _ := strconv.Atoi(t.(string))
					if j == 1 {
						cnd = "0<1"
					}
				}
			}
		}
		i = i + 2
		res = res + cnd + "->"
		// assignementExpressionList or comma
		if reflect.TypeOf(ctx.GetChild(i)) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			ch := ctx.GetChild(i).(antlr.ParseTree).Accept(v).(string)
			res = res + ch
			i = i + 1
		}
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) &&
			ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText() == "," {
			i = i + 1
			res = res + ","
		}

	    lg := ""
		l := len(v.actionExpression)
		if 	v.hasLogical {
			l = l - 1
			lg = v.actionExpression[l]			
		}
		act := make([]string, l)
		for j := 0; j < l; j++ {
			act[j] = v.actionExpression[j]
		}
	    
		_, err := v.actions[nm]
		if !err {
			a := NewActionBody()
			a.Logical = lg
			a.Condition = cnd
			a.Actions = act
			v.actions[nm] = a
		} else {
			v.addError("Duplicated action name '" + nm + "'")
		}
	}

	return res
}
