package symaicorecontroller

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDoTraversalbeh(t *testing.T) {
	clnt := InitTestConfig(t)	
	assert.NotNil(t, clnt)
	ReinitClientTest(clnt)	
	cnf.GetLogger().Info("TestDoTraversalbeh started")
	// Preparing property for traversalbeh command
	res, err := doProperty(clnt, "{\"content\":\"0 < 1\"}")
	assert.Nil(t, err, "unexpected error for property command")
	assert.Equal(t, res, "0<1", "unexpected response for property command")
	// Preparing environment for traversalbeh command
	res, err = doEnvironment(clnt, "{\"content\":\"a == 2 && b == 3 && c == 2\"}")
	assert.Nil(t, err, "unexpected error for environment command")
	assert.Equal(t, res, "a==2&&b==3&&c==2", "unexpected response for environment command")
	// Preparing actions for traversalbeh command
	res, err = doActions(clnt, "{\"content\":\"a(1): a > b -> c = a + b, a(2): a < b -> c = b - a, a(3): a == b -> a = c - b, a(4): 1 -> a = b + 1,\"}")
	assert.Nil(t, err, "unexpected error for actions command")
	assert.Equal(t, res, "a(1):a>b->c=a+b,a(2):a<b->c=b-a,a(3):a==b->a=c-b,a(4):0<1->a=b+1,", "unexpected response for actions command")
	// Preparing behaviors for traversalbeh command
	res, err = doBehaviors(clnt, "{\"content\":\"B(0) = B(1).a(4).B(1), B(1) = a(1) + a(2) + a(3),\"}")
	assert.Nil(t, err, "unexpected error for behaviors command")
	assert.Equal(t, res, "B(0)=B(1).a(4).B(1),B(1)=a(1)+a(2)+a(3),", "unexpected response for behaviors command")

	res, err = doTraversalbeh(clnt, "")
	assert.Nil(t, err, "unexpected error for traversalbeh command")	
	assert.Equal(t, res, "", "unexpected response for traversalbeh command")
}