package config

import (
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"src/server/utils"
	"strconv"
	"strings"

	"github.com/sirupsen/logrus"
	"gopkg.in/ini.v1"
)

type (
	SymAIConfig struct {
		SymAISection         SymAISectionConfig      `ini:"SymAI"`
		ExpressionSection    ExpressionSectionConfig `ini:"Expression"`
		FrontendSection      FrontendSectionConfig   `ini:"Frontend"`
		LoggersSection       LoggersSectionConfig    `ini:"loggers"`
		HandlersSection      LoggersSectionConfig    `ini:"handlers"`
		FormattersSection    LoggersSectionConfig    `ini:"formatters"`
		LoggersFromComfig    map[string]interface{}
		HandlersFromConfig   map[string]interface{}
		FormattersFromConfig map[string]interface{}

		Logger *logrus.Logger
	}

	LoggerConfig struct {
		LogFile  string `ini:"logfile"`
		LogLevel string `ini:"loglevel"`
	}

	SymAISectionConfig struct {
		TempDir        string `ini:"tempdir"`
		Host           string `ini:"host"`
		Port           int    `ini:"port"`
		ExpressionHost string `ini:"expression_host"`
		ExpressionPort int    `ini:"expression_port"`
		AI             string `ini:"ai"`
		ReenterCount   int    `ini:"reenter_count"`
		Debug          string `ini:"debug"`
	}

	ExpressionSectionConfig struct {
		Host             string `ini:"host"`
		Port             int    `ini:"port"`
		ExpressionSolver string `ini:"expression_solver"`
		SolverMaxModels  int    `ini:"solver_max_models"`
	}

	FrontendSectionConfig struct {
		Host          string `ini:"host"`
		Port          int    `ini:"port"`
		SymAICoreHost string `ini:"symaicore_host"`
		SymAICorePort int    `ini:"symaicore_port"`
		Resources     string `ini:"resources"`
	}

	LoggersSectionConfig struct {
		Keys string `ini:"keys"`
	}

	LoggerConfigStruct struct {
		Level     string `ini:"level"`
		Handlers  string `ini:"handlers"`
		Qualname  string `ini:"qualname"`
		Propagate int    `ini:"propagate"`
	}

	HandlerConfigStruct struct {
		Class       string `ini:"class"`
		Level       string `ini:"level"`
		Formatter   string `ini:"formatter"`
		Args        string `ini:"args"`
		Interval    string `ini:"interval"`
		BackupCount int    `ini:"backupcount"`
	}

	FormatterConfigStruct struct {
		Format string `ini:"format"`
	}

	// WriterHook is a hook that writes logs of specified levels to an io.Writer with a custom formatter
	WriterHook struct {
		Writer    io.Writer
		Formatter logrus.Formatter
		LogLevels []logrus.Level
	}
)

var (
	Config SymAIConfig
)

// Levels returns the levels for which the hook is fired.
func (hook *WriterHook) Levels() []logrus.Level {
	return hook.LogLevels
}

// Fire writes the log entry to the specified writer using the custom formatter.
func (hook *WriterHook) Fire(entry *logrus.Entry) error {
	// Use the hook's specific formatter to format the entry
	line, err := hook.Formatter.Format(entry)
	if err != nil {
		return err
	}
	_, err = hook.Writer.Write(line)
	return err
}

func Create(path string) (cfg *SymAIConfig, err error) {
	err = nil
	if !utils.FileExists(path) {
		Config.InitDefaults()
		dir := filepath.Dir(path)
		if _, err = os.Stat(dir); os.IsNotExist(err) {
			err = os.MkdirAll(dir, 0755) // 0755 provides read/write/execute for owner, read/execute for group/others
		}
		if err == nil {
			err = Save(&Config, path)
		}
		if err == nil {
			cfg = &Config
		}
	} else {
		cfg, err = Load(path)
	}
	return cfg, err
}

func Load(path string) (*SymAIConfig, error) {
	var (
		err error = nil
	)
	ext := filepath.Ext(path)

	if strings.ToLower(ext) == ".ini" {
		inidata, e := ini.Load(path)
		if e != nil {
			err = e
		} else {
			err = inidata.MapTo(&Config)
			Config.FormattersFromConfig = make(map[string]interface{})
			Config.LoggersFromComfig = make(map[string]interface{})
			Config.HandlersFromConfig = make(map[string]interface{})
			if err == nil {
				sects := inidata.Sections()
				for _, s := range sects {
					nm := s.Name()
					sp := strings.Split(nm, "_")
					if len(sp) > 1 {
						switch sp[0] {
						case "logger":
							nm = nm[len(sp[0])+1:]
							lc := LoggerConfigStruct{}
							err := inidata.Section(s.Name()).MapTo(&lc)
							if err != nil {
								return nil, err
							}
							Config.LoggersFromComfig[nm] = lc
						case "formatter":
							nm = nm[len(sp[0])+1:]
							lc := FormatterConfigStruct{}
							err := inidata.Section(s.Name()).MapTo(&lc)
							if err != nil {
								return nil, err
							}
							Config.FormattersFromConfig[nm] = lc
						case "handler":
							nm = nm[len(sp[0])+1:]
							lc := HandlerConfigStruct{}
							err := inidata.Section(s.Name()).MapTo(&lc)
							if err != nil {
								return nil, err
							}
							Config.HandlersFromConfig[nm] = lc
						default:
						}
					}
				}
			}
		}
	} else {
		return nil, errors.New("unknown configuration file extension")
	}
	return &Config, err
}

func (cfg *SymAIConfig) InitDefaults() {
	var (
		lgr   LoggerConfigStruct    = LoggerConfigStruct{}
		fmtr  FormatterConfigStruct = FormatterConfigStruct{}
		hlndr HandlerConfigStruct   = HandlerConfigStruct{}
	)
	// SymAI
	cfg.SymAISection.TempDir = "/tmpdir/temp"
	cfg.SymAISection.Host = "localhost"
	cfg.SymAISection.Port = 12345
	cfg.SymAISection.ExpressionHost = "localhost"
	cfg.SymAISection.ExpressionPort = 8080
	cfg.SymAISection.AI = "False"
	cfg.SymAISection.ReenterCount = 1
	cfg.SymAISection.Debug = "True"
	// Expression
	cfg.ExpressionSection.Host = "localhost"
	cfg.ExpressionSection.Port = 8080
	cfg.ExpressionSection.ExpressionSolver = "Z3"
	cfg.ExpressionSection.SolverMaxModels = 10
	// Frontend
	cfg.FrontendSection.Host = "localhost"
	cfg.FrontendSection.Port = 8000
	cfg.FrontendSection.SymAICoreHost = "localhost"
	cfg.FrontendSection.SymAICorePort = 12345
	cfg.FrontendSection.Resources = "/app/resources"
	// Loggers
	cfg.LoggersSection.Keys = "root, expression, symaicore, frontend"
	// Handlers
	cfg.HandlersSection.Keys = "consoleHandler,file,file_symaicore, file_frontend"
	// Formatters
	cfg.FormattersSection.Keys = "simpleFormatter"
	// Loggers descriptions
	cfg.LoggersFromComfig = make(map[string]interface{})
	lgr.Handlers = "consoleHandler"
	lgr.Level = "DEBUG"
	cfg.LoggersFromComfig["root"] = lgr
	lgr.Handlers = "consoleHandler,file"
	lgr.Level = "DEBUG"
	lgr.Qualname = "expression"
	lgr.Propagate = 0
	cfg.LoggersFromComfig["expression"] = lgr
	lgr.Handlers = "consoleHandler,file_symaicore"
	lgr.Level = "DEBUG"
	lgr.Qualname = "symaicore"
	lgr.Propagate = 0
	cfg.LoggersFromComfig["symaicore"] = lgr
	lgr.Handlers = "consoleHandler,file"
	lgr.Level = "DEBUG"
	lgr.Qualname = "frontend"
	lgr.Propagate = 0
	cfg.LoggersFromComfig["frontend"] = lgr
	// Handlers descriptions
	cfg.HandlersFromConfig = make(map[string]interface{})
	hlndr.Level = "DEBUG"
	hlndr.Class = "StreamHandler"
	hlndr.Formatter = "simpleFormatter"
	hlndr.Args = "(sys.stdout,)"
	cfg.HandlersFromConfig["consoleHandler"] = hlndr
	hlndr.Level = "DEBUG"
	hlndr.Class = "handlers.TimedRotatingFileHandler"
	hlndr.Formatter = "simpleFormatter"
	hlndr.Interval = "midnight"
	hlndr.BackupCount = 5
	hlndr.Args = "('/logdir/expression.log',)"
	cfg.HandlersFromConfig["file"] = hlndr
	hlndr.Level = "DEBUG"
	hlndr.Class = "handlers.TimedRotatingFileHandler"
	hlndr.Formatter = "simpleFormatter"
	hlndr.Interval = "midnight"
	hlndr.BackupCount = 5
	hlndr.Args = "('/logdir/symaicore.log',)"
	cfg.HandlersFromConfig["file_symaicore"] = hlndr
	hlndr.Level = "DEBUG"
	hlndr.Class = "handlers.TimedRotatingFileHandler"
	hlndr.Formatter = "simpleFormatter"
	hlndr.Interval = "midnight"
	hlndr.BackupCount = 5
	hlndr.Args = "('/logdir/frontend.log',)"
	cfg.HandlersFromConfig["file_frontend"] = hlndr
	// Formatters descriptions
	cfg.FormattersFromConfig = make(map[string]interface{})
	fmtr.Format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
	cfg.FormattersFromConfig["simpleFormatter"] = fmtr
}

func Save(c *SymAIConfig, path string) error {
	ext := filepath.Ext(path)
	if strings.ToLower(ext) == ".ini" {
		cfg := ini.Empty()
		sec, err := cfg.NewSection("SymAI")
		if err != nil {
			return err
		}
		sec.Key("debug").SetValue(c.SymAISection.Debug)
		sec.Key("host").SetValue(c.SymAISection.Host)
		sec.Key("expression_host").SetValue(c.SymAISection.ExpressionHost)
		sec.Key("tempdir").SetValue(c.SymAISection.TempDir)
		sec.Key("ai").SetValue(c.SymAISection.AI)
		sec.Key("port").SetValue(strconv.Itoa(c.SymAISection.Port))
		sec.Key("expressioin_port").SetValue(strconv.Itoa(c.SymAISection.ExpressionPort))
		sec.Key("reenter_count").SetValue(strconv.Itoa(c.SymAISection.ReenterCount))

		sec, err = cfg.NewSection("Expression")
		if err != nil {
			return err
		}
		sec.Key("host").SetValue(c.ExpressionSection.Host)
		sec.Key("expression_solver").SetValue(c.ExpressionSection.ExpressionSolver)
		sec.Key("solver_max_models").SetValue(strconv.Itoa(c.ExpressionSection.SolverMaxModels))
		sec.Key("port").SetValue(strconv.Itoa(c.ExpressionSection.Port))

		sec, err = cfg.NewSection("Frontend")
		if err != nil {
			return err
		}
		sec.Key("host").SetValue(c.FrontendSection.Host)
		sec.Key("symaicore_host").SetValue(c.FrontendSection.SymAICoreHost)
		sec.Key("resources").SetValue(c.FrontendSection.Resources)
		sec.Key("port").SetValue(strconv.Itoa(c.FrontendSection.Port))
		sec.Key("symaicore_port").SetValue(strconv.Itoa(c.FrontendSection.SymAICorePort))

		sec, err = cfg.NewSection("loggers")
		if err != nil {
			return err
		}
		sec.Key("keys").SetValue(c.LoggersSection.Keys)

		sec, err = cfg.NewSection("handlers")
		if err != nil {
			return err
		}
		sec.Key("keys").SetValue(c.HandlersSection.Keys)

		sec, err = cfg.NewSection("formatters")
		if err != nil {
			return err
		}
		sec.Key("keys").SetValue(c.FormattersSection.Keys)

		for k, v := range c.LoggersFromComfig {
			sec, err := cfg.NewSection("logger_" + k)
			if err != nil {
				return err
			}

			t := v.(LoggerConfigStruct)
			sec.Key("level").SetValue(t.Level)
			sec.Key("handlers").SetValue(t.Handlers)
			sec.Key("qualname").SetValue(t.Qualname)
			sec.Key("propagate").SetValue(strconv.Itoa(t.Propagate))
		}
		for k, v := range c.FormattersFromConfig {
			sec, err := cfg.NewSection("formatter_" + k)
			if err != nil {
				return err
			}
			t := v.(FormatterConfigStruct)
			sec.Key("format").SetValue(t.Format)
		}
		for k, v := range c.HandlersFromConfig {
			sec, err := cfg.NewSection("handler_" + k)
			if err != nil {
				return err
			}
			t := v.(HandlerConfigStruct)
			sec.Key("level").SetValue(t.Level)
			sec.Key("args").SetValue(t.Args)
			sec.Key("class").SetValue(t.Class)
			sec.Key("formatter").SetValue(t.Formatter)
			sec.Key("backupcount").SetValue(strconv.Itoa(t.BackupCount))
			sec.Key("interval").SetValue(t.Interval)
		}

		return cfg.SaveTo(path)
	}
	return errors.New("unknown configuration file extension")
}

func InitLogger(loggerName string) error {
	var err error = nil

	_, err = Config.InitLogger(loggerName)

	return err
}

func (cfg *SymAIConfig) getLoggerConfig(loggername string) (LoggerConfigStruct, error) {
	var (
		err error = nil
		r         = LoggerConfigStruct{}
	)
	for nm, v := range cfg.LoggersFromComfig {
		if strings.TrimSpace(nm) == strings.TrimSpace(loggername) {
			r = v.(LoggerConfigStruct)
			return r, nil
		}
	}
	err = fmt.Errorf("unknown logger name '%s'", loggername)
	return r, err
}

func (cfg *SymAIConfig) getHandlerConfig(handlername string) (HandlerConfigStruct, error) {
	var (
		err error = nil
		r         = HandlerConfigStruct{}
	)
	for nm, v := range cfg.HandlersFromConfig {
		if strings.TrimSpace(nm) == strings.TrimSpace(handlername) {
			r = v.(HandlerConfigStruct)
			return r, nil
		}
	}
	err = fmt.Errorf("unknown handler name '%s'", handlername)
	return r, err
}

func (cfg *SymAIConfig) getFormatterConfig(formattername string) (FormatterConfigStruct, error) {
	var (
		err error = nil
		r         = FormatterConfigStruct{}
	)
	for nm, v := range cfg.FormattersFromConfig {
		if strings.TrimSpace(nm) == strings.TrimSpace(formattername) {
			r = v.(FormatterConfigStruct)
			return r, nil
		}
	}
	err = fmt.Errorf("unknown formatter name '%s'", formattername)
	return r, err
}

func (cfg *SymAIConfig) qSetLogReportCaller(f string) error {
	if strings.Index(f, "%function%") > 0 ||
		strings.Index(f, "%line%") > 0 ||
		strings.Index(f, "%file%") > 0 ||
		strings.Index(f, "%(filename)s") > 0 ||
		strings.Index(f, "%(lineno)s") > 0 ||
		strings.Index(f, "%(funcName)s") > 0 {
		cfg.Logger.SetReportCaller(true)
	}
	return nil
}

func (cfg *SymAIConfig) InitLogger(name string) (*logrus.Logger, error) {
	var (
		err       error     = nil
		lgr                 = LoggerConfigStruct{Level: ""}
		hndlr               = HandlerConfigStruct{}
		fmtr                = FormatterConfigStruct{}
		lgrLevels           = logrus.AllLevels
		hlvls               = logrus.AllLevels
		writer    io.Writer = nil
	)

	cfg.Logger = logrus.New()
	cfg.Logger.SetOutput(io.Discard)
	cfg.Logger.SetLevel(logrus.DebugLevel)

	lgr, err = cfg.getLoggerConfig(name)
	if err == nil {
		if lgr.Level != "" {
			lgrLevels, err = getAllowedLogLevels(lgr.Level)
		}
		if err == nil {
			hs := strings.Split(lgr.Handlers, ",")
			for i, s := range hs {
				hs[i] = strings.TrimSpace(s)
				hndlr, err = cfg.getHandlerConfig(hs[i])
				if err == nil {
					hlvls, err = getAllowedLogLevels(hndlr.Level)
					if err != nil || len(hlvls) < 1 {
						err = nil
						hlvls = lgrLevels
					}
					fmtr, err = cfg.getFormatterConfig(hndlr.Formatter)
					if err == nil {
						if fmtr.Format == "" {
							err = fmt.Errorf("incorrect formatter")
						} else {
							if hndlr.Class == "NullHandler" {
								continue // Just skip a NullHandler
							} else {
								if hndlr.Class == "StreamHandler" {
									// StreamHandler
									if len(hndlr.Args) < 2 {
										continue
									}
									args := strings.Split(hndlr.Args[1:len(hndlr.Args)-1], ",")
									for _, a := range args {
										a = strings.TrimSpace(a)
										if len(a) > 0 {
											if a == "ostream" || a == "stdout" || a == "sys.stdout" || strings.ToLower(a) == "os.stdout" {
												writer = os.Stdout
											} else {
												if a == "errstream" || a == "stderr" || a == "sys.stderr" || strings.ToLower(a) == "os.stderr" {
													writer = os.Stderr
												} else {
													err = fmt.Errorf("unknown stream name '%s'", a)
													break
												}
											}
											_ = cfg.qSetLogReportCaller(fmtr.Format)
											cfg.Logger.AddHook(&WriterHook{
												Writer: writer,
												Formatter: &Formatter{
													Name:      name,
													LogFormat: fmtr.Format,
												},
												LogLevels: hlvls, // Log requested levels to desired output
											})
										} else {
											break
										}
									}
								} else {
									if hndlr.Class == "FileHandler" || hndlr.Class == "WatchedFileHandler" ||
										hndlr.Class == "BaseRotatingHandler" || hndlr.Class == "RotatingFileHandler" ||
										hndlr.Class == "TimedRotatingFileHandler" ||
										hndlr.Class == "handlers.FileHandler" || hndlr.Class == "handlers.WatchedFileHandler" ||
										hndlr.Class == "handlers.BaseRotatingHandler" || hndlr.Class == "handlers.RotatingFileHandler" ||
										hndlr.Class == "handlers.TimedRotatingFileHandler" {

										if len(hndlr.Args) < 2 {
											continue
										}
										args := strings.Split(hndlr.Args[1:len(hndlr.Args)-1], ",")
										for _, a := range args {
											a = strings.TrimSpace(a)
											if len(a) > 0 {
												i = len(a)
												if i > 2 && ((a[0:1] == "'" && a[i-1:i] == "'") || (a[0:1] == "\"" && a[i-1:i] == "\"")) {
													a = a[1 : i-1]
												}
												dir := filepath.Dir(a)
												if _, err := os.Stat(dir); os.IsNotExist(err) {
													err = os.MkdirAll(dir, 0755) // 0755 provides read/write/execute for owner, read/execute for group/others
													if err != nil {
														break
													}
												} else if err != nil {
													break
												}
												writer, err := os.OpenFile(a, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
												if err != nil {
													break
												}
												_ = cfg.qSetLogReportCaller(fmtr.Format)
												cfg.Logger.AddHook(&WriterHook{
													Writer: writer,
													Formatter: &Formatter{
														Name:      name,
														LogFormat: fmtr.Format,
													},
													LogLevels: hlvls, // Log requested levels to desired output
												})
											}
										}
									} else {
										// Other handlers
										err = fmt.Errorf("unknown or not implemented handler name '%s'", hndlr.Class)
									}
								}
							}
						}
					}
				}
				if err != nil {
					break
				}
			}
		}
	}

	return cfg.Logger, err
}

func getAllowedLogLevels(loglevel string) ([]logrus.Level, error) {
	var (
		err error        = nil
		lvl logrus.Level = logrus.InfoLevel
	)

	if strings.TrimSpace(loglevel) == "" {
		loglevel = "trace"
	}
	allowedLevels := make([]logrus.Level, 0)

	lvl, err = GetLogLevel(loglevel)
	if err == nil {
		for _, v := range logrus.AllLevels {
			allowedLevels = append(allowedLevels, v)
			if v == lvl {
				break
			}
		}
	}

	return allowedLevels, err
}

func Validate(config *SymAIConfig) error {
	var err error

	return err
}

func ValidateLoggerSettings(cfg *LoggerConfig) error {
	var err error = nil

	err = ValidateLogLevel(cfg.LogLevel)

	return err
}

func GetLogLevel(loglevel string) (logrus.Level, error) {
	loglevel = strings.TrimSpace(loglevel)

	if loglevel == "" {
		loglevel = "trace"
	}

	if strings.ToLower(loglevel) == "critical" {
		loglevel = "fatal"
	}
	lvl, err := logrus.ParseLevel(loglevel)
	return lvl, err
}

func ValidateLogLevel(loglevel string) error {
	_, err := GetLogLevel(loglevel)
	return err
}
