# COMS3930 Module 2: Sensors and WebSerial Project

## Grow Your Own Pixel Plant

Description:
A series of flowers, each with a randomly generated number of petals, simulate the game ["he loves me, he loves me not."](https://en.wikipedia.org/wiki/He_loves_me..._he_loves_me_not)
 One flower is displayed at a time. Petals are picked off one-by-one, and a corresponding message of “[he, she, they, I] loves me” or “[he, she, they, I] loves me not” is shown, culminating in a final answer when the last petal is picked off. 

Hardware Materials:
* TTGO T1 board with built-in ESP32 microcontroller
* Potentiometer Toggle
* Button
* Breadboard
* Male-to-female wires
* USB-C to USB-C cable 
* Laptop with USB-C port

Enclosure materials: 
* Cardboard Box - to be used as an enclosure
* Electric Tape
* Markers, Pen
* X-acto knife

Process: 
1. Align the TTGO T1 board with the breadboard so that each pin corresponds with its own row on the breadboard. Gently insert the TTGO board into the breadboard.
2. Use the Male-to-Female wires to connect the button and potentiometer to the breadboard, thereby connecting the button and potentiometer to the TTGO T1.
     - For the button:
         - Notice that there are 4 prongs on the button, but the 4 are paired into 2 pairs.
         - Connect one prong from the other pair to a ground pin.
         - Connect one prong from one pair to a GPIO pin on the TTGO T1 (again, via breadboard). Note the pin number. 
     - For the potentiometer:
         - Notice that there are 3 prongs in a line.
         - Connect one outer prong to the 3V pin.
         - Connect the other outer prong to a ground pin.
         - Connect the middle prong to a GPIO pin. Note the pin number. 
1. Connecting the button and potentiometer (choose pins) via wires to breadboard 
1. Connect TTGO T1 board to laptop via USB-C to USB-C cable. Set up Arduino IDE by selecting “TTGO T1” for board and the correct USB-C port.
3. Develop program (found in repo) that reads in serial input from button and potentiometer  in Arduino IDE. (make sure to write the correct pins) 

connecting serial 

