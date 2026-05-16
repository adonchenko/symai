package parser

import (
	"errors"
	"math"
	"reflect"

	"src/server/utils"
)

func processLT(t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {

	if t1Kind == reflect.Bool {
		t1 = utils.BoolToFloat64(t1.(bool))
	}
	if t2Kind == reflect.Bool {
		t2 = utils.BoolToFloat64(t2.(bool))
	}
	res := t1.(float64) < t2.(float64)
	return res, nil
}

func processLE(t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {

	if t1Kind == reflect.Bool {
		t1 = utils.BoolToFloat64(t1.(bool))
	}
	if t2Kind == reflect.Bool {
		t2 = utils.BoolToFloat64(t2.(bool))
	}
	res := t1.(float64) <= t2.(float64)
	return res, nil
}

func processGT(t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {

	if t1Kind == reflect.Bool {
		t1 = utils.BoolToFloat64(t1.(bool))
	}
	if t2Kind == reflect.Bool {
		t2 = utils.BoolToFloat64(t2.(bool))
	}
	res := t1.(float64) > t2.(float64)
	return res, nil
}

func processGE(t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {

	if t1Kind == reflect.Bool {
		t1 = utils.BoolToFloat64(t1.(bool))
	}
	if t2Kind == reflect.Bool {
		t2 = utils.BoolToFloat64(t2.(bool))
	}
	res := t1.(float64) >= t2.(float64)
	return res, nil
}

func processEQ(t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {

	if t1Kind == reflect.Bool {
		t1 = utils.BoolToFloat64(t1.(bool))
	}
	if t2Kind == reflect.Bool {
		t2 = utils.BoolToFloat64(t2.(bool))
	}
	res := t1.(float64) == t2.(float64)
	return res, nil
}

func processNE(t1 interface{}, t1Kind reflect.Kind,
	t2 interface{}, t2Kind reflect.Kind) (interface{}, error) {

	if t1Kind == reflect.Bool {
		t1 = utils.BoolToFloat64(t1.(bool))
	}
	if t2Kind == reflect.Bool {
		t2 = utils.BoolToFloat64(t2.(bool))
	}
	res := t1.(float64) != t2.(float64)
	return res, nil
}

func processEmbeddedFunction(fn string, arg []interface{}) (interface{}, error) {
	switch fn {
	case "sin":
		return doSin(arg)
	case "cos":
		return doCos(arg)
	case "tan":
		return doTan(arg)
	case "cotan":
		return doCotan(arg)
	case "asin":
		return doAsin(arg)
	case "acos":
		return doAcos(arg)
	case "atan":
		return doAtan(arg)
	case "acotan":
		return doAcotan(arg)
	case "log":
		return doLog(arg)
	case "lg":
		return doLg(arg)
	case "sqrt":
		return doSqrt(arg)
	case "exp":
		return doExp(arg)
	case "pow":
		return doPow(arg)
	default:
		return nil, errors.New("Unsupported function: " + fn)
	}
}

func doSin(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("sin function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("sin function requires a numeric argument")
	}
	return math.Sin(x), nil
}

func doCos(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("cos function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("cos function requires a numeric argument")
	}
	return math.Cos(x), nil
}

func doTan(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("tan function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("tan function requires a numeric argument")
	}
	return math.Tan(x), nil
}

func doCotan(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("cotan function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("cotan function requires a numeric argument")
	}
	x = math.Tan(x)
	if x == 0 {
		return 0, errors.New("cotan function is undefined for this input")
	}
	return 1 / x, nil
}

func doAsin(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("asin function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("asin function requires a numeric argument")
	}
	return math.Asin(x), nil
}

func doAcos(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("acos function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("acos function requires a numeric argument")
	}
	return math.Acos(x), nil
}

func doAtan(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("atan function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("atan function requires a numeric argument")
	}
	return math.Atan(x), nil
}

func doAcotan(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("acotan function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("acotan function requires a numeric argument")
	}
	x = math.Atan(x)
	if x == 0 {
		return 0, errors.New("acotan function is undefined for this input")
	}
	return 1 / x, nil
}

func doLog(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("log function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("log function requires a numeric argument")
	}
	return math.Log(x), nil
}

func doLg(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("lg function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("lg function requires a numeric argument")
	}
	return math.Log10(x), nil
}

func doSqrt(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("sqrt function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("sqrt function requires a numeric argument")
	}
	if x < 0 {
		return 0, errors.New("sqrt function is undefined for negative numbers")
	}
	return math.Sqrt(x), nil
}

func doExp(args []interface{}) (float64, error) {

	if len(args) != 1 {
		return 0, errors.New("exp function requires exactly one argument")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("exp function requires a numeric argument")
	}
	return math.Exp(x), nil
}

func doPow(args []interface{}) (float64, error) {

	if len(args) != 2 {
		return 0, errors.New("pow function requires exactly two arguments")
	}
	x, ok := args[0].(float64)
	if !ok {
		return 0, errors.New("pow function requires a numeric first argument")
	}
	y, ok := args[1].(float64)
	if !ok {
		return 0, errors.New("pow function requires a numeric second argument")
	}

	return math.Pow(x, y), nil
}
