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
		HTTPConfigsSection   HTTPConfigNamesStruct   `ini:"httpconfigs"`
		WSSConfigsSection    WSSConfigNamesStruct    `ini:"wssconfigs"`
		LoggersFromComfig    map[string]interface{}
		HandlersFromConfig   map[string]interface{}
		FormattersFromConfig map[string]interface{}

		WSSConfigsFromConfig  map[string]interface{}
		HTTPConfigsFromConfig map[string]interface{}
		Logger                *logrus.Logger
		StopCh                chan os.Signal
	}

	LoggerConfig struct {
		LogFile  string `ini:"logfile"`
		LogLevel string `ini:"loglevel"`
	}

	SymAISectionConfig struct {
		TempDir              string `ini:"tempdir"`
		HostConfig           string `ini:"hostconfig"`
		WSSHostConfig        string `ini:"wss_hostconfig"`
		Host                 string `ini:"host"`
		Port                 int    `ini:"port"`
		ExpressionHost       string `ini:"expression_host"`
		ExpressionPort       int    `ini:"expression_port"`
		ExpressionHostConfig string `ini:"expression_hostconfig"`
		AI                   string `ini:"ai"`
		ReenterCount         int    `ini:"reenter_count"`
		Debug                string `ini:"debug"`
	}

	ExpressionSectionConfig struct {
		Host             string `ini:"host"`
		Port             int    `ini:"port"`
		ExpressionSolver string `ini:"expression_solver"`
		SolverMaxModels  int    `ini:"solver_max_models"`
		HostConfig       string `ini:"hostconfig"`
	}

	FrontendSectionConfig struct {
		Host                string `ini:"host"`
		Port                int    `ini:"port"`
		SymAICoreHost       string `ini:"symaicore_host"`
		SymAICorePort       int    `ini:"symaicore_port"`
		SymAICoreHostConfig string `ini:"symaicore_hostconfig"`
		Resources           string `ini:"resources"`
		HostConfig          string `ini:"hostconfig"`
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

	HTTPConfigNamesStruct struct {
		Keys string `ini:"keys"`
	}

	WSSConfigNamesStruct struct {
		Keys string `ini:"keys"`
	}

	WSSSectionConfig struct {
		MaxConnections    int    `ini:"max_connections"`
		ReadBufferSize    int    `ini:"read_buffer_size"`
		WriteBufferSize   int    `ini:"write_buffer_size"`
		HandshakeTimeout  int    `ini:"handshake_timeout"`
		EntryPoint        string `ini:"entry_point"`
		EnableCompression bool   `ini:"enable_compression"`
		MaxMessageSize	  int64  `ini:"max_message_size"`
		PongWait          int    `ini:"pong_wait"`
		PingPeriod        int    `ini:"ping_period"`
		WriteWait         int    `ini:"write_wait"`
	}

	HTTPConfigStruct struct {
		Host         string `ini:"host"`
		Port         int    `ini:"port"`
		ReadTimeout  int    `ini:"read_timeout"`
		WriteTimeout int    `ini:"write_timeout"`
		IdleTimeout  int    `ini:"idle_timeout"`
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

func (c *SymAIConfig) GetLogger() *logrus.Logger {
	return c.Logger
}

func GetConfig() *SymAIConfig {
	return &Config
}

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
			Config.HTTPConfigsFromConfig = make(map[string]interface{})
			Config.WSSConfigsFromConfig = make(map[string]interface{})
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
						case "httpserver":
							nm = nm[len(sp[0])+1:]
							lc := HTTPConfigStruct{}
							err := inidata.Section(s.Name()).MapTo(&lc)
							if err != nil {
								return nil, err
							}
							Config.HTTPConfigsFromConfig[nm] = lc
						case "wss":
							nm = nm[len(sp[0])+1:]
							lc := WSSSectionConfig{}
							err := inidata.Section(s.Name()).MapTo(&lc)
							if err != nil {
								return nil, err
							}
							Config.WSSConfigsFromConfig[nm] = lc
						default:
						}
					}
				}

				// Check if loggers, hanlers and formatters lists are corresponds to the corresponding config section keys
				// loggers
				sp := strings.Split(Config.LoggersSection.Keys, ",")
				for _, s := range sp {
					s = strings.TrimSpace(s)
					b := false
					for lc, _ := range Config.LoggersFromComfig {
						if lc == s {
							b = true
							break
						}
					}
					if !b {
						return nil, fmt.Errorf("logger '%s' is declared in loggers section but not defined", s)
					}
				}
				if len(sp) < len(Config.LoggersFromComfig) {
					return nil, fmt.Errorf("number of declared loggers less than number of defined loggers")
				}
				// handlers
				sp = strings.Split(Config.HandlersSection.Keys, ",")
				for _, s := range sp {
					s = strings.TrimSpace(s)
					b := false
					for lc, _ := range Config.HandlersFromConfig {
						if lc == s {
							b = true
							break
						}
					}
					if !b {
						return nil, fmt.Errorf("handler '%s' is declared in handlers section but not defined", s)
					}
				}
				if len(sp) < len(Config.HandlersFromConfig) {
					return nil, fmt.Errorf("number of declared handlers less than number of defined handlers")
				}
				// formatters
				sp = strings.Split(Config.FormattersSection.Keys, ",")
				for _, s := range sp {
					s = strings.TrimSpace(s)
					b := false
					for lc, _ := range Config.FormattersFromConfig {
						if lc == s {
							b = true
							break
						}
					}
					if !b {
						return nil, fmt.Errorf("formatter '%s' is declared in formatters section but not defined", s)
					}
				}
				if len(sp) < len(Config.FormattersFromConfig) {

					return nil, fmt.Errorf("number of declared formatters less than number of defined formatters")
				}
			}
			err = Config.adjustHTTPSettings()
			if err == nil {
				err = Config.adjustWSSSettings()
			}
		}

	} else {
		return nil, errors.New("unknown configuration file extension")
	}
	return &Config, err
}

func (cfg *SymAIConfig) adjustHTTPSettings() error {
	var err error = nil
	// We have 3 "magic" configs. They are expresson, symaicore and frontend.
	// In order to be compatible with python version, the Host and Port fields of Expression, SymaiCore and Frontend
	// sections accordingthly should be equal to corrsponding Host and Port fields from corresponding sections
	if cfg.SymAISection.HostConfig == "" {
		cfg.SymAISection.HostConfig = "symaicore"
	}
	s := strings.TrimSpace(cfg.SymAISection.HostConfig)
	c, e := Config.GetHTTPServerConfig(s)
	if e != nil {
		c = HTTPConfigStruct{
			Host: cfg.SymAISection.Host,
			Port: cfg.SymAISection.Port,
		}
		cfg.HTTPConfigsFromConfig[s] = c
	} else {
		if c.Host != cfg.SymAISection.Host || c.Port != cfg.SymAISection.Port {
			c.Host = cfg.SymAISection.Host
			c.Port = cfg.SymAISection.Port
			cfg.HTTPConfigsFromConfig[s] = c
		}
	}

	if cfg.SymAISection.ExpressionHostConfig == "" {
		cfg.SymAISection.ExpressionHostConfig = "expression"
	}
	s = strings.TrimSpace(cfg.SymAISection.ExpressionHostConfig)
	c, e = cfg.GetHTTPServerConfig(s)
	if e != nil {
		c = HTTPConfigStruct{
			Host: cfg.SymAISection.ExpressionHost,
			Port: cfg.SymAISection.ExpressionPort,
		}
		cfg.HTTPConfigsFromConfig[s] = c
	} else {
		if c.Host != cfg.SymAISection.ExpressionHost || c.Port != cfg.SymAISection.ExpressionPort {
			c.Host = cfg.SymAISection.ExpressionHost
			c.Port = cfg.SymAISection.ExpressionPort
			cfg.HTTPConfigsFromConfig[s] = c
		}
	}

	if cfg.ExpressionSection.HostConfig == "" {
		cfg.ExpressionSection.HostConfig = "expression"
	}
	s = strings.TrimSpace(cfg.ExpressionSection.HostConfig)
	c, e = cfg.GetHTTPServerConfig(s)
	if e != nil {
		c = HTTPConfigStruct{
			Host: cfg.ExpressionSection.Host,
			Port: cfg.ExpressionSection.Port,
		}
		cfg.HTTPConfigsFromConfig[s] = c
	} else {
		if c.Host != cfg.ExpressionSection.Host || c.Port != cfg.ExpressionSection.Port {
			c.Host = cfg.ExpressionSection.Host
			c.Port = cfg.ExpressionSection.Port
			cfg.HTTPConfigsFromConfig[s] = c
		}
	}

	if cfg.FrontendSection.HostConfig == "" {
		cfg.FrontendSection.HostConfig = "frontend"
	}
	s = strings.TrimSpace(cfg.FrontendSection.HostConfig)
	c, e = cfg.GetHTTPServerConfig(s)
	if e != nil {
		c = HTTPConfigStruct{
			Host: cfg.FrontendSection.Host,
			Port: cfg.FrontendSection.Port,
		}
		cfg.HTTPConfigsFromConfig[s] = c
	} else {
		if c.Host != cfg.FrontendSection.Host || c.Port != cfg.FrontendSection.Port {
			c.Host = cfg.FrontendSection.Host
			c.Port = cfg.FrontendSection.Port
			cfg.HTTPConfigsFromConfig[s] = c
		}
	}
	if cfg.FrontendSection.SymAICoreHostConfig == "" {
		cfg.FrontendSection.SymAICoreHostConfig = "symaicore"
	}
	s = strings.TrimSpace(cfg.FrontendSection.SymAICoreHostConfig)
	c, e = cfg.GetHTTPServerConfig(s)
	if e != nil {
		c = HTTPConfigStruct{
			Host: cfg.FrontendSection.SymAICoreHost,
			Port: cfg.FrontendSection.SymAICorePort,
		}
		cfg.HTTPConfigsFromConfig[s] = c
	} else {
		if c.Host != cfg.FrontendSection.SymAICoreHost || c.Port != cfg.FrontendSection.SymAICorePort {
			c.Host = cfg.FrontendSection.SymAICoreHost
			c.Port = cfg.FrontendSection.SymAICorePort
			cfg.HTTPConfigsFromConfig[s] = c

		}
	}
	s = ""
	for k, _ := range cfg.HTTPConfigsFromConfig {
		if s != "" {
			s = s + ","
		}
		s = s + k
	}
	cfg.HTTPConfigsSection.Keys = s

	return err
}

func (cfg *SymAIConfig) adjustWSSSettings() error {
	var err error = nil
	// We have 3 "magic" configs. They are expresson, symaicore and frontend.
	// In order to be compatible with python version, the Host and Port fields of Expression, SymaiCore and Frontend
	// sections accordingthly should be equal to corrsponding Host and Port fields from corresponding sections
	if cfg.SymAISection.WSSHostConfig == "" {
		cfg.SymAISection.WSSHostConfig = "symaicore"
		c := WSSSectionConfig{
			MaxConnections:    10,
			ReadBufferSize:    2048,
			WriteBufferSize:   2048,
			HandshakeTimeout:  60,
			EntryPoint:        "/",
			EnableCompression: true,
			WriteWait:         10,
			PingPeriod:        60,
			PongWait:          54,
			MaxMessageSize:    512 * 1024,
		}
		if cfg.WSSConfigsFromConfig == nil {
			cfg.WSSConfigsFromConfig = make(map[string]interface{})
		}
		cfg.WSSConfigsFromConfig["symaicore"] = c
	}
	s := ""
	for k, _ := range cfg.WSSConfigsFromConfig {
		if s != "" {
			s = s + ","
		}
		s = s + k
	}
	cfg.WSSConfigsSection.Keys = s

	return err
}

func (cfg *SymAIConfig) InitDefaults() {
	var (
		lgr     LoggerConfigStruct    = LoggerConfigStruct{}
		fmtr    FormatterConfigStruct = FormatterConfigStruct{}
		hlndr   HandlerConfigStruct   = HandlerConfigStruct{}
		httpcfg HTTPConfigStruct      = HTTPConfigStruct{}
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
	cfg.SymAISection.HostConfig = "symaicore"
	cfg.SymAISection.ExpressionHostConfig = "expression"
	// Expression
	cfg.ExpressionSection.Host = "localhost"
	cfg.ExpressionSection.Port = 8080
	cfg.ExpressionSection.ExpressionSolver = "Z3"
	cfg.ExpressionSection.SolverMaxModels = 10
	cfg.ExpressionSection.HostConfig = "expression"
	// Frontend
	cfg.FrontendSection.Host = "localhost"
	cfg.FrontendSection.Port = 8000
	cfg.FrontendSection.SymAICoreHost = "localhost"
	cfg.FrontendSection.SymAICorePort = 12345
	cfg.FrontendSection.Resources = "/app/resources"
	cfg.FrontendSection.HostConfig = "frontend"
	cfg.FrontendSection.SymAICoreHostConfig = "symaicore"

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

	// HTPP Configs
	cfg.HTTPConfigsFromConfig = make(map[string]interface{})
	httpcfg.Host = "localhost"
	httpcfg.Port = 12345
	httpcfg.WriteTimeout = 5
	httpcfg.ReadTimeout = 5
	httpcfg.IdleTimeout = 36000
	cfg.HTTPConfigsFromConfig["symaicore"] = httpcfg
	httpcfg.Port = 8000
	cfg.HTTPConfigsFromConfig["frontend"] = httpcfg
	httpcfg.Port = 8080
	cfg.HTTPConfigsFromConfig["expression"] = httpcfg

	cfg.adjustHTTPSettings()
	cfg.adjustWSSSettings()
}

func Save(c *SymAIConfig, path string) error {
	ext := filepath.Ext(path)
	if strings.ToLower(ext) == ".ini" {
		err := c.adjustHTTPSettings()
		if err != nil {
			return err
		}
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
		sec.Key("hostconfig").SetValue(c.SymAISection.HostConfig)
		sec.Key("expression_hostconfig").SetValue(c.SymAISection.ExpressionHostConfig)

		sec, err = cfg.NewSection("Expression")
		if err != nil {
			return err
		}
		sec.Key("host").SetValue(c.ExpressionSection.Host)
		sec.Key("expression_solver").SetValue(c.ExpressionSection.ExpressionSolver)
		sec.Key("solver_max_models").SetValue(strconv.Itoa(c.ExpressionSection.SolverMaxModels))
		sec.Key("port").SetValue(strconv.Itoa(c.ExpressionSection.Port))
		sec.Key("hostconfig").SetValue(c.ExpressionSection.HostConfig)

		sec, err = cfg.NewSection("Frontend")
		if err != nil {
			return err
		}
		sec.Key("host").SetValue(c.FrontendSection.Host)
		sec.Key("symaicore_host").SetValue(c.FrontendSection.SymAICoreHost)
		sec.Key("resources").SetValue(c.FrontendSection.Resources)
		sec.Key("port").SetValue(strconv.Itoa(c.FrontendSection.Port))
		sec.Key("symaicore_port").SetValue(strconv.Itoa(c.FrontendSection.SymAICorePort))
		sec.Key("hostconfig").SetValue(c.FrontendSection.HostConfig)
		sec.Key("symaicore_hostconfig").SetValue(c.FrontendSection.SymAICoreHostConfig)

		c.LoggersSection.Keys = ""
		b := false
		for k, v := range c.LoggersFromComfig {
			if b {
				c.LoggersSection.Keys = c.LoggersSection.Keys + ","
			}
			b = true

			c.LoggersSection.Keys = c.LoggersSection.Keys + k
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

		b = false
		c.FormattersSection.Keys = ""
		for k, v := range c.FormattersFromConfig {
			if b {
				c.FormattersSection.Keys = c.FormattersSection.Keys + ","
			}
			b = true

			c.FormattersSection.Keys = c.FormattersSection.Keys + k
			sec, err := cfg.NewSection("formatter_" + k)
			if err != nil {
				return err
			}
			t := v.(FormatterConfigStruct)
			sec.Key("format").SetValue(t.Format)
		}

		b = false
		c.HandlersSection.Keys = ""
		for k, v := range c.HandlersFromConfig {
			if b {
				c.HandlersSection.Keys = c.HandlersSection.Keys + ","
			}
			b = true
			c.HandlersSection.Keys = c.HandlersSection.Keys + k
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

		b = false
		c.HTTPConfigsSection.Keys = ""
		for k, v := range c.HTTPConfigsFromConfig {
			if b {
				c.HTTPConfigsSection.Keys = c.HTTPConfigsSection.Keys + ","
			}
			b = true

			c.HTTPConfigsSection.Keys = c.HTTPConfigsSection.Keys + k
			sec, err := cfg.NewSection("httpserver_" + k)
			if err != nil {
				return err
			}
			t := v.(HTTPConfigStruct)
			sec.Key("host").SetValue(t.Host)
			sec.Key("port").SetValue(strconv.Itoa(t.Port))
			sec.Key("read_timeout").SetValue(strconv.Itoa(t.ReadTimeout))
			sec.Key("write_timeout").SetValue(strconv.Itoa(t.WriteTimeout))
			sec.Key("idle_timeout").SetValue(strconv.Itoa(t.IdleTimeout))
		}

		b = false
		c.WSSConfigsSection.Keys = ""
		for k, v := range c.WSSConfigsFromConfig {
			if b {
				c.WSSConfigsSection.Keys = c.WSSConfigsSection.Keys + ","
			}
			b = true

			c.WSSConfigsSection.Keys = c.WSSConfigsSection.Keys + k
			sec, err := cfg.NewSection("wss_" + k)
			if err != nil {
				return err
			}
			t := v.(WSSSectionConfig)
			sec.Key("max_connections").SetValue(strconv.Itoa(t.MaxConnections))
			sec.Key("read_buffer_size").SetValue(strconv.Itoa(t.ReadBufferSize))
			sec.Key("write_buffer_size").SetValue(strconv.Itoa(t.WriteBufferSize))
			sec.Key("handshake_timeout").SetValue(strconv.Itoa(t.HandshakeTimeout))
			sec.Key("enable_compression").SetValue(strconv.FormatBool(t.EnableCompression))
			sec.Key("write_wait").SetValue(strconv.Itoa(t.WriteWait))
			sec.Key("ping_period").SetValue(strconv.Itoa(t.PingPeriod))
			sec.Key("pong_wait").SetValue(strconv.Itoa(t.PongWait))
			sec.Key("max_message_size").SetValue(strconv.FormatInt(t.MaxMessageSize, 10))
			sec.Key("entry_point").SetValue(t.EntryPoint)			
		}

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

		sec, err = cfg.NewSection("httpconfigs")
		if err != nil {
			return err
		}
		sec.Key("keys").SetValue(c.HTTPConfigsSection.Keys)

		sec, err = cfg.NewSection("wssconfigs")
		if err != nil {
			return err
		}
		sec.Key("keys").SetValue(c.WSSConfigsSection.Keys)

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

func (cfg *SymAIConfig) GetHTTPServerConfig(httpcfgname string) (HTTPConfigStruct, error) {
	var (
		err error = nil
		r         = HTTPConfigStruct{}
	)
	for nm, v := range cfg.HTTPConfigsFromConfig {
		if strings.TrimSpace(nm) == strings.TrimSpace(httpcfgname) {
			r = v.(HTTPConfigStruct)
			return r, nil
		}
	}
	err = fmt.Errorf("unknown HTTP config name '%s'", httpcfgname)
	return r, err
}

func (cfg *SymAIConfig) GetWSSServerConfig(wsscfgname string) (WSSSectionConfig, error) {
	var (
		err error = nil
		r         = WSSSectionConfig{}
	)
	for nm, v := range cfg.WSSConfigsFromConfig {
		if strings.TrimSpace(nm) == strings.TrimSpace(wsscfgname) {
			r = v.(WSSSectionConfig)
			return r, nil
		}
	}
	err = fmt.Errorf("unknown WSS config name '%s'", wsscfgname)
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

func (cfg *SymAIConfig) GetExpressionHostConfig() (HTTPConfigStruct, error) {
	s := strings.TrimSpace(cfg.ExpressionSection.HostConfig)
	if s == "" {
		s = "expression"
	}
	hcf, err := cfg.GetHTTPServerConfig(s)
	return hcf, err
}

func (cfg *SymAIConfig) GetSymAICoreHostConfig() (HTTPConfigStruct, error) {
	s := strings.TrimSpace(cfg.SymAISection.HostConfig)
	if s == "" {
		s = "symaicore"
	}
	hcf, err := cfg.GetHTTPServerConfig(s)
	return hcf, err
}

func (cfg *SymAIConfig) GetSymAICoreExpressionConfig() (HTTPConfigStruct, error) {
	s := strings.TrimSpace(cfg.SymAISection.ExpressionHostConfig)
	if s == "" {
		s = "expression"
	}
	hcf, err := cfg.GetHTTPServerConfig(s)
	return hcf, err
}

func (cfg *SymAIConfig) GetSymAICoreWSSConfig() (WSSSectionConfig, error) {
	s := strings.TrimSpace(cfg.SymAISection.WSSHostConfig)
	if s == "" {
		s = "symaicore"
	}
	hcf, err := cfg.GetWSSServerConfig(s)
	return hcf, err
}

func (cfg *SymAIConfig) GetFrontendHostConfig() (HTTPConfigStruct, error) {
	s := strings.TrimSpace(cfg.FrontendSection.HostConfig)
	if s == "" {
		s = "frontend"
	}
	hcf, err := cfg.GetHTTPServerConfig(s)
	return hcf, err
}

func (cfg *SymAIConfig) GetFrontendSymAICoreConfig() (HTTPConfigStruct, error) {
	s := strings.TrimSpace(cfg.FrontendSection.SymAICoreHostConfig)
	if s == "" {
		s = "symaicore"
	}
	hcf, err := cfg.GetHTTPServerConfig(s)
	return hcf, err
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
