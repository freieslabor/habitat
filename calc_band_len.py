#!/usr/bin/env python3

# Script zum Rechnen der Längen der Stahlbänder am Ende der Balken.
# Quick-and-dirty, war nur für den Tag, an dem wir die Bänder angebaut haben.

import fileinput
import math
import os
import sys

W = 72.0    # Breite des Holzes
SLACK = 8.0 # Reserve, etwas ueberlaenge

print("Eingaben: Winkel, Lochbandlaenge")
while True:
	line = input()
	try:
		line = line.strip()
		line = line.split(",")
		if len(line)!=2:
			print("zwei Zahlen... Winkel , laenge")
			continue
		ang = float(line[0].strip())
		lenD = float(line[1].strip())
	except ValueError:
		print("not float")
		continue
	if ang<0.0 or ang>40.0:
		print("angle not in range 0..40")
		continue
	if lenD<70.0 or lenD>350.0:
		print("length not in range 70..350")
		continue
	ang *= math.pi/180.0
	B = W*math.tan(ang)
	C = W/math.cos(ang)
	A = (lenD-B-C-SLACK)*0.5
	print("A = %.1f\n"%(A,))


