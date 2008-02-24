#!/usr/bin/python

import os, sys, optparse
import tic

def parse_args():
	parser = optparse.OptionParser()
	parser.add_option('-d', '--inbound')
	parser.add_option('-a', '--areas')
	parser.add_option('-l', '--list')
	parser.add_option('-i', '--import')

	opts, args = parser.parse_args()
	return opts,args

def main ():
	opts, args = parse_args()

	for item in [x for x in os.listdir(opts.inbound) if x.endswith('.TIC')]:
		t = tic.TIC(os.path.join(opts.inbound, item))
		if t.valid:
			print '%(area)s/%(file)s from %(origin)s: %(desc)s' % t

if __name__ == '__main__': main()

