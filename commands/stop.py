import urllib2
import traceback
from optparse import make_option

from . import AtlasCommand


class Command(AtlasCommand):

    # Global options from parent class
    help = 'Stop a UDM.'
    options = [
        make_option(
            '-f', '--file', type='string', dest='key_file',
            help='File containing api key.'
        ),
        make_option(
            '-i', '--id', action='append',
            type='int', dest='msm_ids', default=[],
            help='UDM id(s). This can be multiple values separated by commas.'
        ),
    ]

    # Local option for this class
    url_path = '/api/v1/measurement/'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        if not self.parser_options.help_text:
            self._initialize()

    def _initialize(self):
        if not self.parser_options.msm_ids:
            print 'You have to specify at least one measurement id.'
            self.safe_options = False
            return

        self.msm_ids = self.parser_options.msm_ids

        if not self.parser_options.key_file:
            print 'You have to specify the file that holds your api key.'
            self.safe_options = False
            return
        try:
            f = open(self.parser_options.key_file, 'r')
            self.key = f.read().strip()
        except:
            print traceback.format_exc()
            print 'Error while reading configuration'

    def run(self):
        for msm_id in self.msm_ids:
            url = '%s%s%d/?key=%s' % (self.server, self.url_path, msm_id, self.key)
            response = self.http_delete(url)
            if response:
                if response[0] / 100 == 2:
                    print 'UMD: #%s was stopped successfully.' % msm_id
                else:
                    print 'UMD: #%s was not stopped successfully. Return with HTTP code: %d and msg: %s' % (
                        msm_id, response[0], response[1]
                    )

    def http_delete(self, url):
        '''
        Fuction that implements a http delete give a url.
        '''
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.get_method = lambda: 'DELETE'
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            print "HTTP ERROR %d: %s <%s>" % (e.code, e.msg, e.read())
        except:
            print 'Problem with HTTP request (url: %s).' % url
            print traceback.format_exc()
        finally:
            return False

        return (response.code, response.msg)
