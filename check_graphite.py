#!/usr/bin/env python

"""Nagios/Icinga plugin to check graphite metrics"""

import argparse
import logging
import nagiosplugin
import requests
import subprocess

_log = logging.getLogger('nagiosplugin')


# data acquisition

class Metric(nagiosplugin.Resource):

    def __init__(self, url, metric, fromarg):
	self.url = url
        self.metric = metric
	self.fromarg = fromarg

    def probe(self):
        _log.info('getting value for metric %s' % self.metric)
        url='%s/render/?target=%s&from=-%s&format=json' % (self.url, self.metric, self.fromarg)
	r = requests.get(url)
	try:
            values = r.json()[0]["datapoints"]
	    value = long(filter(lambda x: x[0], values)[-1][0])
	except:
            raise 
        _log.debug('value for %s: %d' % (self.metric, value))
	yield nagiosplugin.Metric(self.metric, value, min=0, context='metric')

# runtime environment and data evaluation

@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-w', '--warning', metavar='RANGE', default='',
                      help='return warning if load is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='',
                      help='return critical if load is outside RANGE')
    argp.add_argument('-f', '--fromarg', default='10minutes',
                      help='metric range')
    argp.add_argument('-m', '--metric', help='graphite metric name')
    argp.add_argument('-u', '--url', help='graphite url')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    args = argp.parse_args()
    check = nagiosplugin.Check(
        Metric(args.url, args.metric, args.fromarg),
        nagiosplugin.ScalarContext('metric', args.warning, args.critical),
        nagiosplugin.Summary())
    check.main(verbose=args.verbose)

if __name__ == '__main__':
    main()
