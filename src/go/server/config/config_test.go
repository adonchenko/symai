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
