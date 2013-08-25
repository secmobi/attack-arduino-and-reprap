# Three Demos of Attacking Arduino and RepRap 3D Printers

## About
These are three demos used in my presentation at XCON security conference 2013. Them demonstrate that Arduino-based devices, especially RepRap 3D printers, are very easy to attack through an USB cable connected PC or Android device. These attacks will change Arduino or RepRap's firmware and can be executed automatically.

## Author
Claud Xiao <secmobi@gmail.com>

## Warning
The HalfTemperature.py will rewrites your RepRap printer's firmware, makes its behaviour abnormal, and may physically breaks it. DO NOT run it unless you know exactly what you're doing!

## BlindBlink

The BlindBlink.py will download the 'Blink' firmware from Arduino Uno, find digitalWrite calls in it, changes their parameter from HIGH to LOW, and then upload the fixed firmware to Arduino Uno again. Thus, the 'Blink' will becomes 'Blind'.

It has been tested and works well under this environment:

* Arduino Uno board
* Arduino IDE 1.0.5
* The Blink example program

On other board, like Arduino Mega2560, or using other compiler, like Arduino IDE 0023, it won't works.

You will need to insure the avr-objdump and avrdude tools can be found in $PATH.

## BlindBlinkDroid

The BlindBlinkDroid is an Android version of BlindBlink. This means, you can connect the Arduino board with just an Android device with USB OTG capability and launches similiar attack from Android.

Besides of above requirements, you will need:

* An Android device, which support USB OTG model
* An USB OTG cable
* The Android system is rooted
* Install the Terminal Emulator application from: https://play.google.com/store/apps/details?id=jackpal.androidterm
* Install the Python for Android application from: http://code.google.com/p/python-for-android/
* Install the andavr toolchain from: https://code.google.com/p/andavr/

After connect Android device and Arduino Uno board with USB OTG cable and USB cable, push all files in the 'BlindBlinkDroid' folder into you Android phone, launch Terminal Emulator, get root permission by su, and run 'sh run.sh'.

## HalfTemperature

The HalfTemperature.py will downloads Sprinter firmware from RepRap 3D printer's Sanguinololu board, changes temperature related data in it, and upload the fixed firmware to RepRap. After finished these steps, the RepRap's hot end and print bed's actual work temperature will be the half of what you will see through any RepRap control software like Printrun.

The code will only works as expected under EXACTLY these environments:

* RepRap Prusa Mendel
* Sanguinololu Rev 1.3a
* ATmega644p
* Sprinter firmware git commit 3dca6f0
* Arduino IDE 0023

I don't know what will happen if you run it in other environments. So, you'd better just read its code and just to know how it works.


## Further Details

Please refer my slides at the XCON2013.

--

IN MEMORY OF Q, 25/08/13
