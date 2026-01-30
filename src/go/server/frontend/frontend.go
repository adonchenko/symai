package main

import (
	"errors"
	"fmt"
	"os"
	"time"

	"src/server/config"
	"src/server/controller"

	"github.com/urfave/cli"
)

type (
	InputData struct {
		configFileName string
		host           string
		port           int
		symaiCoreHost  string
		symaiCorePort  int
		resourcePath   string
	}
)

var (
	inputData = InputData{
		configFileName: "/properties/symai.ini",
		host:           "localhost",
		port:           8000,
		symaiCoreHost:  "localhost",
		symaiCorePort:  12345,
		resourcePath:   "/app/resources",
	}
	app *cli.App

	major     string
	minor     string
	patch     string
	buildDate = time.Now().UTC().String()
)

func setTemplates() {
	cli.CommandHelpTemplate = `NAME:
   {{.HelpName}}{{if .Usage}} - {{.Usage}}{{end}}

USAGE:
   {{if .UsageText}}{{.UsageText}}{{else}}{{.HelpName}}{{if .VisibleFlags}} [command options]{{end}} {{if .ArgsUsage}}{{.ArgsUsage}}{{else}}[arguments...]{{end}}{{end}}{{if .Category}}

CATEGORY:

   {{.Category}}{{end}}{{if .Description}}

DESCRIPTION:
   {{.Description}}{{end}}{{if .VisibleFlags}}

OPTIONS:
   {{range .VisibleFlags}}{{.}}
   {{end}}{{end}}
`
}

func main() {
	setTemplates()
	app = cli.NewApp()
	app.Name = "SymAI Frontend Server"
	app.Usage = "frontend [OPTION] ... \n"
	app.Version = buildDate + " V" + major + "." + minor + "." + patch
	app.Action = run
	app.Flags = []cli.Flag{
		cli.StringFlag{
			Name:        "config,c",
			Usage:       "config file",
			Required:    false,
			Value:       inputData.configFileName,
			Destination: &inputData.configFileName,
		},
		cli.StringFlag{
			Name:        "ip,i",
			Usage:       "frontend server host",
			Required:    false,
			Value:       inputData.host,
			Destination: &inputData.host,
		},
		cli.IntFlag{
			Name:        "port,p",
			Usage:       "frontend server port",
			Required:    false,
			Value:       inputData.port,
			Destination: &inputData.port,
		},
		cli.StringFlag{
			Name:        "ch,corehost",
			Usage:       "SymAI Core server host",
			Required:    false,
			Value:       inputData.symaiCoreHost,
			Destination: &inputData.symaiCoreHost,
		},
		cli.IntFlag{
			Name:        "cp,coreport",
			Usage:       "SymAI Core server port",
			Required:    false,
			Value:       inputData.symaiCorePort,
			Destination: &inputData.symaiCorePort,
		},
		cli.StringFlag{
			Name:        "r,resources",
			Usage:       "resources directory",
			Required:    false,
			Value:       inputData.resourcePath,
			Destination: &inputData.resourcePath,
		},
	}
	app.Commands = []cli.Command{}
	app.Run(os.Args)
}

func run(c *cli.Context) error {
	return exec()
}

func exec() error {

	cfg, err := config.Create(inputData.configFileName)
	if err != nil {
		_, _ = fmt.Fprint(os.Stderr, "error loading config:", err)
		return err
	}

	if cfg == nil {
		_, _ = fmt.Fprint(os.Stderr, "config is nil")
		err = errors.New("config is nil")
		return err
	}

	cfg.FrontendSection.Host = inputData.host
	cfg.FrontendSection.Port = inputData.port
	cfg.FrontendSection.SymAICoreHost = inputData.symaiCoreHost
	cfg.FrontendSection.SymAICorePort = inputData.symaiCorePort
	cfg.FrontendSection.Resources = inputData.resourcePath

	_, err = cfg.InitLogger("frontend")
	if err != nil {
		_, _ = fmt.Fprint(os.Stderr, err)
		return err
	}

	return controller.RunFrontendServer(cfg)
}
