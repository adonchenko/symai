package controller

import (
	"fmt"
	"os"
	"os/signal"
	"src/server/config"
	"sync"
	"syscall"
)

func RunFrontendServer(cfg *config.SymAIConfig) error {
	var wg sync.WaitGroup
	err := config.InitLogger("frontend")
	if err != nil {
		_, _ = fmt.Fprint(os.Stderr, err)
		return err
	}
	cfg.Logger.Info("Starting SymAI frontend web server on host " + cfg.FrontendSection.Host + " port ", cfg.FrontendSection.Port, "...")
	wg.Add(1)
	go RunServer(&wg, cfg)
	wg.Wait()
	return nil
}

func RunServer(wg *sync.WaitGroup, cfg *config.SymAIConfig) {
	defer wg.Done()
	c := make(chan os.Signal, 1)

	signal.Notify(c,
		syscall.SIGHUP,
		syscall.SIGINT,
		syscall.SIGTERM,
		syscall.SIGQUIT)
	
	go RunSymAIFrontendServer(wg, cfg, c)

	s := <-c
	switch s {
	case syscall.SIGINT:
		cfg.Logger.Info("received SIGINT signal...")
	case syscall.SIGTERM:
		cfg.Logger.Info("received SIGTERM signal...")
	case syscall.SIGKILL:
		cfg.Logger.Info("received SIGKILL signal...")
	case syscall.SIGQUIT:
		cfg.Logger.Info("received SIGQUIT signal...")
	}
	cfg.Logger.Info("stopping fronted web server...")
}
