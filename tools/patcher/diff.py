#!/usr/bin/env python

# This file just finds the hex differences between two firmware binaries. Helpful for firmware disassembly.

from intelhex import IntelHex
import sys


def find_diff(x, y):
	diff = False
	start = 0
	for i in range(0x9d000000, 0x9d040000):
	    a, b = x[i - 0x80000000], y[i - 0x80000000]
	    if not diff and a != b:
	    	diff = True
	    	start = i
	    elif diff and a == b:
	    	diff = False
	    	print('%08X - %08X (%d bytes)' % (start, i, i - start))

if __name__ == '__main__':
	if len(os.argv) < 3:
		print('Usage: {} <firmware 1> <firmware 2>'.format(os.argv[0]))
		exit(1)

	v0 = IntelHex()
	v0.loadhex(os.argv[1])
	v1 = IntelHex()
	v1.loadhex(os.argv[2])

	find_diff(v0, v1)