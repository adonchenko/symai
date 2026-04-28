package parser

type (
	NameBooleanTestPair struct {
		name string
		flag bool
	}

	NameTerminalsTestPair struct {
		name      string
		terminals []string
	}
)

func NewNameTerminalsTestPair() *NameTerminalsTestPair {
	return &NameTerminalsTestPair{
		name:      "",
		terminals: make([]string, 0),
	}
}