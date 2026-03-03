package parser

import (
	"reflect"
	"strconv"
	"strings"

	"github.com/antlr4-go/antlr/v4"

	"src/server/BehaviorsGrammar"
	"src/server/utils"
)

// A complete Visitor for a parse tree produced by ExpressionParser.
type ExpressionVisitor struct {
	BehaviorsGrammar.BaseBehaviorsGrammarVisitor

	// Expression staff
	hasTrigonometric bool
	hasNonLinear     bool
	varList          []string
	substitutionMap map[string]string

	// Behaviors related staff
	behaviors map[string]BehaviorBody
    // errors
	errorList []string
}

func NewExpressionVisitor() *ExpressionVisitor {
	return &ExpressionVisitor{
		hasTrigonometric: false,
		hasNonLinear:     false,
		varList:          []string{},
		substitutionMap:  map[string]string{},
	}
}

func (v *ExpressionVisitor) GetSubstitutionMap() map[string]string {
	return v.substitutionMap
}

func (v *ExpressionVisitor) SetSubstitutionMap(m map[string]string) {
	v.substitutionMap = m
}

func (v *ExpressionVisitor) HasTrigonometric() bool {
	return v.hasTrigonometric
}

func (v *ExpressionVisitor) HasNonLinear() bool {
	return v.hasNonLinear
}

func (v *ExpressionVisitor) GetVarList() []string {
	return v.varList
}

func (v *ExpressionVisitor) SetVarList(varList []string) {
	v.varList = varList
}

// Visit a parse tree produced by ExpressionParser#primaryExpression.
func (v *ExpressionVisitor) VisitPrimaryExpression(ctx *BehaviorsGrammar.PrimaryExpressionContext) interface{} {

	res := ""
	if ctx.LeftParen() != nil && ctx.RightParen() != nil {
		s := ""
		if ctx.Expression() != nil {
			s = strings.TrimSpace(ctx.Expression().Accept(v).(string))
			if len(s) > 0 {
				res = "(" + s + ")"
			}
		}
	} else if ctx.Constant() != nil {
		res = ctx.Constant().GetText()
	} else if ctx.Identifier() != nil {
		res = ctx.Identifier().GetText()
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#postfixExpression.
func (v *ExpressionVisitor) VisitPostfixExpression(ctx *BehaviorsGrammar.PostfixExpressionContext) interface{} {
	trig_funct := []string{"sin", "cos", "tan", "cotan", "asin", "acos", "atan", "acotan"}
	nl_funct := []string{"log", "lg", "sqrt", "exp", "pow"}

	s := strings.TrimSpace(ctx.PrimaryExpression().Accept(v).(string))
	var_add := true
	if ctx.GetChildCount() > 1 {
		i := 0
		if reflect.TypeOf(ctx.GetChild(1)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			if ctx.GetChild(1).(*antlr.TerminalNodeImpl).GetText() == "(" {
				st := ""
				n := ctx.GetChild(2)
				if reflect.TypeOf(n) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
					st = n.(antlr.ParseTree).Accept(v).(string)
				}
				fn := strings.ToLower(s)
				s = s + "(" + st + ")"

				if utils.Contains(trig_funct, fn) {
					v.hasTrigonometric = true
					var_add = false
				} else if utils.Contains(nl_funct, fn) {
					v.hasNonLinear = true
					var_add = false
				}
				i = 4
			} else {
				st := ""
				if reflect.TypeOf(ctx.GetChild(2)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
					st = ctx.GetChild(2).(*antlr.TerminalNodeImpl).GetText()
				} else {
					t := ctx.GetChild(2).(antlr.ParseTree).Accept(v)
					if t != nil {
						st = t.(string)
					}
				}

				s = s + "." + st
				i = 3
			}

			for i < ctx.GetChildCount() {
				if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
					s = s + ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
				} else {
					t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
					if t != nil {
						s = s + t.(string)
					}
				}
				i++
			}
		}
	}
	if var_add && len(s) > 0 {
		_, err := strconv.Atoi(s[0:1])
		if err != nil {
			if !utils.Contains(v.varList, s) {
				v.varList = append(v.varList, s)
			}
		}
		val, ok := v.substitutionMap[s]
		if ok {
			s = val
		}
		// TODO: Here we can place remove var statement as well.
	}

	return s
}

// Visit a parse tree produced by ExpressionParser#argumentExpressionList.
func (v *ExpressionVisitor) VisitArgumentExpressionList(ctx *BehaviorsGrammar.ArgumentExpressionListContext) interface{} {
	res := ""
	if ctx.AllAssignmentExpression() != nil {
		for _, expr := range ctx.AllAssignmentExpression() {
			s := ""
			t := expr.(antlr.ParseTree).Accept(v)
			if t != nil {
				s = t.(string)
			}
			if len(s) > 0 {
				if len(res) > 0 {
					res = res + ", " + s
				} else {
					res = s
				}
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#unaryExpression.
func (v *ExpressionVisitor) VisitUnaryExpression(ctx *BehaviorsGrammar.UnaryExpressionContext) interface{} {
	res := ""
	u := ""

	if ctx.PostfixExpression() != nil {
		res = ctx.PostfixExpression().Accept(v).(string)
		if ctx.UnaryOperator() != nil {
			u = ctx.UnaryOperator().Accept(v).(string)
		}
		res = u + res
	} 

	return res
}

// Visit a parse tree produced by ExpressionParser#unaryOperator.
func (v *ExpressionVisitor) VisitUnaryOperator(ctx *BehaviorsGrammar.UnaryOperatorContext) interface{} {
	res := ctx.GetText()
	return res
}

// Visit a parse tree produced by ExpressionParser#multiplicativeExpression.
func (v *ExpressionVisitor) VisitMultiplicativeExpression(ctx *BehaviorsGrammar.MultiplicativeExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
			if op == "**" {
				v.hasNonLinear = true
			}
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#additiveExpression.
func (v *ExpressionVisitor) VisitAdditiveExpression(ctx *BehaviorsGrammar.AdditiveExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#relationalExpression.
func (v *ExpressionVisitor) VisitRelationalExpression(ctx *BehaviorsGrammar.RelationalExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#equalityExpression.
func (v *ExpressionVisitor) VisitEqualityExpression(ctx *BehaviorsGrammar.EqualityExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#logicalAndExpression.
func (v *ExpressionVisitor) VisitLogicalAndExpression(ctx *BehaviorsGrammar.LogicalAndExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#logicalOrExpression.
func (v *ExpressionVisitor) VisitLogicalOrExpression(ctx *BehaviorsGrammar.LogicalOrExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#assignmentExpression.
func (v *ExpressionVisitor) VisitAssignmentExpression(ctx *BehaviorsGrammar.AssignmentExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#assignmentOperator.
func (v *ExpressionVisitor) VisitAssignmentOperator(ctx *BehaviorsGrammar.AssignmentOperatorContext) interface{} {
	return ctx.GetText()
}

// Visit a parse tree produced by ExpressionParser#expression.
func (v *ExpressionVisitor) VisitExpression(ctx *BehaviorsGrammar.ExpressionContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}
