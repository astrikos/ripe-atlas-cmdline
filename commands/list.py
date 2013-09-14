import traceback
from optparse import make_option

from . import AtlasCommand


class Command(AtlasCommand):

    help = (
        'Fetch list of available UDMs. Capable of filtering and returning '
        'specific only field'
    )

    options = [
        make_option(
            '-f', '--file', type='string', dest='key_file',
            help='File containing api key. Specifing this option will fetch only UDMs belonging to you.'
        ),
        make_option(
            '-t', '--flat', action='store_true', default=False,
            dest='flat', help='Gives back a flat list of msm_ids.'
        ),
    ] 

    url_path = '/api/v1/measurement/'


    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        if not self.parser_options.help_text:
            self._initialize()

    def _initialize(self):
        '''
        Holds different stuff that we should do in init but we'd rather keep
        __init__ clean.
        '''
        try:
            f = open(self.parser_options.key_file, 'r')
            self.key = f.read()
        except:
            print traceback.format_exc()
            print 'Error while reading configuration'

    def run(self):
        self.stdin_options()
        url = '%s%s' % (self.server, self.url_path)
        if self.key:
            url = '%s?key=%s' % (url, self.key)
        url_query = ''
        for f, v in self.filters.items():
            if not url_query:  # first filter
                url_query = '?%s=%s' % (f, v)
            else:
                url_query = '%s&%s=%s' % (url_query, f, v)

        if self.fields:
            if url_query:
                url_query = '%s&fields=%s' % (url_query, ','.join(self.fields))
            else:
                url_query = '?fields=%s' % (','.join(self.fields))


        url = '%s%s%s' % (self.server, self.url_path, url_query)
         
        results = self.http_get(url)
        if not results:
            return

        full_results = not bool(self.parser_options.flat)
        if self.parser_options.flat:
            try:
                print ','.join(map(str, [k['msm_id'] for k in results['objects']]))
            except:
                full_results = True

        if full_results:
            print 'The list of the fetched UDMs follows:\n%s' % (results)

    def stdin_options(self):
        '''
        Collects from stdin filter options and desired fields.
        '''
        # filters part
        self.filters = {}
        if raw_input('Do you want any filter [y/n]:') == 'y':
            while True:
                option = raw_input('Specify filter:')
                value = raw_input('Specify value:')
                self.filters[option] = value
                if raw_input('More [y/n]:') == 'y':
                    continue
                else:
                    break
        # fields part
        self.fields = []
        if raw_input('Do you want to specify any field (Otherwise you will get all) [y/n]:') == 'y':
            while True:
                field = raw_input('Specify field:')
                self.fields.append(field)
                if raw_input('More [y/n]:') == 'y':
                    continue
                else:
                    break
