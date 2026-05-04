package symaicorecontroller

import (
	"fmt"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"

	"src/server/config"
)

type (
	// Client represents a single WebSocket connection
	Client struct {
		ctx map[string]interface{} // Context fields:
		// "symaiconfig" a SymAISection value @config for details
		// "environment" a FileBaseData value
		// "properties" a PropertyProcessingContext value
		// "actions" an ActionsProcessingContext value
		conn *websocket.Conn
		UUID uuid.UUID
		send chan []byte
	}

	// Hub maintains the set of active clients
	Hub struct {
		// Registered clients - using a map for O(1) lookups
		clients map[*Client]bool
		// Register requests from new clients
		register chan *Client

		// Unregister requests from disconnecting clients
		unregister chan *Client
	}
)

// newHub creates a new Hub instance
func newHub() *Hub {
	return &Hub{
		register:   make(chan *Client),
		unregister: make(chan *Client),
		clients:    make(map[*Client]bool),
	}
}

// run starts the hub's main loop - call this in a goroutine
func (h *Hub) run() {
	for {
		select {
		case client := <-h.register:
			// Add new client to the map
			h.clients[client] = true
			log := config.GetConfig().GetLogger()
			if cnf != nil {
				log = cnf.GetLogger()
			}
			log.Info(fmt.Sprintf("Client connected. Total clients: %d", len(h.clients)))

		case client := <-h.unregister:
			// Remove client if it exists
			if _, ok := h.clients[client]; ok {
				delete(h.clients, client)
				close(client.send)
				log := config.GetConfig().GetLogger()
				if cnf != nil {
					log = cnf.GetLogger()
				}
				client.cleanupTempData()
				log.Info(fmt.Sprintf("Client disconnected. Total clients: %d", len(h.clients)))
				client.conn.Close()
			}
		}
	}
}
