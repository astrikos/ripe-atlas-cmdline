import time
import json
from optparse import make_option

from create import Command


class Command(Command):

    # Global options from parent class
    help = 'Creates one oneoff UDM and waits for the results.'
    options = [
        make_option(
            '-f', '--file', type='string', dest='key_file',
            help='File containing api key.'
        ),
        make_option(
            '-s', '--store', action='store_true', default=False,
            dest='store', help='store the results to results.<udm_id>.json file'
        ),
    ]

    # Local option for this class
    sleep_time = 10

    def run(self):
        '''
        Main function that collects all users information from stdin, creates a
        oneoff UDM and fetches results.
        '''
        try:
            self.stdin_options()
            if not self.is_oneoff:
                print 'UDM has to be a OneOff. Exiting!'
                return
            confirm_msg = (
                'You are about to create a new oneoff RIPE Atlas UDM with the'
                ' following details:\n%s\n[y/n]:'
            ) % self.post_data
            if raw_input(confirm_msg) == 'y':
                self.msm_id = self.create()
                if not self.msm_id:
                    return
                print 'A new oneoff UDM just created with id: %d' % self.msm_id
            else:
                print 'Just exiting.'
                return
        except KeyboardInterrupt:
            return

        # If all good with the creation of measurement
        # adjust sleep time
        if self.probes_number > 300 and self.probes_number < 1000:
            self.sleep_time = 15
        elif self.probes_number > 1000:
            self.sleep_time = 20
        print (
            'Sleeping for %d secs in order to give some time to Atlas '
            'to produce data...'
        ) % self.sleep_time
        time.sleep(self.sleep_time)
        if self.get_probes_number():
            self.get_results()

    def get_probes_number(self):
        '''
        Try to get the number of probes that were used for this OneOff. Using
        all_scheduling_requests_fulfille parameter in the meta response we can 
        be sure when the allocated probes number is the final.
        '''
        url_meta = '%s/api/v1/measurement/%s/?fields=probes,result,all_scheduling_requests_fulfilled' % (self.server, self.msm_id)
        tries = 5
        for i, _ in enumerate(range(0, tries)):
            metadata = self.http_get(url_meta)
            if not metadata:
                return False
            if metadata['all_scheduling_requests_fulfilled']:
                break
            else:
                if i + 1 >= tries:
                    break
                print "RIPE Atlas scheduling seems to be on process, sleeping for 5 more secs."
                time.sleep(5)
        self.nprobes = len(metadata['probes'])
        self.url_results = '%s%s' % (self.server, metadata['result'])

        return True

    def get_results(self):
        '''
        Get results for the OneOff. If option is specified save it to a txt
        file.
        '''
        results = self.http_get(self.url_results)
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