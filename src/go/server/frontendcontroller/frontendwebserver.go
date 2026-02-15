package frontendcontroller

import (
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"src/server/config"
	"src/server/utils"
	"strings"
	"syscall"
)

var (
	quit *chan os.Signal = nil
)

func initController(quitChan *chan os.Signal) {
	quit = quitChan
}

func getContentType(path string) (isBin bool, contentType string, fileName string) {
	isBin = false
	contentType = "text/html"
	ext := strings.ToLower(filepath.Ext(path))
	fileName = config.GetConfig().FrontendSection.Resources + path
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
			fileName = config.GetConfig().FrontendSection.Resources + "/index.html"
		}
	}
	return isBin, contentType, fileName
}

func catchAllHandler(w http.ResponseWriter, r *http.Request) {
	var (
		hcf config.HTTPConfigStruct
		scf config.HTTPConfigStruct
	)
	isBin, contentType, name := getContentType(r.URL.Path)

	if !utils.FileExists(name) {
		config.GetConfig().Logger.Error("resource '" + name + "' not found")
		http.NotFound(w, r)
	} else {
		data, err := os.ReadFile(name)
		if err != nil {
			config.GetConfig().Logger.Error("resource '" + name + "' error file operation " + err.Error())
			http.Error(w, http.StatusText(http.StatusInternalServerError)+" resource '"+name+"' error file operation "+err.Error(), http.StatusInternalServerError)
		} else {
			hcf, err = config.GetConfig().GetFrontendHostConfig()
			if err != nil {
				config.GetConfig().Logger.Error("Failed to get frontend host config: " + err.Error())
				http.Error(w, http.StatusText(http.StatusInternalServerError)+" Failed to get frontend host config: "+err.Error(), http.StatusInternalServerError)
				return
			}
			scf, err = config.GetConfig().GetFrontendSymAICoreConfig()
			if err != nil {
				config.GetConfig().Logger.Error("Failed to get frontend symai core host config: " + err.Error())
				http.Error(w, http.StatusText(http.StatusInternalServerError)+" Failed to get frontend host config: "+err.Error(), http.StatusInternalServerError)
				return
			}
			w.Header().Set("Content-Type", contentType)
			if !isBin {
				// Text file content. Processing the macros
				data = []byte(strings.ReplaceAll(string(data), "{FRONTEND_HOST}", hcf.Host))
				data = []byte(strings.ReplaceAll(string(data), "{FRONTEND_PORT}", fmt.Sprint(hcf.Port)))
				data = []byte(strings.ReplaceAll(string(data), "{CORE_HOST}", scf.Host))
				data = []byte(strings.ReplaceAll(string(data), "{CORE_PORT}", fmt.Sprint(scf.Port)))
			}
			_, err = w.Write(data)
			if err != nil {
				config.GetConfig().Logger.Error("resource '" + name + "' error sending file " + err.Error())
			}
		}
	}
}

func shutdownHandler(http.ResponseWriter, *http.Request) {
	config.GetConfig().Logger.Info("shutdown command received")
	if quit != nil {
		*quit <- os.Signal(syscall.SIGQUIT)
	}
}
