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
type EQExtractorVisitor struct {
	BehaviorsGrammar.BaseBehaviorsGrammarVisitor
	ErrorProcessing

	// Expression staff
	hasTrigonometric bool
	hasNonLinear     bool
	varList          []string
	substitutionMap  map[string]string
	ExtractEQ        bool
	cvals            map[string]interface{}
	vals             map[string]string
	vnames           []string // list of variables to remove from the result when they are placed in 'vnames' list
}

func NewEQExtractorVisitor(args ...interface{}) *EQExtractorVisitor {
	return &EQExtractorVisitor{
		hasTrigonometric: false,
		hasNonLinear:     false,
		varList:          []string{},
		substitutionMap:  map[string]string{},
		ErrorProcessing:  *NewErrorProcessing(),
		ExtractEQ: func() bool {
			res := false
			if len(args) > 0 {
				for i := 0; i < len(args); i++ {
					if reflect.TypeOf(args[i]) == reflect.TypeOf(true) {
						res = res || args[i].(bool)
					}
				}
			}
			return res
		}(),
		vnames: func() []string {
			res := make([]string, 0)
			if len(args) > 0 {
				for i := 0; i < len(args); i++ {
					if reflect.TypeOf(args[i]) == reflect.TypeOf(res) {
						res = args[i].([]string)
					}
				}
			}
			return res
		}(),
		cvals: make(map[string]interface{}, 0),
		vals:  make(map[string]string, 0),
	}
}

func (v *EQExtractorVisitor) GetCvals() map[string]interface{} {
	return v.cvals
}

func (v *EQExtractorVisitor) SetCvals(m map[string]interface{}) {
	v.cvals = m
}

func (v *EQExtractorVisitor) GetVals() map[string]string {
	return v.vals
}

func (v *EQExtractorVisitor) SetVals(m map[string]string) {
	v.vals = m
}

func (v *EQExtractorVisitor) GetSubstitutionMap() map[string]string {
	return v.substitutionMap
}

func (v *EQExtractorVisitor) SetSubstitutionMap(m map[string]string) {
	v.substitutionMap = m
}

func (v *EQExtractorVisitor) HasTrigonometric() bool {
	return v.hasTrigonometric
}

func (v *EQExtractorVisitor) HasNonLinear() bool {
	return v.hasNonLinear
}

func (v *EQExtractorVisitor) GetVarList() []string {
	return v.varList
}

func (v *EQExtractorVisitor) SetVarList(varList []string) {
	v.varList = varList
}

func (v *EQExtractorVisitor) IsInVarList(s string) bool {
	b := false
	for _, r := range v.varList {
		if r == s {
			b = true
			break
		}
	}
	return b
}

func (v *EQExtractorVisitor) IsExtractEQ() bool {
	return v.ExtractEQ
}

func (v *EQExtractorVisitor) SetExtractEQ(extract bool) {
	v.ExtractEQ = extract
}

// Visit a parse tree produced by ExpressionParser#primaryExpression.
func (v *EQExtractorVisitor) VisitPrimaryExpression(ctx *BehaviorsGrammar.PrimaryExpressionContext) interface{} {

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
func (v *EQExtractorVisitor) VisitPostfixExpression(ctx *BehaviorsGrammar.PostfixExpressionContext) interface{} {
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
		// TODO: Here we can place remove var statement as well.
	}

	return s
}

// Visit a parse tree produced by ExpressionParser#argumentExpressionList.
func (v *EQExtractorVisitor) VisitArgumentExpressionList(ctx *BehaviorsGrammar.ArgumentExpressionListContext) interface{} {
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
func (v *EQExtractorVisitor) VisitUnaryExpression(ctx *BehaviorsGrammar.UnaryExpressionContext) interface{} {
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
func (v *EQExtractorVisitor) VisitUnaryOperator(ctx *BehaviorsGrammar.UnaryOperatorContext) interface{} {
	res := ctx.GetText()
	return res
}

// Visit a parse tree produced by ExpressionParser#multiplicativeExpression.
func (v *EQExtractorVisitor) VisitMultiplicativeExpression(ctx *BehaviorsGrammar.MultiplicativeExpressionContext) interface{} {
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
func (v *EQExtractorVisitor) VisitAdditiveExpression(ctx *BehaviorsGrammar.AdditiveExpressionContext) interface{} {
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
func (v *EQExtractorVisitor) VisitRelationalExpression(ctx *BehaviorsGrammar.RelationalExpressionContext) interface{} {
	res := ""
	first := ""
	second := ""
	op := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			if len(op) > 0 && len(first) > 0 && len(second) > 0 {
				res = v.QExtractEQ(first, second, op, res)
			}
			op = ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil && len(t.(string)) > 0 {
				if len(first) == 0 {
					first = t.(string)
				} else {
					second = first
					first = t.(string)
				}
			}
		}
	}

	if len(first) > 0 {
		if len(second) > 0 {
			res = v.QExtractEQ(first, second, op, res)
		} else {
			res = first
		}
	}

	return res
}

func (v *EQExtractorVisitor) QExtractEQ(first string, second string, op string, res string) string {
	// Adding the result. Here we also should place checkking for
	// equality op to == and ExtractEQ flag to select concrete values
	is_add := true

	if v.ExtractEQ && op == "==" {
		b := false
		if utils.IsConstant(first) && utils.IsConstant(second) {
			b = true
		} else {
			if v.IsInVarList(second) && utils.IsConstant(first) {
				b = true
			} else if v.IsInVarList(first) && utils.IsConstant(second) {
				b = true
			}
		}
		if b {
			is_add = false
			if v.IsInVarList(second) {
				f, err := strconv.ParseFloat(first, 64)
				if err == nil {
					v.cvals[second] = f
				} else {
					v.vals[second] = first
				}
			} else {
				if v.IsInVarList(first) {
					f, err := strconv.ParseFloat(second, 64)
					if err == nil {
						v.cvals[first] = f
					} else {
						v.vals[first] = second
					}
				} else {
					// both are constants, so we can calculate the result and place it in res
					f1, err1 := strconv.ParseFloat(first, 64)
					f2, err2 := strconv.ParseFloat(second, 64)
					if len(res) > 0 {
						res = res + "&&"
					}
					if err1 == nil && err2 == nil {
						res = res + strconv.FormatBool(f1 == f2)
					} else {
						res = res + strconv.FormatBool(first == second)
					}
				}
			}
		} else {
			if v.IsInVarList(second) {
				is_add = false
				v.vals[second] = first
				// second -> vals, first is expression
			} else {
				if v.IsInVarList(first) {
					is_add = false
					v.vals[first] = second
					// first -> vals, second is expression
				}
			}
		}
	}

	if is_add {
		if len(res) > 0 {
			res = res + "&&"
		}

		res = res + second + op + first
	}
	return res
}

// Visit a parse tree produced by ExpressionParser#equalityExpression.
func (v *EQExtractorVisitor) VisitEqualityExpression(ctx *BehaviorsGrammar.EqualityExpressionContext) interface{} {
	res := ""
	first := ""
	second := ""
	op := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			if len(op) > 0 && len(first) > 0 && len(second) > 0 {
				res = v.QExtractEQ(first, second, op, res)
			}
			op = ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil && len(t.(string)) > 0 {
				if len(first) == 0 {
					first = t.(string)
				} else {
					second = first
					first = t.(string)
				}
			}
		}
	}

	if len(first) > 0 {
		if len(second) > 0 {
			res = v.QExtractEQ(first, second, op, res)
		} else {
			res = first
		}
	}

	return res
}

func (v *EQExtractorVisitor) IsProcessExtractByVar() bool {
	is_extract := false
	if len(v.vnames) > 0 && len(v.GetVarList()) > 0 {
		for _, nm := range v.vnames {
			if v.IsInVarList(nm) {
				is_extract = true
				break
			}
		}
	}
	return is_extract
}

func (v *EQExtractorVisitor) QAppend(res string, app interface{}, op string) string {
	is_skip := false
	if app != nil && len(app.(string)) > 0 {
		if v.IsProcessExtractByVar() {
			p, _ := InitParser(app.(string))
			visitor := NewEQExtractorVisitor()
			tr := p.Expression()
			s := tr.Accept(visitor)

			if strings.Contains(s.(string), "&&") || strings.Contains(s.(string), "||") {
				p1, _ := InitParser(s.(string))
				visitor1 := NewEQExtractorVisitor(v.vnames, v.ExtractEQ)
				tr1 := p1.Expression()
				s1 := tr1.Accept(visitor1)
				app = s1
				p, _ = InitParser(app.(string))
				visitor = NewEQExtractorVisitor()
				tr = p.Expression()
				tr.Accept(visitor)
			}
			for _, nm := range v.vnames {
				if visitor.IsInVarList(nm) {
					is_skip = true
					break
				}
			}
		}
		if !is_skip {
			if len(res) > 0 {
				res = res + op
			}
			res = res + app.(string)
		}
	}
	return res
}

// Visit a parse tree produced by ExpressionParser#logicalAndExpression.
func (v *EQExtractorVisitor) VisitLogicalAndExpression(ctx *BehaviorsGrammar.LogicalAndExpressionContext) interface{} {
	res := ""
	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			res = v.QAppend(res, t, "&&")
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#logicalOrExpression.
func (v *EQExtractorVisitor) VisitLogicalOrExpression(ctx *BehaviorsGrammar.LogicalOrExpressionContext) interface{} {
	res := ""
	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) != reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			res = v.QAppend(res, t, "||")
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionParser#assignmentExpression.
func (v *EQExtractorVisitor) VisitAssignmentExpression(ctx *BehaviorsGrammar.AssignmentExpressionContext) interface{} {
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
func (v *EQExtractorVisitor) VisitAssignmentOperator(ctx *BehaviorsGrammar.AssignmentOperatorContext) interface{} {
	return ctx.GetText()
}

// Visit a parse tree produced by ExpressionParser#expression.
func (v *EQExtractorVisitor) VisitExpression(ctx *BehaviorsGrammar.ExpressionContext) interface{} {
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
