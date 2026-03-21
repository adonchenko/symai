package symaicorecontroller

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

type (
	ProcessFileData struct {
		source string
		result FileData
		result_error error
	}
)

func InitProcessFileData() []ProcessFileData {
	res := make([]ProcessFileData, 0)

	res = append(res, ProcessFileData {
		source: "{\"content\":\"v==d\"}",
		result: FileData{Solver:"", FileBaseData: FileBaseData{Filename: "", Content: "v==d", Filepath: ""}},
		result_error: nil,
	})

	return res
}

func TestProcessFile(t *testing.T) {
	test_data := InitProcessFileData()
	for _, fd := range test_data {
		res, err := processFile(fd.source)
		
		assert.Equal(t, fd.result_error, err)
		if fd.result_error == nil {
            assert.Equal(t, fd.result.Content, res.Content) 
            assert.Equal(t, fd.result.Filename, res.Filename)
			assert.Equal(t, fd.result.Solver, res.Solver)
		}
	}
}
