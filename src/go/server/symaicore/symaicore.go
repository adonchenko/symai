package main

import (
	"errors"
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/urfave/cli"

	"src/server/config"
	"src/server/symaicorecontroller"
)

type (
	InputData struct {
		configFileName string
		host           string
		port           int
		exprhost       string
		exprport       int
		tempdir        string
		reentercount   int
		debug          bool
		ai             bool
	}
)

var (
	inputData = InputData{
		configFileName: "/properties/symai.ini",
		host:           "localhost",
		port:           12345,
		exprhost:       "localhost",
		exprport:       8080,
		tempdir:        "/tmpdir/temp",
		reentercount:   1,
		debug:          false,
		ai:             false,
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
	app.Name = "SymAI Core Server"
	app.Usage = "symaicore [OPTION] ... \n"
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
			Name:        "t,temp",
			Usage:       "SymAI Core Server temporary directory",
			Required:    false,
			Value:       inputData.tempdir,
			Destination: &inputData.tempdir,
		},
		cli.StringFlag{
			Name:        "eh,exprhost",
			Usage:       "SymAI Expression Server Host address",
			Required:    false,
			Value:       inputData.exprhost,
			Destination: &inputData.exprhost,
		},
		cli.IntFlag{
			Name:        "ep,exprport",
			Usage:       "SymAI Expression Server Host port",
			Required:    false,
			Value:       inputData.exprport,
			Destination: &inputData.exprport,
		},
		cli.BoolFlag{
			Name:        "d,debug",
			Usage:       "SymAI Core Server Symbolic Calculations Debugging Mode On/OFF Flag",
			Required:    false,
			Destination: &inputData.debug,
		},
		cli.BoolFlag{
			Name:        "a,ai",
			Usage:       "SymAI Core Server Symbolic Calculations Using AI Mode On/OFF Flag",
			Required:    false,
			Destination: &inputData.ai,
		},
	}
	app.Commands = []cli.Command{}
	_ = app.Run(os.Args)

}

func run(*cli.Context) error {
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

	cfg.SymAISection.Host = inputData.host
	cfg.SymAISection.Port = inputData.port
	cfg.SymAISection.ExpressionHost = inputData.exprhost
	cfg.SymAISection.ExpressionPort = inputData.exprport
	cfg.SymAISection.TempDir = inputData.tempdir
	cfg.SymAISection.Debug = strconv.FormatBool(inputData.debug)
	cfg.SymAISection.AI = strconv.FormatBool(inputData.ai)

	return symaicorecontroller.RunCoreServer(cfg)
}
