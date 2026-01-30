package config

import (
	"fmt"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

const BaseTestConfigFile string = "test/testconfig."
const BaseSaveTargetFilename string = "./test."

var TestFileExtension []string

func InitExtArray() {
	TestFileExtension = []string{"ini"}
}

func TestLoadSettings(t *testing.T) {
	InitExtArray()
	for _, ext := range TestFileExtension {
		_, err := os.Stat(BaseTestConfigFile + ext)
		if !(err == nil || os.IsExist(err)) {
			t.Fatal(fmt.Sprintf("File `%s` is absent", BaseTestConfigFile+ext))
		}
		cfg, err := Load(BaseTestConfigFile + ext)
		if err != nil {
			t.Fatal(fmt.Errorf("error: `%v`", err))
		}

		assert.NotNil(t, cfg, "cfg is nil")
	}
}

func TestCreateSettings(t *testing.T) {
	InitExtArray()
	defer func(path string) {
		err := os.RemoveAll(path)
		if err != nil {

		}
	}("cp/")
	for _, ext := range TestFileExtension {
		_, err := os.Stat(BaseTestConfigFile + ext)
		cfg, err := Create("cp/" + BaseTestConfigFile + ext)
		if err != nil {
			t.Fatal(fmt.Errorf("error: `%v`", err))
		}

		assert.NotNil(t, cfg, "cfg is nil")
	}
}

func TestLoadSettingsFail(t *testing.T) {
	cfg, err := Load("")
	assert.NotNil(t, err, "settings loaded from an empty file")
	assert.Nil(t, cfg, "cfg is not nil after loading config from an empty file")
}

func TestValidateLoggerSettings(t *testing.T) {
	InitExtArray()
	for _, ext := range TestFileExtension {
		cfg, err := Load(BaseTestConfigFile + ext)
		assert.Nil(t, err, "cannot load config")
		assert.NotNil(t, cfg, "config is nil")
		assert.Nil(t, Validate(cfg), "config validation failed")
		assert.Nil(t, err, "invalid logger settings")
	}
}

func TestValidateLogLevel(t *testing.T) {
	assert.Nil(t, ValidateLogLevel("panic"), "panic log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("fatal"), "fatal log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("error"), "error log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("warn"), "warn log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("warning"), "warning log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("info"), "info log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("debug"), "debug log level is allowed but is invalidated")
	assert.Nil(t, ValidateLogLevel("trace"), "trace log level is allowed but is invalidated")
	assert.NotNil(t, ValidateLogLevel("qqq"), "qqq log level is not allowed but is successfully validated")
}

func TestSaveSettings(t *testing.T) {
	InitExtArray()
	for _, ext := range TestFileExtension {
		_, err := os.Stat(BaseTestConfigFile + ext)
		if !(err == nil || os.IsExist(err)) {
			t.Fatal(fmt.Sprintf("file `%s` is absent", BaseTestConfigFile+ext))
		}
		cfg, err := Load(BaseTestConfigFile + ext)
		if err != nil {
			t.Fatal(fmt.Errorf("error: `%v`", err))
		}
		if cfg == nil {
			t.Fatal("cfg is nil")
		}
		err = Save(cfg, BaseSaveTargetFilename+ext)
		if err != nil {
			t.Fatal(fmt.Errorf("error after Save: `%v`", err))
		}
		_, err = os.Stat(BaseSaveTargetFilename + ext)
		if !(err == nil || os.IsExist(err)) {
			t.Fatal(fmt.Errorf("the destination file has not been created"))
		}
		err = os.RemoveAll(BaseSaveTargetFilename + ext)
		if err != nil {
			t.Fatal(fmt.Errorf("error after removing temporary file: `%v`", err))
		}
	}
}

func TestApplySettings(t *testing.T) {
	InitExtArray()
	for _, ext := range TestFileExtension {
		_, err := os.Stat(BaseTestConfigFile + ext)
		if !(err == nil || os.IsExist(err)) {
			t.Fatal(fmt.Sprintf("File `%s` is absent", BaseTestConfigFile+ext))
		}
		cfg, err := Load(BaseTestConfigFile + ext)
		assert.Nil(t, err, "cannot load config file "+BaseTestConfigFile+ext)
		assert.NotNil(t, cfg, "loaded config file is nil")
		err = Validate(cfg)
		assert.Nil(t, err, "config validation failed")
		err = InitLogger("frontend")
		cfg.Logger.Info("Info")
	}
}
