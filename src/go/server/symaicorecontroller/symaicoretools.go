package symaicorecontroller

import (
	"encoding/json"
	"errors"
	"fmt"
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
		Filepath string // Path to the physical file that keeps the physical file content
	}

	// A file reference definition. Used for keeping environment, properties, activities, behaviors files
	FileData struct {
		FileBaseData
		Solver string `json:"solver,omitempty"`
	}

	// Stack represents a generic LIFO (Last-In-First-Out) data structure.
	Stack[T any] struct {
		items []T
	}
)

// GetAll returns all elements in the stack without modifying it.
func (s *Stack[T]) GetAll() []T {
	return s.items
}

// GetTop returns the top element of the stack without removing it.
// Push adds an element to the top of the stack.
func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

// PushL adds an element to the bottom of the stack.
func (s *Stack[T]) PushL(item T) {
	s.items = append([]T{item}, s.items...)
}

func (s *Stack[T]) GetItems() []T {
	return s.items
}

// Pop removes and returns the top element. 
// Returns the zero value of T and false if the stack is empty.
func (s *Stack[T]) Pop() (T, error) {
    if len(s.items) == 0 {
        var zero T
        return zero, fmt.Errorf("stack is empty")
    }
    
    // Get last item and shrink slice
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, nil
}

// PopL removes and returns the bottom element.
// Returns the zero value of T and false if the stack is empty.
func (s *Stack[T]) PopL() (T, error) {
	if len(s.items) == 0 {
		var zero T
		return zero, fmt.Errorf("stack is empty")
	}
	
	// Get first item and shrink slice	
	item := s.items[0]
	s.items = s.items[1:]
	return item, nil
}

// Top returns the top element without removing it.
// Returns the zero value of T and false if the stack is empty.
func (s *Stack[T]) Top() (T, error) {
	if len(s.items) == 0 {
		var zero T
		return zero, fmt.Errorf("stack is empty")
	}
	return s.items[len(s.items)-1], nil
}

// Bottom returns the bottom element without removing it.
// Returns the zero value of T and false if the stack is empty.
func (s *Stack[T]) Bottom() (T, error) {
	if len(s.items) == 0 {
		var zero T
		return zero, fmt.Errorf("stack is empty")
	}
	return s.items[0], nil
}

// PopN removes and returns the n top elements.
// Returns the zero value of T and false if the stack has less than n elements.
func (s *Stack[T]) PopN(n int) ([]T, error) {
	if len(s.items) < n {
		return nil, fmt.Errorf("stack has less than %d elements", n)
	}
	
	items := s.items[len(s.items)-n:]
	s.items = s.items[:len(s.items)-n]
	return items, nil
}	

// PopLN removes and returns the n bottom elements.
// Returns the zero value of T and false if the stack has less than n elements.
func (s *Stack[T]) PopLN(n int) ([]T, error) {
	if len(s.items) < n {
		return nil, fmt.Errorf("stack has less than %d elements", n)
	}
	
	items := s.items[:n]
	s.items = s.items[n:]
	return items, nil
}	

// PushN adds n elements to the top of the stack.
func (s *Stack[T]) PushN(items []T) {
	s.items = append(s.items, items...)
}

// PushLN adds n elements to the bottom of the stack.
func (s *Stack[T]) PushLN(items []T) {
	s.items = append(items, s.items...)
}

// Dup  duplicates the stack
func (s *Stack[T]) Dup() *Stack[T] {
	newItems := make([]T, len(s.items))
	copy(newItems, s.items)
	return &Stack[T]{items: newItems}
}

// IsEmpty checks if the stack is empty.
func (s *Stack[T]) IsEmpty() bool {
    return len(s.items) == 0
}

// Length returns the number of elements in the stack.
func (s *Stack[T]) Length() int {
	return len(s.items)
}

// Peek returns the top element without removing it.
func (s *Stack[T]) Peek() (T, error) {
	if len(s.items) == 0 {
		var zero T	
		return zero, fmt.Errorf("stack is empty")
	}
	return s.items[len(s.items)-1], nil
}

// Poke updates the top element of the stack without removing it.
func (s *Stack[T]) Poke(val T) error {
	if len(s.items) == 0 {
		return fmt.Errorf("stack is empty")
	}
	s.items[len(s.items)-1] = val
	return nil
}	

// Set updates the n-th element of the stack without removing it.
func (s *Stack[T]) Set(n int, val T) error {
	if n < 0 || n >= len(s.items) {
		return fmt.Errorf("index out of bounds")
	}
	s.items[n] = val
	return nil
}

// Get returns the n-th element of the stack without removing it.
func (s *Stack[T]) Get(n int) (T, error) {
	if n < 0 || n >= len(s.items) {
		var zero T
		return zero, fmt.Errorf("index out of bounds")
	}
		return s.items[n], nil
}	

// Clear removes all elements from the stack.
func (s *Stack[T]) Clear() {
	s.items = []T{}
}

// Reverse reverses the order of elements in the stack.
func (s *Stack[T]) Reverse() {	
	for i, j := 0, len(s.items)-1; i < j; i, j = i+1, j-1 {
		s.items[i], s.items[j] = s.items[j], s.items[i]
	}	
}

// NewStack creates and returns a new Stack instance.
func NewStack[T any]() *Stack[T] {
	return &Stack[T]{items: []T{}}
}

/*** End Stack ***/

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
