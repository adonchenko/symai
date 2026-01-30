package config

// Package easy allows to easily format output of Logrus logger

import (
	"strconv"
	"strings"
	"time"

	"github.com/sirupsen/logrus"
)

const (
	// Default log format will output [INFO]: 2006-01-02T15:04:05Z07:00 - Log message
	defaultLogFormat       = "[%lvl%]: %time% - %msg%"
	defaultTimestampFormat = time.RFC3339
)

// Formatter implements logrus.Formatter interface.
type Formatter struct {
	// Logger's name
	Name string
	// Timestamp format
	TimestampFormat string
	// Available standard keys: time, msg, lvl, function, file, line
	// Also can include custom fields but limited to strings.
	// All fields need to be wrapped inside %% i.e. %time% %msg%
	LogFormat string
}

// Format building log message.
func (f *Formatter) Format(entry *logrus.Entry) ([]byte, error) {
	output := f.LogFormat
	if output == "" {
		output = defaultLogFormat
	}

	timestampFormat := f.TimestampFormat
	if timestampFormat == "" {
		timestampFormat = defaultTimestampFormat
	}

	output = strings.Replace(output, "%name%", f.Name, 1)
	output = strings.Replace(output, "%(name)s", f.Name, 1)

	output = strings.Replace(output, "%time%", entry.Time.Format(timestampFormat), 1)
	output = strings.Replace(output, "%(time)s", entry.Time.Format(timestampFormat), 1)
	output = strings.Replace(output, "%(asctime)s", entry.Time.Format(timestampFormat), 1)

	output = strings.Replace(output, "%msg%", entry.Message, 1)
	output = strings.Replace(output, "%(message)s", entry.Message, 1)

	if entry.Caller != nil {
		output = strings.Replace(output, "%function%", entry.Caller.Func.Name(), 1)
		output = strings.Replace(output, "%(funcName)s", entry.Caller.Func.Name(), 1)
		output = strings.Replace(output, "%line%", strconv.Itoa(entry.Caller.Line), 1)
		output = strings.Replace(output, "%(lineno)s", strconv.Itoa(entry.Caller.Line), 1)
		output = strings.Replace(output, "%file%", entry.Caller.File, 1)
		output = strings.Replace(output, "%(filename)s", entry.Caller.File, 1)
	}

	level := strings.ToUpper(entry.Level.String())
	output = strings.Replace(output, "%lvl%", level, 1)
	output = strings.Replace(output, "%(levelname)s", level, 1)

	for k, val := range entry.Data {
		switch v := val.(type) {
		case string:
			output = strings.Replace(output, "%"+k+"%", v, 1)
		case int:
			s := strconv.Itoa(v)
			output = strings.Replace(output, "%"+k+"%", s, 1)
		case bool:
			s := strconv.FormatBool(v)
			output = strings.Replace(output, "%"+k+"%", s, 1)
		}
	}
	output = output + "\n"
	return []byte(output), nil
}
