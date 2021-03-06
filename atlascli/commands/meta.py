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
    url_path = '/api/v1/measurement/%d/'

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
        print 'UDM #%d has the following metadata:\n%s' % (
            self.parser_options.msm_id, results
        )
