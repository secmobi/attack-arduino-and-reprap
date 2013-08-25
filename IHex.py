#!/usr/bin/env python


def HexChecksum(line):
    if len(line) % 2 != 0:
        ErrorAndExit('broken ihex record: ' + line)
    
    checksum = 0
    for i in range(0, len(line), 2):
        c = int(line[i:i+2], 16)
        checksum = checksum + c

    checksum = (((checksum % 0x100) ^ 0xff) + 1) % 0x100
    checksum = '%02X' % checksum
    return checksum


def Hex2Bin(ihex, raw):
    rawdata = ''

    for line in open(ihex, 'r').readlines():
        line = line.strip()
        start_code = line[0]
        byte_count = int(line[1:3], 16)
        record_type = line[7:9]

        if start_code != ':' or ((byte_count * 2 + 11) != len(line)):
            ErrorAndExit('broken ihex file')

        if record_type == '00':
            for i in range(byte_count):
                rawdata = rawdata + chr(int(line[9 + i * 2:11 + i * 2], 16))
        elif record_type == '01':
            break
        elif record_type == '04':
            continue
        else:
            ErrorAndExit('unimplemented record type' + record_type)

    open(raw, 'wb').write(rawdata)


def Bin2Hex(raw, ihex):
    hexfile = open(ihex, 'w')

    rawdata = open(raw, 'rb').read()
    rawlen = len(rawdata)

    segidx = 0
    seglen = 0
    while rawlen - segidx * 0x10000 > 0:
        if segidx > 0:
            line = ':02000004%04X' % segidx
            line = line + HexChecksum(line[1:])
            hexfile.write(line+'\n')

        if (rawlen - segidx * 0x10000) >= 0x10000:
            seglen = 0x10000
        else:
            seglen = rawlen - segidx * 0x10000

        idx = 0
        while idx < seglen:
            if seglen - idx >= 0x20:
                step = 0x20
            else:
                step = seglen - idx
            line = ':%02X%04X00' % (step, idx)

            begin = segidx * 0x10000 + idx
            end = begin + step
            data = rawdata[begin:end]

            for i in range(step):
                line = '%s%02X' % (line, ord(data[i]))
        
            checksum = HexChecksum(line[1:])
            line = line + checksum

            hexfile.write(line+'\n')
            idx = idx + step

        segidx = segidx + 1

    endline = ':00000001FF\n'
    hexfile.write(endline)

    hexfile.close()

