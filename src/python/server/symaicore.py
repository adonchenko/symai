#!/usr/bin/python3

"""A websockets server with SymAO UI protocol for python 3.
"""
import configparser
import asyncio

import websockets
import symaiconfig
import logging
from logging import config
import signal
import sys
import argparse
import symaicorecommands
from symaicorecommands import SymAICoreCommands

connected_clients = dict()

# Function to handle one client connection
async def handle_client(websocket):
    global connected_clients
    if connected_clients.get(websocket) is None:
        connected_clients.update({websocket: symaicorecommands.SymAICoreParam()})
    sc: SymAICoreCommands = SymAICoreCommands()
    # Add the new client to the set of connected clients
    try:
        # Listen for messages from the client
        async for message in websocket:
            st = message.replace("\t"," ").replace("\r"," ").replace("\n"," ").strip().split()
            if len(st) > 0:
                st = message.replace("\t"," ").replace("\r"," ").replace("\n"," ").strip().split()[0]

            match st:
                case "shutdown":
                    try:
                        for ws, param in connected_clients.items():
                            sc.do_stop(param.get_uuid())
                            await ws.close()
                    except:
                        pass
                    sc.do_shutdown()
                    sys.exit(0)
                case "stop":
                    sc.get_logger().info("stop command received")
                    try:
                        if connected_clients.get(websocket) is not None:
                            sc.do_stop(connected_clients.get(websocket).get_uuid())
                            connected_clients.pop(websocket)
                    except Exception as e:
                        sc.get_logger().error(f"stop command failed {str(e)}")
                        res = "nok " + str(e)
                        await websocket.send(res)
                    else:
                        sc.get_logger().info("stop command passed ok")
                    try:
                        connected_clients.pop(websocket)
                    except:
                        pass
                    await websocket.close()
                case "ai":
                    sc.get_logger().info("ai command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        try:
                            res = "ok " + sc.do_ai(str(connected_clients.get(websocket).get_uuid()),
                                                   str(message))
                        except Exception as e:
                            sc.get_logger().error(f"ai command error {str(e)}")
                            res = f"nok {str(e)}"
                        try:
                            await websocket.send(res)
                        except:
                            pass
                case "solver":
                    sc.get_logger().info("solver command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        try:
                            res = "ok " + sc.do_solver(str(connected_clients.get(websocket).get_uuid()),
                                                   str(message))
                        except Exception as e:
                            sc.get_logger().error(f"solver command error {str(e)}")
                            res = f"nok {str(e)}"
                        try:
                            await websocket.send(res)
                        except:
                            pass
                case "max_models":
                    sc.get_logger().info("max_models command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        try:
                            res = "ok " + sc.do_max_models(str(connected_clients.get(websocket).get_uuid()),
                                                       str(message))
                        except Exception as e:
                            sc.get_logger().error(f"max_models command error {str(e)}")
                            res = f"nok {str(e)}"
                        try:
                            await websocket.send(res)
                        except:
                            pass
                case "reenter_count":
                    sc.get_logger().info("reenter_count command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        try:
                            res = "ok " + sc.do_reenter_count(str(connected_clients.get(websocket).get_uuid()),
                                                           str(message))
                        except Exception as e:
                            sc.get_logger().error(f"reenter_count command error {str(e)}")
                            res = f"nok {str(e)}"
                        try:
                            await websocket.send(res)
                        except:
                            pass
                case "debug":
                    sc.get_logger().info("debug command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        try:
                            res = "ok " + sc.do_debug(str(connected_clients.get(websocket).get_uuid()),
                                                              str(message))
                        except Exception as e:
                            sc.get_logger().error(f"reenter_count command error {str(e)}")
                            res = f"nok {str(e)}"
                        try:
                            await websocket.send(res)
                        except:
                            pass
                case "behaviors":
                    sc.get_logger().info("behaviors command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error(f"UUID not found.Cannot process {message}")
                        await websocket.send(f"nok UUID not found.Cannot process {message}")
                    else:
                        res = "ok"
                        try:
                            s = message.replace("\t"," ").replace("\r"," ").replace("\n"," ").strip()
                            s = sc.do_behaviors(str(connected_clients.get(websocket).get_uuid()),
                                                s[9:])
                            if len(s) > 0:
                                res = res + " " + s
                        except Exception as e:
                            sc.get_logger().error("behaviors command failed " + str(e))
                            res = "nok " + str(e)
                        else:
                            sc.get_logger().info("behaviors command passed ok")
                        finally:
                            await websocket.send(res)
                case "actions":
                    sc.get_logger().info("actions command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error(f"UUID not found.Cannot process {message}")
                        await websocket.send(f"nok UUID not found.Cannot process {message}")
                    else:
                        res = "ok"
                        try:
                            s =  message.replace("\t"," ").replace("\r"," ").replace("\n"," ").strip()
                            s = sc.do_actions(str(connected_clients.get(websocket).get_uuid()),
                                              s[7:])
                            if len(s) > 0:
                                res = res + " " + s
                        except Exception as e:
                            sc.get_logger().error("actions command failed " + str(e))
                            res = "nok " + str(e)
                        else:
                            sc.get_logger().info("actions command passed ok")
                        finally:
                            await websocket.send(res)
                case "environment":
                    sc.get_logger().info("environment command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error(f"UUID not found.Cannot process {message}" )
                        await websocket.send(f"nok UUID not found.Cannot process {message}")
                    else:
                        res = "ok"
                        try:
                            s = sc.do_environment(str(connected_clients.get(websocket).get_uuid()),
                                                  message.replace("\t"," ").replace("\r"," ").replace("\n"," ").strip().strip()[11:])
                            if len(s) > 0:
                                res = res + " " + s
                        except Exception as e:
                            sc.get_logger().error("environment command failed " + str(e))
                            res = "nok " + str(e)
                        else:
                            sc.get_logger().info("environment command passed ok")
                        finally:
                            await websocket.send(res)

                case "property":
                    sc.get_logger().info("property command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        res = "ok"
                        try:
                            s = sc.do_property(str(connected_clients.get(websocket).get_uuid()),
                                               message.replace("\t"," ").replace("\r"," ").replace("\n"," ").strip().strip()[8:])
                            if len(s) > 0:
                                res = res + " " + s
                        except Exception as e:
                            sc.get_logger().error("property command failed " + str(e))
                            res = "nok " + str(e)
                        else:
                            sc.get_logger().info("property command passed ok")
                        finally:
                            await websocket.send(res)

                case "traversalbeh":
                    sc.get_logger().info("traversalbeh command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        res = "ok"
                        try:
                            s = None
                            if len(message) > 11:
                                s = str(message).strip()[12:]
                            suuid = str(connected_clients.get(websocket).get_uuid())
                            sc.get_logger().debug(f"traversalbeh command before loop {suuid}")
                            for res in sc.do_traversalbeh(
                                    suuid,
                                    s):
                                await websocket.send(res)
                                res = ""
                                """
                                if bool(sc.get_debug()):
                                    message = await websocket.recv()
                                    st = message.replace("\t", " ").replace("\r", " ").replace("\n",
                                                                                               " ").strip().split()
                                    if len(st) > 0:
                                        st = message.replace("\t", " ").replace("\r", " ").replace("\n",
                                                                                                   " ").strip().split()[
                                            0]
                                    is_cnt = sc.do_rsp_traversalbeh(str(connected_clients.get(websocket).get_uuid()), st)
                                    if is_cnt:
                                        break
                               """
                        except Exception as e:
                            sc.get_logger().error("traversalbeh command failed " + str(e))
                            res = "nok " + str(e)
                        else:
                            if len(res) > 2 and res[:2] == "ok":
                                sc.get_logger().info("traversalbeh command passed ok")
                        finally:
                            if len(res) > 2 and res[:2] == "ok":
                                await websocket.send(res)

                case "trace":
                    sc.get_logger().info("trace command received")
                    if connected_clients.get(websocket) is None:
                        sc.get_logger().error("UUID not found.Cannot process " + message)
                        await websocket.send("nok UUID not found.Cannot process " + message)
                    else:
                        res = "ok"
                        s = str(message).replace("\t"," ").replace("\r"," ").replace("\n"," ").strip()
                        if len(s) > 5:
                            s = s[5:]
                        else:
                            s = ""
                        try:
                            sc.do_trace(str(connected_clients.get(websocket).get_uuid()), s)
                        except Exception as e:
                            sc.get_logger().error("trace command failed " + str(e))
                            res = "nok " + str(e)
                        else:
                            sc.get_logger().info("trace command passed ok")
                        finally:
                            await websocket.send(res)

                case _:
                    sc.get_logger().error("Unknown command " + message)
                    await websocket.send("Unknown command " + message)

    except websockets.exceptions.ConnectionClosed:
        if connected_clients.get(websocket) is not None:
            connected_clients.pop(websocket)
    finally:
        # Remove the client from the set of connected clients
        pass

def signal_handler(signal, frame):
    logger = logging.getLogger("symaicore")
    logger.info("Signal INT caught")
    sc = SymAICoreCommands()
    sc.remove_directory_tree(symaiconfig.SymAIConfig.BASE_TEMP.value)
    sys.exit(0)

# Main function to start the WebSocket server
async def main():
    sc = symaicorecommands.SymAICoreCommands()

    parser = argparse.ArgumentParser(description="HTTP Server")
    parser.add_argument("-p", "--port", dest="port", default=12345, required=False, type=int,
                        help="Listening port for an SymAI Core Websockets Server")
    parser.add_argument("-i", "--ip", dest="ip", default="localhost", required=False, help="SymAI Core Websockets Server IP")
    parser.add_argument("-c", "--config", dest="config", default="/properties/symai.ini", required=False,
                        help="Configuration file name of SymAI Websockets Server")
    parser.add_argument("-t", "--temp", dest="tempdir", default="/tmpdir/temp", required=False, help="SymAI Core Websockets Server Temporary Directory")
    parser.add_argument("-eh", "--exprhost", dest="exprhost", default="localhost", required=False, help="SymAI Expression Server Host IP")
    parser.add_argument("-ep", "--exprport", dest="exprport", default=8080, required=False, help="SymAI Expression Server Port No")
    parser.add_argument("-rc", "--reentercount", dest="reentercount", default=str(1), required=False, help="SymAI Symbolic Calculations Reentering Counter")
    parser.add_argument("-d", "--debug", dest="debug", default=str(False), required=False, help="SymAI Symbolic Calculations Debugging Mode On/OFF Flag")

    args = parser.parse_args()

    cfg = configparser.ConfigParser()
    cfg.add_section(symaiconfig.SymAIConfig.SYMAICORE.value)
    cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.HOST.value, args.ip)
    cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.PORT.value, str(args.port))
    cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.TEMP.value, args.tempdir)
    cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.EXPRESSION_HOST.value, args.exprhost)
    cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.EXPRESSION_PORT.value, str(args.exprport))
    cfg.set(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.BEHAVIORS_REENTER_COUNT.value, args.reentercount)

    cfg = symaiconfig.create_config(args.config, symaiconfig.SymAIConfig.SYMAICORE.value, cfg)

    logging.config.fileConfig(args.config)
    logger = logging.getLogger("symaicore")
    signal.signal(signal.SIGINT, signal_handler)

    # disable all loggers from different files
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.getLogger('asyncio.coroutines').setLevel(logging.ERROR)
    logging.getLogger('websockets.server').setLevel(logging.ERROR)
    logging.getLogger('websockets.protocol').setLevel(logging.ERROR)
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)

    sc.set_config(cfg)
    sc.set_logger(logger)

    server = await websockets.serve(handle_client,
                                    str(cfg.get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.HOST.value)),
                                    int(cfg.get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.PORT.value)))
    logger.info("SymAI Websockets Server Running On %s:%s ..........." % (cfg.get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.HOST.value), int(cfg.get(symaiconfig.SymAIConfig.SYMAICORE.value, symaiconfig.SymAIConfig.PORT.value))))
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    asyncio.run(main())
