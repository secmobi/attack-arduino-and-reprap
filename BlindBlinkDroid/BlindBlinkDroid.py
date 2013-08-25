#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Demo of automatically tamper Arduino's firmware through USB cable
# Author: Claud Xiao <secmobi@gmail.com>

import sys
from IHex import *


def Log(str):
    print '[+] ' + str + '\n'


def ErrorAndExit(str):
    print 'ERROR: ' + str + ' QUIT!\n'
    sys.exit(-1)


def FindFunction(asm):
    impl = ''
    calls = []
    result = []

    insts = []
    for line in open(asm, 'r').readlines()[7:]:
        pos = line[:8].strip()
        opcode = line[10:22].strip()
        ass = line[23:].split(';')[0].strip()
        insts.append((pos, opcode, ass))

    blocks = []
    begin = 0
    for i in range(len(insts)):
        if insts[i][2] == 'ret':
            blocks.append((begin, i))
            begin = i + 1
            if begin >= len(insts): break

    for block in blocks:
        status = 0

        if impl != '': break

        # low quality signature with inefficiency matching method
        for pos, opcode, ass in insts[block[0]:block[1]+1]:
            if status == 0 and opcode == '82 55': status = 1
            elif status == 1 and opcode == '9f 4f': status = 2
            elif status == 2 and opcode == '86 56': status = 3
            elif status == 3 and opcode == '9f 4f': status = 4
            elif status == 4 and opcode == '4a 57': status = 5
            elif status == 5 and opcode == '5f 4f': status = 6
            elif status == 6: # rjmp to ret
                ops = opcode.split(' ')
                target = '%x' % (int(pos, 16) + int(ops[0], 16) * 2 + 2)
                if len(ops) == 2 and ops[1] == 'c0' and target == insts[block[1]][0]:
                    status = 7
            elif status == 7 and opcode.split(' ')[1] == '30': status = 8
            elif status == 8 and opcode.split(' ')[1] == '30': status = 9
            elif status == 9 and opcode.split(' ')[1] == '30': status = 10 
            elif status == 10 and opcode.split(' ')[1] == '30': status = 11
            elif status == 11 and opcode.split(' ')[1] == '30': status = 12
            elif status == 12 and opcode.split(' ')[1] == '30': status = 13
            elif status == 13 and opcode.split(' ')[1] == '30': status = 14
            elif status == 14 and opcode == 'f8 94': status = 15
            elif status == 15 and opcode.split(' ')[1] == '23': status = 16
            elif status == 16 and opcode.split(' ')[1] == '2b': status = 17

        if status == 17:
            impl = insts[block[0]][0]
            break;

    if impl == '':
        ErrorAndExit('couldn\'t find *digitalWrite*')

    i = 0
    for pos, opcode, ass in insts:
        if ass == 'call\t0x' + impl:
            calls.append(pos)

            for pos, opcode, ass in insts[i-2:i]:
                if not ass.startswith('ldi'): continue
                if ass.endswith('01'):
                    result.append(pos)

        i = i + 1

    return impl, calls, result


def FixHex(origin, target, addrs):
    f = open(target, 'w')

    for line in open(origin, 'r').readlines():
        line = line.strip()
        start_code = line[0]
        byte_count = int(line[1:3], 16)
        start_addr = int(line[3:7], 16)
        record_type = line[7:9]

        if start_code != ':' or ((byte_count * 2 + 11) != len(line)):
            ErrorAndExit('broken ihex file')

        if record_type == '00':
            for addr in addrs:
                addr = int(addr, 16)
                if start_addr <= addr and addr < (start_addr + byte_count):
                    offset = 8 + 2 * (addr - start_addr) + 2
                    newline = line[:offset] + '0' + line[offset+1:-2]
                    line = newline + HexChecksum(newline[1:])

            f.write(line + '\n')
        elif record_type == '01':
            f.write(line)
            break
        else:
            ErrorAndExit('unimplemented record type' + record_type)

    f.close()


def BlindBlink():
    origin_hex = 'dump.hex'
    origin_bin = 'dump.bin'
    origin_asm = 'dump.asm'
    fixed_hex = 'fixed.hex'

    impl, calls, addrs = FindFunction(origin_asm)
    Log('Found implementation of digitalWrite at 0x' + impl)

    if len(calls) > 0:
        Log('Found %d calls to digitalWrite at %s' % (len(calls), repr(calls)))
    else:
        ErrorAndExit('didn\'t find any call to digitalWrite')

    if len(addrs) > 0:
        Log('Found %d calls need to be fixed' % len(addrs))
    else:
        ErrorAndExit('didn\'t find any calls need to be fixed')
        return

    Log('Fix the dump to ' + fixed_hex)
    FixHex(origin_hex, fixed_hex, addrs)


if __name__ == '__main__':
    BlindBlink()
