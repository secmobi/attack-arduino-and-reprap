#!/usr/bin/env python

import sys
import subprocess


DEBUG = False

def RunCmd(cmd):
    output = subprocess.check_output([cmd], stderr=subprocess.STDOUT, shell=True)
    if DEBUG:
	print '[-] Cmd: ' + cmd + '\n' + output


def Log(str):
    print '[+] ' + str + '\n'


def ErrorAndExit(str):
    print 'ERROR: ' + str + ' QUIT!\n'
    sys.exit(-1)

