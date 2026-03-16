package symaicorecontroller

import (
	"errors"
	"fmt"
	"net/http"
	// "os"
	// "path/filepath"

	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"

	"src/server/config"
)

// readPump reads messages from the WebSocket connection
func (c *Client) readPump() {
	// Ensure cleanup happens when this goroutine exits
	defer func() {
		hub.unregister <- c
		c.conn.Close()
	}()

	cfg := config.GetConfig()
	wsscfg, err := cfg.GetWSSServerConfig(cfg.SymAISection.WSSHostConfig)
	if err != nil {
		cfg.Logger.Error("Failed to get symai core wss config: " + err.Error())
		return
	}

	// Configure connection limits
	c.conn.SetReadLimit(wsscfg.MaxMessageSize)
	c.conn.SetReadDeadline(time.Now().Add(time.Duration(wsscfg.PongWait) * time.Second))

	// Reset the read deadline every time we receive a pong
	c.conn.SetPongHandler(func(string) error {
		c.conn.SetReadDeadline(time.Now().Add(time.Duration(wsscfg.PongWait) * time.Second))
		return nil
	})

	// Main read loop
	for {
		messageType, message, err := c.conn.ReadMessage()

		if err != nil {
			// Categorize the error for proper handling
			if websocket.IsCloseError(err, websocket.CloseNormalClosure, websocket.CloseGoingAway) {
				cfg.Logger.Info(fmt.Sprintf("Client %s closed connection normally", c.UUID))
			} else if websocket.IsUnexpectedCloseError(err) {
				//cfg.Logger.Info(fmt.Sprintf("Client %s unexpected close: %v", c.UUID, err))
			} else {
				//cfg.Logger.Info(fmt.Sprintf("Client %s read error: %v", c.UUID, err))
			}
			return
		}

		// Log message details for debugging - be careful with sensitive data
		cfg.Logger.Debug(fmt.Sprintf("Received message '%s' type %d, length %d from %s",
			message, messageType, len(message), c.UUID))
		rsp, err := c.ProcessMessage(message)
		if err != nil {
			cfg.Logger.Error(fmt.Sprintf("Error processing message from %s: %v", c.UUID, err))
		}
		
		if err == nil {
			rsp = []byte("ok")
		} else {
			rsp = []byte("nok " + err.Error() + " " + string(rsp))
		}
		c.send <- rsp
	}
}

// writePump sends messages to the WebSocket connection
func (c *Client) writePump() {
	cfg := config.GetConfig()
	wsscfg, err := cfg.GetWSSServerConfig(cfg.SymAISection.WSSHostConfig)
	if err != nil {
		cfg.Logger.Error(fmt.Sprintf("Failed to get symai core wss config: %v", err))
		return
	}
	// Create a ticker for sending periodic pings
	ticker := time.NewTicker(time.Duration(wsscfg.PingPeriod) * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			// Set write deadline for every write operation
			c.conn.SetWriteDeadline(time.Now().Add(time.Duration(wsscfg.WriteWait) * time.Second))

			if !ok {
				// The hub closed the channel - send close message
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			// Get a writer for the next message
			w, err := c.conn.NextWriter(websocket.TextMessage)
			if err != nil {
				return
			}
			w.Write(message)

			// Batch any queued messages into the same WebSocket frame
			// This improves performance when messages arrive faster than we send
			n := len(c.send)
			for i := 0; i < n; i++ {
				w.Write([]byte{'\n'})
				w.Write(<-c.send)
			}

			if err := w.Close(); err != nil {
				return
			}

		case <-ticker.C:
			// Send periodic ping to keep connection alive
			c.conn.SetWriteDeadline(time.Now().Add(time.Duration(wsscfg.WriteWait) * time.Second))
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

// handleWebSocket upgrades HTTP connections and manages the WebSocket lifecycle
func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	// Upgrade the HTTP connection to WebSocket
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		config.GetConfig().Logger.Error("Failed to upgrade to WebSocket: " + err.Error())
		return
	}

	client := &Client{
		ctx : make(map[string]interface{}),
		conn: conn,
		send: make(chan []byte, 512*1024), // Buffer size for outgoing messages
		UUID: uuid.New(),
	}
	client.ctx["symaiconfig"] = config.GetConfig().SymAISection

	hub.register <- client

	// Start goroutines for reading and writing
	go client.writePump()
	go client.readPump()
}

func (c *Client) cleanupTempData() {
	// Client temporary data cleanup
	// TODO:!!!

}

func (c *Client) ProcessMessage(msg []byte) ([]byte, error) {
	var (
		err error = nil
	)

	s := strings.TrimSpace(string(msg))
	cmd := strings.Split(strings.ReplaceAll(strings.ReplaceAll(strings.ReplaceAll(s, "\t", " "), "\n", " "), "\r", " "), " ")

	tail := ""
	rsp := []byte("")
	if len(cmd[0]) == 0 {
		rsp = []byte("Empty command received")
	} else {
		tail = strings.TrimSpace(s[strings.Index(s, cmd[0])+len(cmd[0]):])
	}

	s = cmd[0]	
	if coreCommands != nil {
		f, ok := (*coreCommands)[cmd[0]]
		if !ok {
			rsp = []byte("")
			err = errors.New("unknown command '" + cmd[0] + "'")
		} else
		{
			err = f.exec(c, tail)
		}
    } else {
		err = errors.New("unknown command '" + cmd[0] + "'")
	}
	return rsp, err
}
