import time
import json
from optparse import make_option

from create import Command as CreateCommand


class Command(CreateCommand):

    # Global options from parent class
    help = 'Creates one oneoff UDM and waits for the results.'
    options = [
        make_option(
            '-f', '--file', type='string', dest='key_file',
            help='File containing api key.'
        ),
        make_option(
            '-s', '--store', action='store_true', default=False,
            dest='store', help=(
                'store the results to results.<udm_id>.json file'
            )
        ),
    ]

    def run(self):
        '''
        Main function that collects all users information from stdin, creates a
        oneoff UDM and fetches results.
        '''
        super(Command, self).run()
        if not self.msm_id:
            return False

        sleep_time = 20
        print (
            'Sleeping for %d secs in order to give some time to Atlas '
            'to produce data...'
        ) % sleep_time
        time.sleep(sleep_time)

        retries = 3
        timeout = 10
        self.results_url = None
        for i, _ in enumerate(range(0, retries)):
            meta = self.get_meta_data()
            if not meta:
                print("We couldn't get meta data for te new measurement.")
                return False
            scheduling_complete = meta[0]
            self.results_url = meta[1]
            if not scheduling_complete:
                msg = (
                    "RIPE Atlas scheduling seems to be on process, sleeping "
                    "for 5 more secs."
                )
                print msg
                time.sleep(timeout)
        if self.results_url:
            self.get_results()

    def fill_definitions(self):
        """Fill definitions structure from user input."""

        definitions = {}
        self.measurement_type = definitions["type"] = self.get_type()
        definitions["target"] = self.get_target()
        if self.measurement_type == 'traceroute':
            definitions["protocol"] = self.get_type_protocol()
        definitions["af"] = self.get_ip_version()
        definitions["description"] = self.get_description()
        self.is_oneoff = definitions["is_oneoff"] = True
        additional_options = self.get_additional_options()
        if additional_options:
            definitions.update(additional_options)
        self.post_data['definitions'] = [definitions]

    def get_meta_data(self):
        """
        Get url of the results and all_scheduling_requests_fulfille parameter,
        which indicates if Atlas scheduling process is finished.
        """
        url_meta = (
            '%s/api/v1/measurement/%s/?fields=probes,result,'
            'all_scheduling_requests_fulfilled'
        ) % (self.server, self.msm_id)

        metadata = self.http_get(url_meta)
        if not metadata:
            return False

        results_url = '%s%s' % (self.server, metadata['result'])

        return (metadata['all_scheduling_requests_fulfilled'], results_url)

    def get_results(self):
        '''
        Get results for the OneOff. If option is specified save it to a txt
        file.
        '''
        results = self.http_get(self.results_url)
        if not results:
            return
        print 'Got %d results for UDM id: %d.' % (len(results), self.msm_id)
        if self.parser_options.store:
            print 'Writing results to results.%d.json...' % self.msm_id
            open('results.%d.json' % self.msm_id, 'w').write(
                json.dumps(results)
            )
        else:
            print 'Results follow:\n%s' % results
