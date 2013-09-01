import json
import urllib2
import traceback
from distutils.util import strtobool
from optparse import make_option

from . import AtlasCommand


class Command(AtlasCommand):

    help = 'Create a new RIPE Atlas UDM.'
    url_path = '/api/v1/measurement/?key=%s'
    post_data = {}
    options = [
        make_option(
            '-f', '--file', type='string', dest='key_file',
            help='File containing api key.'
        ),
    ]

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        if not self.parser_options.help_text:
            self._initialize()

    def _initialize(self):
        '''
        Holds different stuff that we should do in init but we'd rather keep
        __init__ clean.
        '''
        if not self.parser_options.key_file:
            print 'You have to specify the file that holds your api key.'
            self.safe_options = False
            return
        try:
            f = open(self.parser_options.key_file, 'r')
            self.key = f.read()
            self.url = '%s%s' % (self.server, self.url_path % self.key)
        except:
            print traceback.format_exc()
            print 'Error while reading configuration'

    def run(self):
        '''
        Main function that collects all users information from stdin, and
        creates a new UDM.
        '''
        try:
            self.stdin_options()
            confirm_msg = (
                'You are about to create a new RIPE Atlas UDM with the '
                'following details:\n%s\n[y/n]:'
            ) % self.post_data
            if raw_input(confirm_msg) == 'y':
                msm_id = self.create()
                if msm_id:
                    print 'A new UDM just created with id: %d' % msm_id
            else:
                print 'Just exiting.'
        except KeyboardInterrupt:
            return

    def stdin_options(self):
        '''
        Collects from stdin all information that a user most likely wants to
        specify.
        '''
        # definitions part
        definitions = {}
        # --- required fields
        self.target = raw_input('Specify Target:')
        while not self.target:
            self.target = raw_input('Target is required:')
        definitions['target'] = self.target
        self.type = raw_input('Specify Type:')
        while not self.type:
            self.type = raw_input('Type is required:')
        definitions['type'] = self.type
        if self.type == 'traceroute':
            self.trace_protocol = raw_input('Specify  Traceroute Protocol[ICMP/UDP]:')
            definitions['protocol'] = self.trace_protocol
            while not self.trace_protocol:
                self.self.trace_protocol = raw_input('Protocol is required:')
                definitions['protocol'] = self.trace_protocol
        while True:
            try:
                self.af = int(raw_input('Specify Protocol[4/6]:'))
                if self.af not in (4, 6):
                    raise ValueError()
                break
            except ValueError:
                print 'Please specify 4 or 6.'
        definitions['af'] = self.af
        self.description = raw_input('Specify Description:')
        while not self.description:
            self.description = raw_input('Description is required:')
        definitions['description'] = self.description

        # --- non required fields
        try:
            self.is_oneoff = strtobool(raw_input('Is it OneOff [y/n]:'))
        except ValueError:
            print 'You make me sad :( I assume "n".'
            self.is_oneoff = False
        definitions['is_oneoff'] = 'true' if self.is_oneoff else 'false'
        if not self.is_oneoff:
            self.interval = raw_input('Specify Interval:')
            definitions['interval'] = self.interval
        if raw_input('Do you need any additional options [y/n]:') == 'y':
            additional_options = {}
            while True:
                option = raw_input('Specify option:')
                value = raw_input('Specify value:')
                additional_options[option] = value
                if raw_input('More [y/n]:') == 'y':
                    continue
                else:
                    break
            definitions.update(additional_options)
        self.post_data['definitions'] = [definitions]
        # times part
        self.start_time = raw_input(
            'Specify Start Time [Unix Timestamp\Leave blank for now]:'
        )
        if self.start_time != '':
            self.post_data['start_time'] = self.start_time
        if not self.is_oneoff:
            self.end_time = raw_input(
                'Specify End Time [Unix Timestamp\Leave blank for never]:'
            )
            if self.end_time != '':
                self.post_data['end_time'] = self.end_time
        # probes part
        probes = {}
        while True:
            try:
                self.probes_number = int(raw_input('Specify Number of Probes (Integer):'))
                break
            except ValueError:
                print 'Please specify a number.'
        probes['requested'] = self.probes_number
        self.probe_source_type = raw_input(
            'Specify Probes Source Type [area/country/prefix/asn/probes/msm]:'
        )
        probes['type'] = self.probe_source_type
        if self.probe_source_type == 'area':
            msg = (
                'Specify Probes Source [WW/West/North-Central/'
                'South-Central/North-East/South-East]:'
            )
        else:
            msg = 'Specify Probes Source:'
        self.probe_source = raw_input(msg)
        probes['value'] = self.probe_source
        self.post_data['probes'] = [probes]

    def create(self):
        '''
        Makes the http post that create the UDM itself.
        '''
        post_data = json.dumps(self.post_data)
        req = urllib2.Request(self.url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        try:
            response = urllib2.urlopen(req, post_data)
        except:
            print 'Problem with HTTP request.'
            print traceback.format_exc()
            return False
        response = json.load(response)
        return response['measurements'][0]
