#!/system/bin/sh

export PATH=$PATH:/data/data/jackpal.androidterm/local/bin

echo "[+] Download firmware from the board to dump.hex"
echo ""

avrdude -C /data/data/jackpal.androidterm/local/bin/avrdude.conf -p atmega328p -c arduino -P /dev/ttyACM0 -U flash:r:dump.hex:i

echo "[+] Convert the dump to dump.bin"
echo ""

sh python.sh Hex2Bin.py dump.hex dump.bin

echo "[+] Disassemble the binary code to dump.asm"
echo ""
avr-objdump -D -b binary -mavr5 dump.bin > dump.asm

sh python.sh BlindBlinkDroid.py

echo "[+] Upload fixed firmware to the board"
echo ""
avrdude -C /data/data/jackpal.androidterm/local/bin/avrdude.conf -p atmega328p -c arduino -P /dev/ttyACM0 -U flash:w:fixed.hex:i

echo "[+] Done!"
echo ""
