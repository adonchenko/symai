package symaicorecontroller

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gorilla/websocket"

	"src/server/config"
)

var (
	hub      *Hub
	stopChan chan os.Signal

	upgrader = websocket.Upgrader{}
)

func initController() error {
	stopChan = make(chan os.Signal, 1)
	signal.Notify(stopChan, syscall.SIGTERM, syscall.SIGINT, syscall.SIGQUIT, syscall.SIGHUP)

	cfg := config.GetConfig()
	wsscfg, err := cfg.GetWSSServerConfig(cfg.SymAISection.WSSHostConfig)
	if err != nil {
		cfg.Logger.Error("Failed to get symai core wss config: " + err.Error())
		return err
	}

	upgrader = websocket.Upgrader{
		ReadBufferSize:  wsscfg.ReadBufferSize,
		WriteBufferSize: wsscfg.WriteBufferSize,
		CheckOrigin: func(r *http.Request) bool {
			return true // Allow all origins for simplicity, adjust as needed for security
		},
	}
	return nil
}

func RunCoreServer(cfg *config.SymAIConfig) error {
	var (
		hcf config.HTTPConfigStruct
	)
	err := config.InitLogger("symaicore")
	if err != nil {
		_, _ = fmt.Fprint(os.Stderr, err)
		return err
	}
	hcf, err = cfg.GetSymAICoreHostConfig()
	if err == nil {
		err = initController()
		if err != nil {
			cfg.Logger.Error("Failed to initialize SymAI Core Server: " + err.Error())
			return err
		}
		wsscfg, err := cfg.GetWSSServerConfig(cfg.SymAISection.WSSHostConfig)
		if err != nil {
			cfg.Logger.Error("Failed to get SymAI Core Web Socket Server config: " + err.Error())
			return err
		}
		// Create and start the hub
		hub = newHub()
		go hub.run()

		// Set up HTTP routes
		http.HandleFunc(wsscfg.EntryPoint, handleWebSocket)
		// Create the HTTP server with timeouts
		server := &http.Server{
			Addr:         hcf.Host + ":" + fmt.Sprint(hcf.Port),
			ReadTimeout:  time.Duration(hcf.ReadTimeout) * time.Second,
			WriteTimeout: time.Duration(hcf.WriteTimeout) * time.Second,
		}

		// Start server in a goroutine so we can handle shutdown
		go func() {
			cfg.Logger.Info("Starting SymAI Core Server on host '"+hcf.Host+"', port ", hcf.Port, " and root path '"+wsscfg.EntryPoint+"' ...")
			if err := server.ListenAndServe(); err != http.ErrServerClosed {
				cfg.Logger.Error("SymAI Core Server error: " + err.Error())
			}
		}()

		// Wait for interrupt signal
		stopChan := make(chan os.Signal, 1)
		signal.Notify(stopChan, syscall.SIGINT, syscall.SIGTERM)
		<-stopChan

		cfg.Logger.Info("Shutting down SymAI Core server...")

		// Create a deadline for shutdown
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second) // TODO: Make timeout configurable
		defer cancel()

		// Close all WebSocket connections gracefully
		for client := range hub.clients {
			// Send close message to each client
			client.conn.WriteMessage(websocket.CloseMessage,
				websocket.FormatCloseMessage(websocket.CloseNormalClosure, "SymAI Core Server shutting down"))
			client.conn.Close()
		}

		// Shutdown HTTP server
		if err := server.Shutdown(ctx); err != nil {
			cfg.Logger.Error("SymAI Core Server shutdown error: " + err.Error())
		}

		cfg.Logger.Info("SymAI Core Server stopped")

		return nil
	} else {
		cfg.Logger.Error("Failed to get SymAI Core host config: " + err.Error())
		return err
	}
}
