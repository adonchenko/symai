package parser

import (
	"errors"
	"fmt"
	"math"
	"reflect"
	"strconv"
	"strings"

	"github.com/antlr4-go/antlr/v4"

	"src/server/BehaviorsGrammar"
	"src/server/utils"
)

// A complete Visitor for a parse tree produced by ExpressionParser.
type EvalVisitor struct {
	BehaviorsGrammar.BaseBehaviorsGrammarVisitor
	ErrorProcessing

	// Expression staff
	hasTrigonometric bool
	hasNonLinear     bool
	varList          []string
	substitutionMap  map[string]string
}

func NewEvalVisitor(args ...interface{}) *EvalVisitor {
	return &EvalVisitor{
		hasTrigonometric: false,
		hasNonLinear:     false,
		varList:          []string{},
		substitutionMap:  map[string]string{},
		ErrorProcessing:  *NewErrorProcessing(),
	}
}

func (v *EvalVisitor) GetSubstitutionMap() map[string]string {
	return v.substitutionMap
}

func (v *EvalVisitor) SetSubstitutionMap(m map[string]string) {
	v.substitutionMap = m
}

func (v *EvalVisitor) HasTrigonometric() bool {
	return v.hasTrigonometric
}

func (v *EvalVisitor) HasNonLinear() bool {
	return v.hasNonLinear
}

func (v *EvalVisitor) GetVarList() []string {
	return v.varList
}

func (v *EvalVisitor) SetVarList(varList []string) {
	v.varList = varList
}

func (v *EvalVisitor) IsInVarList(s string) bool {
	b := false
	for _, r := range v.varList {
		if r == s {
			b = true
			break
		}
	}
	return b
}

// Visit a parse tree produced by ExpressionParser#primaryExpression.
func (v *EvalVisitor) VisitPrimaryExpression(ctx *BehaviorsGrammar.PrimaryExpressionContext) interface{} {

	res := ""
	if ctx.LeftParen() != nil && ctx.RightParen() != nil && ctx.Expression() != nil {
		tval := ctx.Expression().Accept(v)
		if tval != nil {
			tp := reflect.ValueOf(tval).Kind()
			if tp == reflect.Bool ||
				tp == reflect.Int || tp == reflect.Int8 || tp == reflect.Int16 ||
				tp == reflect.Int32 || tp == reflect.Int64 ||
				tp == reflect.Float32 || tp == reflect.Float64 {
				return tval
			}
			s := strings.TrimSpace(tval.(string))
			if len(s) > 0 {
				res = "(" + s + ")"
			}
		}
	} else if ctx.Constant() != nil {
		s := ctx.Constant().GetText()
		r, err := strconv.ParseFloat(s, 64)
		if err != nil {
			r, _ := strconv.ParseBool(strings.ToLower(s))
			return r
		}
		return r
	} else if ctx.Identifier() != nil {
		res = ctx.Identifier().GetText()
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#postfixExpression.
func (v *EvalVisitor) VisitPostfixExpression(ctx *BehaviorsGrammar.PostfixExpressionContext) interface{} {
	trig_funct := []string{"sin", "cos", "tan", "cotan", "asin", "acos", "atan", "acotan"}
	nl_funct := []string{"log", "lg", "sqrt", "exp", "pow"}

	tval := ctx.PrimaryExpression().Accept(v)
	if reflect.TypeOf(tval) != reflect.TypeOf("") {
		return tval
	}

	s := strings.TrimSpace(tval.(string))
	var_add := true
	if ctx.GetChildCount() > 1 {
		i := 0
		if reflect.TypeOf(ctx.GetChild(1)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			if ctx.GetChild(1).(*antlr.TerminalNodeImpl).GetText() == "(" {
				st := make([]interface{}, 0)
				n := ctx.GetChild(2)
				if reflect.TypeOf(n) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
					st = n.(antlr.ParseTree).Accept(v).([]interface{}) // argumentExpressionList
				}
				fn := strings.ToLower(s)
				s = ""
				for _, arg := range st {
					if len(s) > 0 {
						s = s + ","
					}
					s = s + fmt.Sprintf("%v", arg)
				}

				s = fn + "(" + s + ")"

				if utils.Contains(trig_funct, fn) {
					v.hasTrigonometric = true
					var_add = false
					ret, err := processEmbeddedFunction(fn, st)
					if err != nil {
						v.addError(err.Error())
					}
					return ret
				} else if utils.Contains(nl_funct, fn) {
					v.hasNonLinear = true
					var_add = false
					ret, err := processEmbeddedFunction(fn, st)
					if err != nil {
						v.addError(err.Error())
					}
					return ret
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
	if var_add && len(s) > 0 && s[0] != '(' {
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
	}

	return s
}

// Visit a parse tree produced by ExpressionParser#argumentExpressionList.
func (v *EvalVisitor) VisitArgumentExpressionList(ctx *BehaviorsGrammar.ArgumentExpressionListContext) interface{} {
	res := make([]interface{}, 0)

	for _, expr := range ctx.AllAssignmentExpression() {
		res = append(res, expr.(antlr.ParseTree).Accept(v))
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#unaryExpression.
func (v *EvalVisitor) VisitUnaryExpression(ctx *BehaviorsGrammar.UnaryExpressionContext) interface{} {
	var res interface{}

	if ctx.PostfixExpression() != nil {
		res = ctx.PostfixExpression().Accept(v)

		if ctx.UnaryOperator() != nil {
			u := strings.TrimSpace(ctx.UnaryOperator().Accept(v).(string))
			switch u {
			case "+":
				// do nothing, just return the value
				switch reflect.TypeOf(res).Kind() {
				case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64,
					reflect.Float32, reflect.Float64, reflect.Bool:
					// do nothing, just return the value
				case reflect.String:
					if len(res.(string)) > 0 && res.(string)[0] == '+' {
						res = res.(string)[1:]
					} else {
						res = "+" + res.(string)
					}
				}
			case "-":
				switch reflect.TypeOf(res).Kind() {
				case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
					res = -res.(int)
				case reflect.Float32, reflect.Float64:
					res = -res.(float64)
				case reflect.Bool:
					// do nothing, just return the value
				case reflect.String:
					if len(res.(string)) > 0 && res.(string)[0] == '-' {
						res = res.(string)[1:]
					} else {
						res = "-" + res.(string)
					}
				}
			case "!":
				switch reflect.TypeOf(res).Kind() {
				case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
					res = res.(int) == 0
				case reflect.Float32, reflect.Float64:
					res = res.(float64) == 0
				case reflect.Bool:
					res = !res.(bool)
				case reflect.String:
					if len(res.(string)) > 0 && res.(string)[0] == '!' {
						res = res.(string)[1:]
					} else {
						res = "!" + res.(string)
					}
				}
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#unaryOperator.
func (v *EvalVisitor) VisitUnaryOperator(ctx *BehaviorsGrammar.UnaryOperatorContext) interface{} {
	res := ctx.GetText()
	return res
}

func (v *EvalVisitor) processFloat64Func(
	t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind,

	task func(
		t1 interface{}, t1Kind reflect.Kind,
		t2 interface{}, t2Kind reflect.Kind) (interface{}, error),

	taskNotationStr string,
	checkZero bool) (interface{}, error) {
	var (
		res interface{}
		err error = nil
	)

	if v.HasError() {
		return 0, errors.New("cannot process function due to previous errors")
	}
	if checkZero && t2Kind == reflect.Bool && !t2.(bool) {
		res = 0
		v.addError(fmt.Sprintf("operation %s:Division by zero", taskNotationStr))
		err = errors.New(v.errorList[len(v.errorList)-1])
	} else {
		if checkZero {
			if (t2Kind == reflect.Int || t2Kind == reflect.Int8 ||
				t2Kind == reflect.Int16 || t2Kind == reflect.Int32 || t2Kind == reflect.Int64) &&
				t2.(int) == 0 {
				res = 0
				v.addError(fmt.Sprintf("operation %s:Division by zero", taskNotationStr))
				err = errors.New(v.errorList[len(v.errorList)-1])
			} else {
				if (t2Kind == reflect.Float32 || t2Kind == reflect.Float64) && t2.(float64) == 0 {
					res = 0
					v.addError(fmt.Sprintf("operation %s:Division by zero", taskNotationStr))
					err = errors.New(v.errorList[len(v.errorList)-1])
				}
			}
		}
	}
	if err == nil {
		if t1Kind == reflect.String || t2Kind == reflect.String {
			res = fmt.Sprintf("%v%s%v", t1, taskNotationStr, t2)
		} else {
			res, err = task(t1, t1Kind, t2, t2Kind)
			if err != nil {
				v.addError(fmt.Sprintf("operation %s: %s", taskNotationStr, err.Error()))
				err = errors.New(v.errorList[len(v.errorList)-1])
			}
		}
	}

	return res, err
}

// Visit a parse tree produced by ExpressionParser#multiplicativeExpression.
func (v *EvalVisitor) VisitMultiplicativeExpression(ctx *BehaviorsGrammar.MultiplicativeExpressionContext) interface{} {
	var err error = nil

	res := ctx.GetChild(0).(antlr.ParseTree).Accept(v)
	op := ""

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op = ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			tp := reflect.TypeOf(t).Kind()
			switch op {
			case "**":
				v.hasNonLinear = true
				res, err = v.processFloat64Func(res, reflect.TypeOf(res).Kind(), t, tp,
					func(t1 interface{}, t1Kind reflect.Kind,
						t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {
						if t1Kind == reflect.Bool {
							t1 = utils.BoolToFloat64(t1.(bool))
						}
						if t2Kind == reflect.Bool {
							t2 = utils.BoolToFloat64(t2.(bool))
						}
						res := math.Pow(t1.(float64), t2.(float64))
						return res, nil
					},
					"**", false)
			case "/":
				res, err = v.processFloat64Func(res, reflect.TypeOf(res).Kind(), t, tp,
					func(t1 interface{}, t1Kind reflect.Kind,
						t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {
						if t1Kind == reflect.Bool {
							t1 = utils.BoolToFloat64(t1.(bool))
						}
						if t2Kind == reflect.Bool {
							t2 = utils.BoolToFloat64(t2.(bool))
						}
						res := t1.(float64) / t2.(float64)
						return res, nil
					},
					"/", true)
			case "*":
				res, err = v.processFloat64Func(res, reflect.TypeOf(res).Kind(), t, tp,
					func(t1 interface{}, t1Kind reflect.Kind,
						t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {
						if t1Kind == reflect.Bool {
							t1 = utils.BoolToFloat64(t1.(bool))
						}
						if t2Kind == reflect.Bool {
							t2 = utils.BoolToFloat64(t2.(bool))
						}
						res := t1.(float64) * t2.(float64)
						return res, nil
					},
					"*", false)
			case "%":
				res, err = v.processFloat64Func(res, reflect.TypeOf(res).Kind(), t, tp,
					func(t1 interface{}, t1Kind reflect.Kind,
						t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {
						if t1Kind == reflect.Bool {
							t1 = utils.BoolToFloat64(t1.(bool))
						}
						if t2Kind == reflect.Bool {
							t2 = utils.BoolToFloat64(t2.(bool))
						}
						res := math.Mod(t1.(float64), t2.(float64))
						return res, nil
					},
					"%", true)
			}
		}
	}
	if err != nil {
		res = 0
	}
	return res
}

// Visit a parse tree produced by ExpressionParser#additiveExpression.
func (v *EvalVisitor) VisitAdditiveExpression(ctx *BehaviorsGrammar.AdditiveExpressionContext) interface{} {
	var err error = nil

	res := ctx.GetChild(0).(antlr.ParseTree).Accept(v)
	op := ""

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op = ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			tp := reflect.TypeOf(t).Kind()
			switch op {
			case "+":
				res, err = v.processFloat64Func(res, reflect.TypeOf(res).Kind(), t, tp,
					func(t1 interface{}, t1Kind reflect.Kind,
						t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {
						if t1Kind == reflect.Bool {
							t1 = utils.BoolToFloat64(t1.(bool))
						}
						if t2Kind == reflect.Bool {
							t2 = utils.BoolToFloat64(t2.(bool))
						}
						res := t1.(float64) + t2.(float64)
						return res, nil
					},
					"+", false)
			case "-":
				res, err = v.processFloat64Func(res, reflect.TypeOf(res).Kind(), t, tp,
					func(t1 interface{}, t1Kind reflect.Kind,
						t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {
						if t1Kind == reflect.Bool {
							t1 = utils.BoolToFloat64(t1.(bool))
						}
						if t2Kind == reflect.Bool {
							t2 = utils.BoolToFloat64(t2.(bool))
						}
						res := t1.(float64) - t2.(float64)
						return res, nil
					},
					"-", false)
			}
		}
	}
	if err != nil {
		res = 0
	}
	return res
}

// Visit a parse tree produced by ExpressionParser#relationalExpression.
func (v *EvalVisitor) VisitRelationalExpression(ctx *BehaviorsGrammar.RelationalExpressionContext) interface{} {
	var (
		res    interface{} = nil
		r      interface{} = nil
		err    error       = nil
		first  interface{} = nil
		second interface{} = nil
		op     string      = ""
		fn     func(t1 interface{}, t1Kind reflect.Kind,
			t2 interface{}, t2Kind reflect.Kind) (interface{}, error) = nil
	)

	first = ctx.GetChild(0).(antlr.ParseTree).Accept(v)

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			if first != nil && second != nil && len(op) > 0 {
				r, err = v.processFloat64Func(first, reflect.TypeOf(first).Kind(),
					second, reflect.TypeOf(second).Kind(),
					fn, op, false)
				if err != nil {
					r = false
					v.addError(fmt.Sprintf("operation %s: %s", op, err.Error()))
				}
				first = second
				second = nil
				if res == nil && r != nil {
					res = r
				} else if res != nil && r != nil {
					if reflect.TypeOf(res).Kind() == reflect.Bool && reflect.TypeOf(r).Kind() == reflect.Bool {
						res = res.(bool) && r.(bool)
					} else {
						res = fmt.Sprintf("%v&&%v", res, r)
					}
				}
			}
			op = ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			switch op {
			case "<":
				fn = processLT
			case "<=":
				fn = processLE
			case ">":
				fn = processGT
			case ">=":
				fn = processGE
			}
		} else {
			second = ctx.GetChild(i).(antlr.ParseTree).Accept(v)
		}
	}

	if first != nil && second != nil && len(op) > 0 {
		r, err = v.processFloat64Func(first, reflect.TypeOf(first).Kind(),
			second, reflect.TypeOf(second).Kind(),
			fn, op, false)
		if err != nil {
			v.addError(fmt.Sprintf("operation %s: %s", op, err.Error()))
			r = false
		}

		if res == nil && r != nil {
			res = r
		} else if res != nil && r != nil {
			if reflect.TypeOf(res).Kind() == reflect.Bool && reflect.TypeOf(r).Kind() == reflect.Bool {
				res = res.(bool) && r.(bool)
			} else {
				res = fmt.Sprintf("%v&&%v", res, r)
			}
		}
	} else {
		if res == nil && first != nil {
			res = first
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#equalityExpression.
func (v *EvalVisitor) VisitEqualityExpression(ctx *BehaviorsGrammar.EqualityExpressionContext) interface{} {
	var (
		res    interface{} = nil
		r      interface{} = nil
		err    error       = nil
		first  interface{} = nil
		second interface{} = nil
		op     string      = ""
		fn     func(t1 interface{}, t1Kind reflect.Kind,
			t2 interface{}, t2Kind reflect.Kind) (interface{}, error) = nil
	)

	first = ctx.GetChild(0).(antlr.ParseTree).Accept(v)

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			if first != nil && second != nil && len(op) > 0 {
				r, err = v.processFloat64Func(first, reflect.TypeOf(first).Kind(),
					second, reflect.TypeOf(second).Kind(),
					fn, op, false)
				if err != nil {
					v.addError(fmt.Sprintf("operation %s: %s", op, err.Error()))
					r = false
				}

				first = second
				second = nil
				if res == nil && r != nil {
					res = r
				} else if res != nil && r != nil {
					if reflect.TypeOf(res).Kind() == reflect.Bool && reflect.TypeOf(r).Kind() == reflect.Bool {
						res = res.(bool) && r.(bool)
					} else {
						res = fmt.Sprintf("%v&&%v", res, r)
					}
				}
			}
			op = ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			switch op {
			case "==":
				fn = processEQ
			case "!=":
				fn = processNE
			}
		} else {
			second = ctx.GetChild(i).(antlr.ParseTree).Accept(v)
		}
	}

	if first != nil && second != nil && len(op) > 0 {
		r, err = v.processFloat64Func(first, reflect.TypeOf(first).Kind(),
			second, reflect.TypeOf(second).Kind(),
			fn, op, false)
		if err != nil {
			v.addError(fmt.Sprintf("operation %s: %s", op, err.Error()))
			r = false
		}

		if res == nil && r != nil {
			res = r
		} else if res != nil && r != nil {
			if reflect.TypeOf(res).Kind() == reflect.Bool && reflect.TypeOf(r).Kind() == reflect.Bool {
				res = res.(bool) && r.(bool)
			} else {
				res = fmt.Sprintf("%v&&%v", res, r)
			}
		}
	} else {
		if res == nil && first != nil {
			res = first
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#logicalAndExpression.
func (v *EvalVisitor) VisitLogicalAndExpression(ctx *BehaviorsGrammar.LogicalAndExpressionContext) interface{} {
	var (
		res    interface{} = nil
		second interface{} = nil
	)

	res = ctx.GetChild(0).(antlr.ParseTree).Accept(v)

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			second = ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if reflect.TypeOf(res).Kind() == reflect.Bool && reflect.TypeOf(second).Kind() == reflect.Bool {
				res = res.(bool) && second.(bool)
			} else {
				if (reflect.TypeOf(res).Kind() == reflect.Bool || reflect.TypeOf(res).Kind() == reflect.String) &&
					(reflect.TypeOf(second).Kind() == reflect.Bool || reflect.TypeOf(second).Kind() == reflect.String) {
					res = fmt.Sprintf("%v&&%v", res, second)
				} else {
					v.addError(fmt.Sprintf("operation &&: incompatible types %v and %v", reflect.TypeOf(res).Kind(), reflect.TypeOf(second).Kind()))
					res = ""
				}
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#logicalOrExpression.
func (v *EvalVisitor) VisitLogicalOrExpression(ctx *BehaviorsGrammar.LogicalOrExpressionContext) interface{} {
	var (
		res    interface{} = nil
		second interface{} = nil
	)

	res = ctx.GetChild(0).(antlr.ParseTree).Accept(v)

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			second = ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if reflect.TypeOf(res).Kind() == reflect.Bool && reflect.TypeOf(second).Kind() == reflect.Bool {
				res = res.(bool) || second.(bool)
			} else {
				if (reflect.TypeOf(res).Kind() == reflect.Bool || reflect.TypeOf(res).Kind() == reflect.String) &&
					(reflect.TypeOf(second).Kind() == reflect.Bool || reflect.TypeOf(second).Kind() == reflect.String) {
					res = fmt.Sprintf("%v||%v", res, second)
				} else {
					v.addError(fmt.Sprintf("operation ||: incompatible types %v and %v", reflect.TypeOf(res).Kind(), reflect.TypeOf(second).Kind()))
					res = ""
				}
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#assignmentExpression.
func (v *EvalVisitor) VisitAssignmentExpression(ctx *BehaviorsGrammar.AssignmentExpressionContext) interface{} {

	if v.HasError() {
		return 0
	}

	if ctx.LogicalOrExpression() != nil {
		return ctx.LogicalOrExpression().Accept(v)
	}

	lp := ctx.UnaryExpression().Accept(v)
	tp := reflect.TypeOf(lp).Kind()
	if tp == reflect.Bool ||
		tp == reflect.Int || tp == reflect.Int8 || tp == reflect.Int16 ||
		tp == reflect.Float32 || tp == reflect.Float64 {
		v.addError(fmt.Sprintf("operation =: cannot assign to %v", lp))
		return 0
	}
	rp := ctx.AssignmentExpression().Accept(v)
	return fmt.Sprintf("%v=%v", lp, rp)
}

// Visit a parse tree produced by ExpressionParser#assignmentOperator.
func (v *EvalVisitor) VisitAssignmentOperator(ctx *BehaviorsGrammar.AssignmentOperatorContext) interface{} {
	return ctx.GetText()
}

// Visit a parse tree produced by ExpressionParser#expression.
func (v *EvalVisitor) VisitExpression(ctx *BehaviorsGrammar.ExpressionContext) interface{} {

	res := ctx.GetChild(0).(antlr.ParseTree).Accept(v)

	for i := 1; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = fmt.Sprintf("%v, %v", res, t)
			}
		}

	}

	return res
}
