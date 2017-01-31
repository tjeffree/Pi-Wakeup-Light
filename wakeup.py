#!/usr/bin/python
# -*- coding: utf-8 -*-

# The Pin. Use Broadcom numbers.
BRIGHT_PIN   = 17

# User config
START_BRIGHT = 15   # Minutes before alarm to start lighting up
END_BRIGHT   = -45  # Minutes after alarm to turn off
MAX_BRIGHT   = 255  # Max brightness 1 - 255

# Other constants
BRIGHT_MULTI = MAX_BRIGHT / START_BRIGHT
SLEEP_TIME   = 10

import os
import sys
import pigpio
import time
import datetime
import signal
from thread import start_new_thread

try:
	alarmTime = datetime.datetime.strptime(sys.argv[1], '%H:%M')
	alarmTime = alarmTime.replace(year=2000, month=1, day=1)
	print(alarmTime)
except:
	sys.stdout.write('Usage: %s HH:MM' % os.path.basename(sys.argv[0]))
	print("")
	quit()

bright = 0
oldbright = 0
abort = False

pi = pigpio.pi()

def setLights(pin, brightness):
	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, realBrightness)

def fadeLights(pin, brightness):

#	print("FADE IN")

	newBrightness = brightness
	currentBrightness = pi.get_PWM_dutycycle(pin)

	if newBrightness < currentBrightness:
		setLights(BRIGHT_PIN, brightness)
		return
	
	while currentBrightness < newBrightness:
		currentBrightness = currentBrightness + 1
		
		pi.set_PWM_dutycycle(pin, currentBrightness)
		time.sleep(0.1)
	
#	print("FADE OUT")

def sigterm_handler(_signo, _stack_frame):
	setLights(BRIGHT_PIN, 0)
	abort = True
	sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

def checkTime():
	global bright
	global oldbright
	global abort
	
	while True:
		now = datetime.datetime.now()
		now = now.replace(year=2000, month=1, day=1) # , hour=6, minute=25, second=0

		d1_ts = time.mktime(now.timetuple())
		d2_ts = time.mktime(alarmTime.timetuple())

		minuteDiff = (d2_ts - d1_ts) / 60
		percDiff   = 0

		if minuteDiff < START_BRIGHT and minuteDiff > END_BRIGHT:
			
			if minuteDiff < 0:
				bright = MAX_BRIGHT
			
			else:
				bright = (START_BRIGHT - minuteDiff) * BRIGHT_MULTI

				percDiff = (minuteDiff / START_BRIGHT) * 100

				if percDiff > 5:
					bright = bright * 0.2
				elif percDiff > 1:
					bright = bright * 0.5

		else:
			bright = 0

		bright = round(bright)

		if bright > MAX_BRIGHT:
			bright = MAX_BRIGHT
		
		print("MINUTE: " + str(minuteDiff))
		print("DIFF: " + str(percDiff))
		print("BRIGHT: " + str(bright))
		
		time.sleep(SLEEP_TIME)

start_new_thread(checkTime, ())

while abort == False:
	if bright != oldbright:

		oldbright = bright

		if bright > 0:
			fadeLights(BRIGHT_PIN, bright)
		else:
			setLights(BRIGHT_PIN, bright)
	
	time.sleep(0.1)

setLights(BRIGHT_PIN, 0)

time.sleep(0.5)

pi.stop()
