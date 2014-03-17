import json
from optparse import make_option

from . import AtlasCommand


class Command(AtlasCommand):

    # Global options from parent class
    help = 'Fetch results for specific RIPE Atlas UDM.'

    options = [
        make_option(
            '-i', '--id', type='int', dest='msm_id',
            help='UDM id.'
        ),
        make_option(
            '-s', '--store', action='store_true', default=False,
            dest='store', help=(
                'store the results to results.<udm_id>.json file'
            )
        ),
    ]

    # Local option for this class
    url_path = '/api/v1/measurement/%s/result/'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        if not self.parser_options.help_text:
            self._initialize()

    def _initialize(self):
        if not self.parser_options.msm_id:
            print 'You have to specify the measurement id.'
            self.safe_options = False
            return
        self.url = '%s%s' % (
            self.server, self.url_path % self.parser_options.msm_id
        )

    def run(self):
        results = self.http_get(self.url)
        if not results:
            return
        print 'Got %d results for UDM id: %d.' % (
            len(results), self.parser_options.msm_id
        )
        if self.parser_options.store:
            msg = (
                'Writing results to results.%d.json...'
            ) % self.parser_options.msm_id
            print msg
            open('results.%d.json' % self.parser_options.msm_id, 'w').write(
                json.dumps(results)
            )
        else:
            print 'Results follow:\n%s' % results
