import json
import urllib2
from optparse import make_option

from . import AtlasCommand


class Command(AtlasCommand):

    # Global options from parent class
    help = 'Fetch meta data for specific RIPE Atlas UDM.'
    options = [
        make_option(
            '-i', '--id', type='int', dest='msm_id',
            help='UDM id.'
        ),
    ]

    # Local option for this class
    url = 'https://atlas.ripe.net/api/v1/measurement/%s/?fields='

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        if not self.parser_options.help_text:
            self._initialize()

    def _initialize(self):
        if not self.parser_options.msm_id:
            print 'You have to specify the measurement id.'
            self.safe_options = False
            return

    def run(self):
        url = self.url % self.parser_options.msm_id
        results = self.http_get(url)
        if not results:
            return
        print 'UDM #%d has the following metadata:\n%s' % (
            self.parser_options.msm_id, results
        )
