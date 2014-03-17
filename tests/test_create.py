#from __future__ import absolute_import
import unittest
from StringIO import StringIO
import urllib2

import mock
from jsonschema import validate

from atlascli.commands.create import Command as CreateCommand
from atlascli.commands.create import InvalidEntry


class UnitTestCreate(unittest.TestCase):

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
                    "interval": {
                        "type": "integer",
                    },
                }
            }
        }
        self.probes_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["requested", "type", "value"],
                "properties": {
                    "requested": {
                        "type": "integer",
                    },
                    "type": {
                        "type": "string",
                        "enum": [
                            "area", "country", "prefix", "asn", "probes", "msm"
                        ]
                    },
                    "value": {
                        "type": "string",
                    },
                }
            }
        }
        self.post_data_schema = {
            "type": "object",
            "required": ["definitions", "probes"],
            "properties": {
                "definitions": self.definitions_schema,
                "start_time": {"type": "integer"},
                "end_time": {"type": "integer"},
                "probes": self.probes_schema
            }
        }
        args = ["-f", "tests/test_api_key", "-p", "test_file1"]
        self.cmd = CreateCommand(args)

    def test_get_api_key(self):
        with mock.patch('__builtin__.open', return_value=StringIO('api_key')):
            self.assertEqual(self.cmd.get_api_key(), "api_key")
        self.cmd.parser_options.key_file = "testing"
        self.assertEqual(self.cmd.get_api_key(), False)
        self.cmd.parser_options.key_file = False
        with mock.patch('__builtin__.raw_input', return_value=""):
            self.assertEqual(self.cmd.get_api_key(), False)

    def test_run(self):
        self.cmd.parser_options.post_data_file = "test"
        with mock.patch('__builtin__.open', return_value=StringIO('{}')):
            seffect = urllib2.HTTPError(
                "test_url", 500, StringIO("Server is down"),
                StringIO('testing'), StringIO('testing')
            )
            with mock.patch('urllib2.urlopen', side_effect=seffect):
                self.assertEqual(self.cmd.run(), False)

        self.cmd.parser_options.post_data_file = None
        definitions = [
            "ping", "www.test.test", "4", "pint to test", "n", "500",
            "y", "additional_opt", "additional_opt_value", "n"
        ]
        times = ["", "12345677"]
        probes = ["50", "asn", "3333"]
        side_effect = definitions + times + probes
        seffect = side_effect + ['y']
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            io = StringIO('{ "measurements": [ 123456789, 123456790 ] }')
            with mock.patch('urllib2.urlopen', return_value=io):
                self.assertEqual(self.cmd.run(), True)
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            io = StringIO('{ "measurements": 123456790}')
            with mock.patch('urllib2.urlopen', return_value=io):
                self.assertEqual(self.cmd.run(), False)
        seffect = side_effect + ['n']
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            self.assertEqual(self.cmd.run(), True)

    def test_get_type(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_type())
        for mtype in ('ping', 'traceroute', 'dns', 'sslcert'):
            with mock.patch('__builtin__.raw_input', return_value=mtype):
                self.assertEqual(self.cmd.get_type(), mtype)

    def test_get_target(self):
        self.cmd.measurement_type = "ping"
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            assert isinstance(self.cmd.get_target(), str)
        with mock.patch('__builtin__.raw_input', return_value=""):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_target())
        self.cmd.measurement_type = "dns"
        with mock.patch('__builtin__.raw_input', return_value=''):
            assert isinstance(self.cmd.get_target(), str)

    def test_get_type_protocol(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(
                InvalidEntry, lambda: self.cmd.get_type_protocol()
            )
        for protocol in ("UDP", "TCP", "ICMP"):
            with mock.patch('__builtin__.raw_input', return_value=protocol):
                self.assertEqual(self.cmd.get_type_protocol(), protocol)

    def test_get_ip_version(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_ip_version())
        for protocol in ("4", "6"):
            with mock.patch('__builtin__.raw_input', return_value=protocol):
                self.assertEqual(self.cmd.get_ip_version(), int(protocol))

    def test_get_description(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            assert isinstance(self.cmd.get_description(), str)
        with mock.patch('__builtin__.raw_input', return_value=""):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_description())

    def test_get_is_oneoff(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_is_oneoff())
        with mock.patch('__builtin__.raw_input', return_value="y"):
            self.assertEqual(self.cmd.get_is_oneoff(), True)
        with mock.patch('__builtin__.raw_input', return_value="n"):
            self.assertEqual(self.cmd.get_is_oneoff(), False)

    def test_get_interval(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_interval())
        with mock.patch('__builtin__.raw_input', return_value='0'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_interval())
        with mock.patch('__builtin__.raw_input', return_value='300'):
            self.assertEqual(self.cmd.get_interval(), 300)
        with mock.patch('__builtin__.raw_input', return_value=''):
            self.assertEqual(self.cmd.get_interval(), '')

    def test_get_additional_options(self):
        with mock.patch('__builtin__.raw_input', return_value='n'):
            assert self.cmd.get_additional_options() == {}
        with mock.patch('__builtin__.raw_input', side_effect=['y', '']):
            assert self.cmd.get_additional_options() == {}
        seffect = ['y', 'option', 'value', 'n']
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            assert self.cmd.get_additional_options() == {'option': 'value'}
        seffect = ['y', 'option', 'value', 'y', 'option1', 'value1', 'n']
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            expected = {'option': 'value', 'option1': 'value1'}
            assert self.cmd.get_additional_options() == expected

    def test_fill_definitions(self):

        def test_input(seffect):
            with mock.patch('__builtin__.raw_input', side_effect=seffect):
                self.cmd.fill_definitions()
                validate(
                    self.cmd.post_data['definitions'], self.definitions_schema
                )
        seffect = [
            "ping", "www.test.test", "4", "pint to test", "n", "500", "y",
            "additional_opt", "additional_opt_value", "n"
        ]
        test_input(seffect)
        seffect = [
            "traceroute", "www.test.test", "UDP", "4", "pint to test", "y",
            "y", "additional_opt", "additional_opt_value", "n"
        ]
        test_input(seffect)
        seffect = [
            "ping", "www.test.test", "4", "pint to test", "n", "500", "y",
            "additional_opt", "additional_opt_value"
        ]
        self.assertRaises(StopIteration, lambda: test_input(seffect))

    def test_get_start_time(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_start_time())
        with mock.patch('__builtin__.raw_input', return_value='0'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_start_time())
        with mock.patch('__builtin__.raw_input', return_value='300'):
            self.assertEqual(self.cmd.get_start_time(), 300)
        with mock.patch('__builtin__.raw_input', return_value=''):
            self.assertEqual(self.cmd.get_start_time(), '')

    def test_get_end_time(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_end_time())
        with mock.patch('__builtin__.raw_input', return_value='0'):
            self.assertRaises(InvalidEntry, lambda: self.cmd.get_end_time())
        with mock.patch('__builtin__.raw_input', return_value='300'):
            self.assertEqual(self.cmd.get_end_time(), 300)
        with mock.patch('__builtin__.raw_input', return_value=''):
            self.assertEqual(self.cmd.get_end_time(), '')

    def test_fill_times(self):
        self.cmd.is_oneoff = True
        with mock.patch('__builtin__.raw_input', side_effect=['', '12345677']):
            self.cmd.fill_times()
            assert 'end_time' not in self.cmd.post_data
            assert 'start_time' not in self.cmd.post_data

        self.cmd.is_oneoff = False
        with mock.patch('__builtin__.raw_input', side_effect=['', '12345677']):
            self.cmd.fill_times()
            assert 'start_time' not in self.cmd.post_data
            assert self.cmd.post_data['end_time'] == 12345677

        with mock.patch('__builtin__.raw_input', side_effect=['12', '123456']):
            self.cmd.fill_times()
            assert self.cmd.post_data['start_time'] == 12
            assert self.cmd.post_data['end_time'] == 123456

    def test_get_probes_number(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(
                InvalidEntry, lambda: self.cmd.get_probes_number()
            )
        with mock.patch('__builtin__.raw_input', return_value='0'):
            self.assertRaises(
                InvalidEntry, lambda: self.cmd.get_probes_number()
            )
        with mock.patch('__builtin__.raw_input', return_value='300'):
            self.assertEqual(self.cmd.get_probes_number(), 300)
        with mock.patch('__builtin__.raw_input', return_value='-1'):
            self.assertRaises(
                InvalidEntry, lambda: self.cmd.get_probes_number()
            )

    def test_get_probes_source_type(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            self.assertRaises(
                InvalidEntry, lambda: self.cmd.get_probes_source_type()
            )
        for source in ("area", "country", "prefix", "asn", "probes", "msm"):
            with mock.patch('__builtin__.raw_input', return_value=source):
                self.assertEqual(self.cmd.get_probes_source_type(), source)

    def test_get_probes_source_value(self):
        with mock.patch('__builtin__.raw_input', return_value='dummy_string'):
            assert isinstance(self.cmd.get_probes_source_value(), str)
        with mock.patch('__builtin__.raw_input', return_value=""):
            self.assertRaises(
                InvalidEntry, lambda: self.cmd.get_probes_source_value()
            )

    def test_fill_probes(self):
        seffect = ["500", "asn", "3333"]
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            self.cmd.fill_probes()
            validate(
                self.cmd.post_data['probes'], self.probes_schema
            )

    def test_stdin_options(self):
        definitions = [
            "ping", "www.test.test", "4", "pint to test", "n", "500",
            "y", "additional_opt", "additional_opt_value", "n"
        ]
        times = ["", "12345677"]
        probes = ["50", "asn", "3333"]
        seffect = definitions + times + probes
        with mock.patch('__builtin__.raw_input', side_effect=seffect):
            self.cmd.data_from_stdin()
            validate(
                self.cmd.post_data, self.post_data_schema
            )

    def test_create(self):
        io = StringIO('{ "measurements": [ 123456789, 123456790 ] }')
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertEqual(self.cmd.create(), 123456789)

        io = StringIO('{ "measurements": 123456789 }')
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertEqual(self.cmd.create(), False)

        io = StringIO('{ "testing": 123456789 }')
        with mock.patch('urllib2.urlopen', return_value=io):
            self.assertEqual(self.cmd.create(), False)
        seffect = urllib2.HTTPError(
            "test_url", 500, StringIO("Server is down"),
            StringIO('testing'), StringIO('testing')
        )
        with mock.patch('urllib2.urlopen', side_effect=seffect):
            print self.cmd.create()
