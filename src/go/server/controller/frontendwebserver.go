package controller

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"src/server/config"
	"src/server/utils"
	"strings"
	"sync"
	"syscall"

	"github.com/gorilla/mux"
)

var (
	srvCfg   *config.SymAIConfig = nil
	srvWg    *sync.WaitGroup     = nil
	stopChan chan os.Signal
)

func getContentType(path string) (isBin bool, contentType string, fileName string) {
	isBin = false
	contentType = "text/html"
	ext := strings.ToLower(filepath.Ext(path))
	fileName = srvCfg.FrontendSection.Resources + path
	switch ext {
	case ".html", ".htm":
		contentType = "text/html"
	case ".gif":
		contentType = "image/gif"
		isBin = true
	case ".jpg", ".jpeg":
		contentType = "image/jpeg"
		isBin = true
	case ".png":
		contentType = "image/png"
		isBin = true
	case ".tiff":
		contentType = "image/tiff"
		isBin = true
	case ".ico":
		contentType = "image/x-icon"
		isBin = true
	case ".pdf":
		contentType = "application/pdf"
		isBin = true
	case ".svg":
		contentType = "image/svg+xml"
		isBin = true
	case ".css":
		contentType = "text/css"
	case ".csv":
		contentType = "text/csv"
	case ".js":
		contentType = "application/javascript"
	case ".text", ".txt":
		contentType = "text/plain"
	case ".xml":
		contentType = "text/xml"
	default:
		if filepath.Base(path) == "" || filepath.Base(path) == "/" {
			fileName = srvCfg.FrontendSection.Resources + "/index.html"
		}
	}
	return isBin, contentType, fileName
}

func catchAllHandler(w http.ResponseWriter, r *http.Request) {
	isBin, contentType, name := getContentType(r.URL.Path)

	if !utils.FileExists(name) {
		srvCfg.Logger.Error("resource '" + name + "' not found")
		http.NotFound(w, r)
	} else {
		data, err := os.ReadFile(name)
		if err != nil {
			srvCfg.Logger.Error("resource '" + name + "' error file operation " + err.Error())
			http.Error(w, http.StatusText(http.StatusInternalServerError)+" resource '"+name+"' error file operation "+err.Error(), http.StatusInternalServerError)
		} else {
			w.Header().Set("Content-Type", contentType)
			if !isBin {
				// Text file content. Processing the macros
				data = []byte(strings.ReplaceAll(string(data), "{FRONTEND_HOST}", srvCfg.FrontendSection.Host))
				data = []byte(strings.ReplaceAll(string(data), "{FRONTEND_PORT}", fmt.Sprint(srvCfg.FrontendSection.Port)))
				data = []byte(strings.ReplaceAll(string(data), "{CORE_HOST}", srvCfg.FrontendSection.SymAICoreHost))
				data = []byte(strings.ReplaceAll(string(data), "{CORE_PORT}", fmt.Sprint(srvCfg.FrontendSection.SymAICorePort)))
			}
			_, err = w.Write(data)
			if err != nil {
				srvCfg.Logger.Error("resource '" + name + "' error sending file " + err.Error())
			}
		}
	}
}

func shutdownHandler(w http.ResponseWriter, r *http.Request) {
	srvCfg.Logger.Info("shutdown command received")
	stopChan <- syscall.SIGQUIT
}

func RunSymAIFrontendServer(wg *sync.WaitGroup, cfg *config.SymAIConfig, c chan os.Signal) {
	srvCfg = cfg
	srvWg = wg
	stopChan = c

	defer srvWg.Done()
	router := mux.NewRouter()
	router.StrictSlash(true)
	router.PathPrefix("/").HandlerFunc(catchAllHandler).Methods("GET")
	router.Methods("POST").PathPrefix("/api/v1/system/shutdown")

	srv := &http.Server{
		Handler: router,
		Addr:    cfg.FrontendSection.Host + ":" + fmt.Sprint(cfg.FrontendSection.Port),
	}
	err := srv.ListenAndServe()
	if err != nil {
		srvCfg.Logger.Error(err.Error())
	} else {
		srvCfg.Logger.Info("Finished OK")
	}
}
