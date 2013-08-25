
import sys
from IHex import Hex2Bin

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: ' + __file__ + '<hex> <bin>'
        sys.exit(-1)

    Hex2Bin(sys.argv[1], sys.argv[2])

