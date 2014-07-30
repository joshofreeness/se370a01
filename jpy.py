#!/usr/bin/env python3

"""jpy.py: A python shell. Written by Joshua Free (jfre553 2646577)"""


import os

while (True):
	arg = input(os.getcwd() + "$> ")

	#Handle "PWD"
	#and stuff
	if(arg == "pwd"):
		print(os.getcwd())
		continue






