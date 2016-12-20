#!/usr/bin/python

from random import SystemRandom

r = SystemRandom()

for i in range(32):
	n = r.randint(0, 0xFFFFFFFF)
	print("{0:08x}".format(n))
