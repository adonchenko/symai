package symaicorecontroller

import (
	"encoding/json"
	"errors"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"time"

	"github.com/antlr4-go/antlr/v4"

	"src/server/BehaviorsGrammar"
	"src/server/parser"
)

type (
	FileBaseData struct {
		Filename string `json:"filename,omitempty"` // Original file name if exists one
		Content  string `json:"content,omitempty"`  // A file content
		Filepath string // Path to the physical file that keeps the file content
	}

	// A file reference definition. Used for keeping environment, properties, activities, behaviors files
	FileData struct {
		FileBaseData
		Solver string `json:"solver,omitempty"`
	}
)

func CreateFileWithPath(path string) (*os.File, error) {
	// Extract the directory part from the path
	dir := filepath.Dir(path)

	// Create directories if they don't exist
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, err
	}

	// Create the file (truncates if exists)
	return os.Create(path)
}

func WriteToFile(path string, content string) error {
	fp, err := CreateFileWithPath(path)
	if err == nil {
		defer fp.Close()
		_, err = fp.Write([]byte(content))
	}

	return err
}

func processFile(inp string) (FileData, error) {
	fd := FileData{Solver: "", FileBaseData: FileBaseData{Filename: "", Content: "", Filepath: ""}}
	err := json.Unmarshal([]byte(inp), &fd)

	return fd, err
}

func InitParser(inputStr string) (*BehaviorsGrammar.BehaviorsGrammarParser, *parser.SymAIErrorListener) {
	listener := parser.SymAIErrorListener{}
	input := antlr.NewInputStream(inputStr)
	lexer := BehaviorsGrammar.NewBehaviorsGrammarLexer(input)
	stream := antlr.NewCommonTokenStream(lexer, 0)
	p := BehaviorsGrammar.NewBehaviorsGrammarParser(stream)
	p.BuildParseTrees = true
	lexer.RemoveErrorListeners()
	p.RemoveErrorListeners()
	lexer.AddErrorListener(&listener)
	p.AddErrorListener(&listener)

	return p, &listener
}

func ShutdownExpression() error {
	if cnf != nil {
		sc := cnf.SymAISection
		conn := http.Client{Timeout: time.Duration(1) * time.Second}
		req, err := http.NewRequest("GET", "http://"+sc.ExpressionHost+":"+strconv.FormatInt(int64(sc.ExpressionPort), 10)+"/shutdown", nil)
		if err != nil {
			return err
		} 
		_, err = conn.Do(req)
		if err != nil {
			return err
		}
		return nil
	} else {
		return errors.New("cnf is nil or symaiconfig value is missing in client context")
	}
}
