package parser

import (
	"reflect"

	"github.com/antlr4-go/antlr/v4"

	"src/server/BehaviorsGrammar"
)

// A complete Visitor for a parse tree produced by ActionsGrammarParser.
type (
	BehaviorBody struct {
		Terminals []string
	}

	BehaviorsVisitor struct {
		EQExtractorVisitor

		// Behaviors related staff
		Terminals map[string]BehaviorBody
		cur_terms []string
	}
)

func (v *BehaviorBody) GetText() string {
	res := ""
	for i := 0; i < len(v.Terminals); i++ {
		res = res + v.Terminals[i]
	}
	return res
}

func NewBehaviorBody() *BehaviorBody {
	return &BehaviorBody{
		Terminals: make([]string, 0),
	}
}

func NewBehaviorsVisitor() *BehaviorsVisitor {
	return &BehaviorsVisitor{
		EQExtractorVisitor: *NewEQExtractorVisitor(),
		Terminals: make(map[string]BehaviorBody, 0),
	}
}

func (v *BehaviorsVisitor) GetBehaviors() map[string]BehaviorBody {
	return v.Terminals
}

func (v *BehaviorsVisitor) SetBehaviors(t map[string]BehaviorBody) {
	v.Terminals = t
}

// Visit a parse tree produced by ExpressionGrammarParser#behaviors.
func (v *BehaviorsVisitor) VisitBehaviors(ctx *BehaviorsGrammar.BehaviorsContext) interface{} {
	res := ""
	v.Terminals = make(map[string]BehaviorBody, 0)
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

// Visit a parse tree produced by ExpressionGrammarParser#system_of_eqs.
func (v *BehaviorsVisitor) VisitSystem_of_eqs(ctx *BehaviorsGrammar.System_of_eqsContext) interface{} {
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

// Visit a parse tree produced by ExpressionGrammarParser#eqs.
func (v *BehaviorsVisitor) VisitEqs(ctx *BehaviorsGrammar.EqsContext) interface{} {
	res := ""
	nm := ""
	v.cur_terms = make([]string, 0)
	i := 0
	t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
	if t != nil {
		nm = t.(string)
		res = nm + "="
		i = i + 2
		if len(nm) > 1 && nm[:1] == "!" {
			nm = nm[1:]
			v.cur_terms = append(v.cur_terms, "!")
		}
	}
	t = ctx.GetChild(i).(antlr.ParseTree).Accept(v)
	if t != nil {
		res = res + t.(string)
		i = i + 1
		_, ok := v.Terminals[nm]
		if ok {
			v.addError("Duplicated behavior name '" + nm + "'")
		} else {
			v.Terminals[nm] = BehaviorBody{
				Terminals: v.cur_terms,
			}
		}
	}
	return res
}

// Visit a parse tree produced by ExpressionGrammarParser#prim_name.
func (v *BehaviorsVisitor) VisitPrim_name(ctx *BehaviorsGrammar.Prim_nameContext) interface{} {
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

// Visit a parse tree produced by ExpressionGrammarParser#comp_name.
func (v *BehaviorsVisitor) VisitComp_name(ctx *BehaviorsGrammar.Comp_nameContext) interface{} {
	res := ""
	if reflect.TypeOf(ctx.GetChild(0)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) &&
		ctx.GetChild(0).(*antlr.TerminalNodeImpl).GetText() == "(" {
		bck := v.cur_terms
		v.cur_terms = make([]string, 0)
		t := ctx.GetChild(1).(antlr.ParseTree).Accept(v)
		if t != nil {
			nm := "(" + t.(string) + ")"
			res = res + nm
			_, ok := v.Terminals[nm]
			if !ok {
				v.Terminals[nm] = BehaviorBody{
					Terminals: v.cur_terms,
				}
			}
		}
		v.cur_terms = bck
	} else {
		t := ctx.GetChild(0).(antlr.ParseTree).Accept(v)
		if t != nil {
			res = res + t.(string)
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionGrammarParser#postfix_item.
func (v *BehaviorsVisitor) VisitPostfix_item(ctx *BehaviorsGrammar.Postfix_itemContext) interface{} {
	res := ""
	
	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
			v.cur_terms = append(v.cur_terms, op)
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
				v.cur_terms = append(v.cur_terms, t.(string))
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionGrammarParser#items_list.
func (v *BehaviorsVisitor) VisitItems_list(ctx *BehaviorsGrammar.Items_listContext) interface{} {
	res := ""

	for i := 0; i < ctx.GetChildCount(); i++ {
		if reflect.TypeOf(ctx.GetChild(i)) == reflect.TypeOf((*antlr.TerminalNodeImpl)(nil)) {
			op := ctx.GetChild(i).(*antlr.TerminalNodeImpl).GetText()
			res = res + op
			v.cur_terms = append(v.cur_terms, op)
		} else {
			t := ctx.GetChild(i).(antlr.ParseTree).Accept(v)
			if t != nil {
				res = res + t.(string)
			}
		}
	}

	return res
}

// Visit a parse tree produced by ExpressionGrammarParser#par_item.
func (v *BehaviorsVisitor) VisitPar_item(ctx *BehaviorsGrammar.Par_itemContext) interface{} {
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
