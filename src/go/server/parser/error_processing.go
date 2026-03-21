package parser

// Error processing

type ErrorProcessing struct {
	errorList []string
}

func (v *ErrorProcessing) GetErrorList() []string {
	return v.errorList
}

func (v *ErrorProcessing) SetErrorList(lst []string) {
	v.errorList = lst
}

func NewErrorProcessing() *ErrorProcessing {
	return &ErrorProcessing{
		errorList: make([]string, 0),
	}
}

func (v *ErrorProcessing) HasError() bool {
	return len(v.errorList) > 0
}

func (v *ErrorProcessing) addError(err string) {
	v.errorList = append(v.errorList, err)
}