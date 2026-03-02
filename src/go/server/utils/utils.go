package utils

import (
	"math"
	"os"
	"strconv"
	"strings"
)

func FileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil || os.IsExist(err)
}

// contains checks if a string is present in a slice of strings.
func Contains(s []string, str string) bool {
	for _, v := range s { // Iterate over each element
		if v == str {
			return true // Return true if a match is found
		}
	}
	return false // Return false if the loop finishes without a match
}

func IsFloat(s string) bool {
	f, err := strconv.ParseFloat(s, 64)
	return err == nil && !math.IsNaN(f) && !math.IsInf(f, 0)
}

func IsInteger(s string) bool {
	_, err := strconv.Atoi(s)
	return err == nil
}

func IsBoolean(s string) bool {
	_, err := strconv.ParseBool(strings.ToLower(s))
	return err == nil
}

func IsConstant(s string) bool {
	return IsFloat(s) || IsInteger(s) || IsBoolean(s)
}
