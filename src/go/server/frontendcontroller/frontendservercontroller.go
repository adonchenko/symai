package frontendcontroller

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"src/server/config"
	"syscall"
	"time"

	"github.com/gorilla/mux"
)

func RunFrontendServer(cfg *config.SymAIConfig) error {

	err := config.InitLogger("frontend")
	if err != nil {
		_, _ = fmt.Fprint(os.Stderr, err)
		return err
	}
	// Set up HTTP routes
	router := mux.NewRouter()
	router.StrictSlash(true)
	router.PathPrefix("/").HandlerFunc(catchAllHandler).Methods("GET")
	router.PathPrefix("/api/v1/system/shutdown").HandlerFunc(shutdownHandler).Methods("POST")
	hcf, err := cfg.GetFrontendHostConfig()
	if err != nil {
		cfg.Logger.Error("Failed to get SymAI frontend host config: " + err.Error())
		return err
	}

	// Create the HTTP server with timeouts
	server := &http.Server{
		Handler:      router,
		Addr:         hcf.Host + ":" + fmt.Sprint(hcf.Port),
		ReadTimeout:  time.Duration(hcf.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(hcf.WriteTimeout) * time.Second,
	}

	// Start server in a goroutine so we can handle shutdown
	go func() {
		cfg.Logger.Info("SymAI frontend server starting on " + hcf.Host + ":" + fmt.Sprint(hcf.Port))
		if err := server.ListenAndServe(); err != http.ErrServerClosed {
			cfg.Logger.Error("SymAI frontend server error: " + err.Error())
		}
	}()

	// Wait for interrupt signal
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM, syscall.SIGHUP, syscall.SIGQUIT)
	initController(&quit)
	<-quit

	cfg.Logger.Info("Shutting down SymAI frontend server...")

	// Create a deadline for shutdown
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Shutdown HTTP server
	if err := server.Shutdown(ctx); err != nil {
		cfg.Logger.Error("SymAI frontend server shutdown error: " + err.Error())
	}

	cfg.Logger.Info("SymAI frontend server stopped")

	return nil
}
