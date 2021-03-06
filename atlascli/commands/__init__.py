import urllib2
import json
import pkgutil
from optparse import OptionParser, make_option


class AtlasCommand(object):
    help = ""
    options = []

    def __init__(self, sys_args):
        self.server = "https://atlas.ripe.net"
        basic_options = [
            make_option(
                "--help_text", action="store_true", dest="help_text",
                help="shows a small description of what the command is about"
            ),
        ]
        fin_options = basic_options + self.options
        parser = OptionParser(
            "usage: atlas_manage.py command [options]",
            option_list=fin_options
        )

        (self.parser_options, _) = parser.parse_args(sys_args)
        self.safe_options = True
        if self.parser_options.help_text:
            print self.help

    def run(self):
        print "Available commands:"
        paths = ["./atlascli/commands"]
        for _, package_name, _ in pkgutil.iter_modules(paths):
            print package_name

    def http_get(self, url):
        """
        Common function that implements a http get given a url
        """
        req = urllib2.Request(url)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError as exc:
            log = "HTTP ERROR %d: %s <%s>" % (exc.code, exc.msg, exc.read())
            print log
            return False
        data = json.load(response)
        return data
