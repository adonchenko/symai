import json
import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/")

from symaicorecommands import *
from symaiconfig import *

import logging

import unittest

class SymAITestConstants(Enum):
    TEST_BASE_TEMP_DIR = "./test/data/temp"
    TEST_INI_DEFAULT = "./test/data/test.ini"

class SymAICoreTestCase(unittest.TestCase):
    def setUp(self):

        self.cc = SymAICoreCommands()
        self.cfg = ConfigParser()
        self.cfg.add_section(SymAIConfig.HANDLER_FILE_SYMAICORE.value)
        self.cfg.set(SymAIConfig.HANDLER_FILE_SYMAICORE.value, SymAIConfig.ARGS.value, "temp/symaicore.log")
        self.cfg = symaiconfig.create_config(SymAITestConstants.TEST_INI_DEFAULT.value, symaiconfig.SymAIConfig.SYMAICORE.value, self.cfg)
        logging.basicConfig(filename=SymAITestConstants.TEST_INI_DEFAULT.value)
        logger = logging.getLogger("symaicore")
        self.cc.set_config(self.cfg)
        self.cc.set_logger(logger)
        self.cc.set_temp_dir("temp")

    def test_do_actions(self):
        # cuuid, [data_received, need_test_repl, resp_tail_tpl, need_test_file, file_test_tpl, ...], ...
        test_data =[
                     [ "temp",
                       [ "",
                         True,
                        '{"content": "", "filename": "actions.act"}',
                         False,
                         '{"content": "", "filename": "actions.act"}'
                       ]
                     ],
                     [ "temp",
                       [ '{"content": "a(1): a > b -> c = a + b, a(2): a < b -> c = b - a, a(3): a == b -> a = c - b, a(4): 1 -> a = b + 1,", "filename": "b.beh"}',
                         False,
                         '',
                         True,
                         'a(1):a>b->c=a+b,a(2):a<b->c=b-a,a(3):a==b->a=c-b,a(4):0<1->a=b+1,',
                       ]
                     ]
                   ]
        for it in test_data:
            cuuid = it[0]

            data_received = it[1][0]
            need_test_rsp = it[1][1]
            rsp_tpl = it[1][2]
            need_test_file = it[1][3]
            file_content = it[1][4]
            rsp = self.cc.do_actions(cuuid, data_received)
            self.assertIsNotNone(rsp, "Result is None")
            if need_test_rsp:
                # Going with response test
                self.assertNotEqual(rsp, "", "Cannot be empty")
                rst = json.loads(rsp_tpl)
                rsr = json.loads(rsp)
                self.assertEqual(rsr, rst, "lists of expected and received fields are not equal")
            if need_test_file:
                fname = ""
                if hasattr(self.cc, "actions"):
                    fname = getattr(self.cc,"actions")
                    try:
                        with open(fname, "r") as file:
                            content = file.read()
                        self.assertEqual(content, file_content, "loaded content is not equal to expected")
                        # TODO: parse both file_content and content action lists and then compare its

                    except FileNotFoundError:
                        self.assertTrue(False, f"Error: The file {fname} was not found.")
                    except Exception as e:
                        self.assertTrue(False, f"An error occurred: {e}")
                else:
                    self.assertTrue(False, "action file has not been defined")

    def test_do_behaviors(self):
        # cuuid, [data_received, need_test_repl, resp_tail_tpl, need_test_file, file_test_tpl, ...], ...
        test_data = [
            ["temp",
             ["",
              True,
              '{"content": "", "filename": "behaviors.beh"}',
              False,
              '{"content": "", "filename": "behaviors.beh"}'
              ]
             ],
            ["temp",
             ['{"content": "B(0)=B(1).a(4).B(1),B(1)=a(1)+a(2)+a(3),", "filename": "b.beh"}',
              False,
              '',
              True,
              'B(0)=B(1).a(4).B(1),B(1)=a(1)+a(2)+a(3),',
              ]
             ]
        ]
        for it in test_data:
            cuuid = it[0]

            data_received = it[1][0]
            need_test_rsp = it[1][1]
            rsp_tpl = it[1][2]
            need_test_file = it[1][3]
            file_content = it[1][4]
            rsp = self.cc.do_behaviors(cuuid, data_received)
            self.assertIsNotNone(rsp, "Result is None")
            if need_test_rsp:
                # Going with response test
                self.assertNotEqual(rsp, "", "Cannot be empty")
                rst = json.loads(rsp_tpl)
                rsr = json.loads(rsp)
                self.assertEqual(rsr, rst, "lists of expected and received fields are not equal")
            if need_test_file:
                fname = ""
                if hasattr(self.cc, "behaviors"):
                    fname = getattr(self.cc, "behaviors")
                    try:
                        with open(fname, "r") as file:
                            content = file.read()
                        self.assertEqual(content, file_content, "loaded content is not equal to expected")
                        # TODO: parse both file_content and content behaviors lists and then compare its

                    except FileNotFoundError:
                        self.assertTrue(False, f"Error: The file {fname} was not found.")
                    except Exception as e:
                        self.assertTrue(False, f"An error occurred: {e}")
                else:
                    self.assertTrue(False, "behaviors file has not been defined")

    def test_do_property(self):
        # cuuid, [data_received, need_test_repl, resp_tail_tpl, need_test_file, file_test_tpl, ...], ...
        test_data = [
            ["temp",
             ["",
              True,
              '{"content": "", "filename": "properties.prop"}',
              False,
              '{"content": "", "filename": "properties.prop"}'
              ]
             ]
        ]
        for it in test_data:
            cuuid = it[0]

            data_received = it[1][0]
            need_test_rsp = it[1][1]
            rsp_tpl = it[1][2]
            need_test_file = it[1][3]
            file_content = it[1][4]
            rsp = self.cc.do_property(cuuid, data_received)
            self.assertIsNotNone(rsp, "Result is None")
            if need_test_rsp:
                # Going with response test
                self.assertNotEqual(rsp, "", "Cannot be empty")
                rst = json.loads(rsp_tpl)
                rsr = json.loads(rsp)
                self.assertEqual(rsr, rst, "lists of expected and received fields are not equal")
            if need_test_file:
                fname = ""
                if hasattr(self.cc, "property"):
                    fname = getattr(self.cc, "property")
                    try:
                        with open(fname, "r") as file:
                            content = file.read()
                        self.assertEqual(content, file_content, "loaded content is not equal to expected")
                        # TODO: parse both file_content and content properties and then compare its

                    except FileNotFoundError:
                        self.assertTrue(False, f"Error: The file {fname} was not found.")
                    except Exception as e:
                        self.assertTrue(False, f"An error occurred: {e}")
                else:
                    self.assertTrue(False, "property file has not been defined")

    def test_do_environment(self):
        # cuuid, [data_received, need_test_repl, resp_tail_tpl, need_test_file, file_test_tpl, ...], ...
        test_data = [
            ["temp",
             ["",
              True,
              '{"content": "", "filename": "environment.env"}',
              False,
              '{"content": "", "filename": "environment.env"}'
              ]
             ]
        ]
        for it in test_data:
            cuuid = it[0]

            data_received = it[1][0]
            need_test_rsp = it[1][1]
            rsp_tpl = it[1][2]
            need_test_file = it[1][3]
            file_content = it[1][4]
            rsp = self.cc.do_environment(cuuid, data_received)
            self.assertIsNotNone(rsp, "Result is None")
            if need_test_rsp:
                # Going with response test
                self.assertNotEqual(rsp, "", "Cannot be empty")
                rst = json.loads(rsp_tpl)
                rsr = json.loads(rsp)
                self.assertEqual(rsr, rst, "lists of expected and received fields are not equal")
            if need_test_file:
                fname = ""
                if hasattr(self.cc, "environment"):
                    fname = getattr(self.cc, "environment")
                    try:
                        with open(fname, "r") as file:
                            content = file.read()
                        self.assertEqual(content, file_content, "loaded content is not equal to expected")
                        # TODO: parse both file_content and content environments and then compare its

                    except FileNotFoundError:
                        self.assertTrue(False, f"Error: The file {fname} was not found.")
                    except Exception as e:
                        self.assertTrue(False, f"An error occurred: {e}")
                else:
                    self.assertTrue(False, "environment file has not been defined")

    def tearDown(self):
        if self.cc is not None:
            self.cc.remove_directory_tree(self.cc.get_temp_dir())
            self.cc = None
        self.cfg = None
