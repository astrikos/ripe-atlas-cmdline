import os
import json
import unittest
from StringIO import StringIO

import mock
from jsonschema import validate

from atlascli.commands.oneoff import Command as OneOffCommand


class UnitTestOneOff(unittest.TestCase):

    def setUp(self):

        self.definitions_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type", "af", "description"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["ping", "traceroute", "dns", "sslcert"]
                    },
                    "af": {
                        "type": "integer",
                        "enum": [4, 6]
                    },
                    "description": {
                        "type": "string",
                    },
                    "target": {
                        "type": "string",
                    },
                    "is_oneoff": {
                        "type": "boolean",
                    },
                }
            }
        }

        args = ["-f", "tests/test_api_key"]
        self.cmd = OneOffCommand(args)

    def create_patch(self, name):
        patcher = mock.patch(name)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def test_run(self):
        self.cmd.sleep_time = 0
        self.cmd.timeout = 0
        create = self.create_patch('atlascli.commands.create.Command.run')
        meta = self.create_patch(
            'atlascli.commands.oneoff.Command.get_meta_data'
        )
        results = self.create_patch(
            'atlascli.commands.oneoff.Command.get_results'
        )

        # UDM creation failed
        create.return_value = False
        self.assertFalse(self.cmd.run())
        # meta fetching failed
        create.return_value = True
        meta.return_value = False
        self.assertFalse(self.cmd.run())
        # url extracting failed
        meta.return_value = (True, None)
        self.assertFalse(self.cmd.run())
        # getting results checks
        meta.return_value = (True, "dummy_url")
        results.return_value = True
        self.assertTrue(self.cmd.run())
        results.return_value = False
        self.assertFalse(self.cmd.run())

    def test_fill_definitions(self):

        def test_input(seffect):
            with mock.patch('__builtin__.raw_input', side_effect=seffect):
                self.cmd.fill_definitions()
                validate(
                    self.cmd.post_data['definitions'], self.definitions_schema
                )
        seffect = [
            "ping", "www.test.test", "4", "pint to test", "y",
            "additional_opt", "additional_opt_value", "n"
        ]
        test_input(seffect)
        seffect = [
            "traceroute", "www.test.test", "UDP", "4", "pint to test",
            "y", "additional_opt", "additional_opt_value", "n"
        ]
        test_input(seffect)
        seffect = [
            "traceroute", "www.test.test", "UDP", "4", "pint to test", "n"
        ]
        test_input(seffect)
        seffect = [
            "ping", "www.test.test", "4", "pint to test", "y",
            "additional_opt", "additional_opt_value"
        ]
        self.assertRaises(StopIteration, lambda: test_input(seffect))

    def test_get_meta_data(self):
        response = {
            "all_scheduling_requests_fulfilled": True,
            "result": "dummy_url"
        }
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            res = self.cmd.get_meta_data()
            self.assertTrue(isinstance(res[0], bool))
            self.assertTrue(isinstance(res[1], unicode))

        response = {"result": "dummy_url"}
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertFalse(self.cmd.get_meta_data())

        response = {"all_scheduling_requests_fulfilled": True}
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertFalse(self.cmd.get_meta_data())

        response = {}
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertFalse(self.cmd.get_meta_data())

    def test_get_results(self):
        self.cmd.results_url = "dummy_url"
        self.cmd.msm_id = 100000
        response = {}
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertFalse(self.cmd.get_results())

        response = {"results": []}
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertTrue(self.cmd.get_results())

        response = {"results": []}
        self.cmd.parser_options.store = True
        io = StringIO(json.dumps(response))
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertTrue(self.cmd.get_results())
            fpath = "results.%d.json" % self.cmd.msm_id
            file_results = open(fpath).read()
            try:
                self.assertEqual(file_results, json.dumps(response))
            finally:
                os.remove(fpath)
