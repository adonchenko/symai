package symaicorecontroller

import (
	"errors"
	"syscall"

	"src/server/config"
)

type (
	SymAICoreCommandProcessing func(c *Client, params string) error

	SymAICoreCommand struct {
		exec SymAICoreCommandProcessing
	}
)

var (
	allCoreCommands map[string]SymAICoreCommand = make(map[string]SymAICoreCommand, 0)
	cnf             *config.SymAIConfig         = nil
)

func doShutdown(c *Client, params string) error {
	if cnf == nil {
		config.GetConfig().GetLogger().Error("cnf is nil")
		return errors.New("cnf is nil")
	}
	cnf.GetLogger().Info("client " + c.UUID.String() + " shutdown command received")
	stopChan <- syscall.SIGQUIT
	// TODO: stop expression and frontend services here as well!!!
	return nil
}

func doStop(c *Client, params string) error {
	if cnf == nil {
		config.GetConfig().GetLogger().Error("cnf is nil")
		return errors.New("cnf is nil")
	}
	cnf.GetLogger().Info("client " + c.UUID.String() + " stop command received")
	hub.unregister <- c
	return nil
}

func initCoreCommands(c *config.SymAIConfig) *map[string]SymAICoreCommand {
	cnf = c
	allCoreCommands = make(map[string]SymAICoreCommand, 0)
	allCoreCommands["shutdown"] = SymAICoreCommand{
		exec: doShutdown,
	}
	allCoreCommands["stop"] = SymAICoreCommand{
		exec: doStop,
	}
	return &allCoreCommands
}
