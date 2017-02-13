#!/usr/bin/python
# -*- coding: utf-8 -*-

# The Pin. Use Broadcom numbers.
BRIGHT_PIN   = 17
BUTTON_PIN   = 18
ON_LED_PIN   = 23

# User config
START_BRIGHT = 15   # Minutes before alarm to start lighting up
END_BRIGHT   = -45  # Minutes after alarm to turn off
MAX_BRIGHT   = 175  # Max brightness 1 - 255

# Other constants
BRIGHT_MULTI = MAX_BRIGHT / START_BRIGHT
SLEEP_TIME   = 10

import os
import sys
import pigpio
import time
import datetime
import signal
import RPi.GPIO as GPIO
from thread import start_new_thread

try:
	alarmTime = datetime.datetime.strptime(sys.argv[1], '%H:%M')
	alarmTime = alarmTime.replace(year=2000, month=1, day=1)
	print(alarmTime)
except:
	sys.stdout.write('Usage: %s HH:MM' % os.path.basename(sys.argv[0]))
	print("")
	quit()

#try:

bright = 0
oldbright = 0
abort = False

disable_light = False
button_press_time = None
override_light_on = False

pi = pigpio.pi()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ON_LED_PIN, GPIO.OUT)

GPIO.output(ON_LED_PIN, GPIO.HIGH)

def setLights(pin, brightness):
#	realBrightness = int(int(brightness) * (float(bright) / 255.0))
	pi.set_PWM_dutycycle(pin, brightness)

def fadeLights(pin, brightness):

#	print("FADE IN")

	newBrightness = brightness
	currentBrightness = pi.get_PWM_dutycycle(pin)

	if newBrightness < currentBrightness:
		setLights(BRIGHT_PIN, brightness)
		return
	
	while currentBrightness < newBrightness:

		if disable_light == True:
			return

		currentBrightness = currentBrightness + 1
		
		pi.set_PWM_dutycycle(pin, currentBrightness)
		time.sleep(0.1)
	
#	print("FADE OUT")

def handle_button_press():
	global disable_light
	global oldbright
	
	if disable_light == True:
		print('Light back on')
		disable_light = False
		oldbright = 0
		GPIO.output(ON_LED_PIN, GPIO.HIGH)
	else:
		print('Light off')
		disable_light = True
		GPIO.output(ON_LED_PIN, GPIO.LOW)

def handle_button_hold():
	global override_light_on

	if override_light_on == True:
		print("BUTTON HELD - LIGHT OFF")
		setLights(BRIGHT_PIN, 0)
		override_light_on = False
	else:
		print("BUTTON HELD - LIGHT ON")
		setLights(BRIGHT_PIN, 200)
		override_light_on = True

def round_bright(x):
	return int(round(x / 10.0)) * 10

def sigterm_handler(_signo, _stack_frame):
	GPIO.output(ON_LED_PIN, GPIO.LOW)
	GPIO.cleanup()
	setLights(BRIGHT_PIN, 0)
	abort = True
	sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

def checkTime():
	global bright
	global oldbright
	global abort
	
	while abort == False:
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
				
				bright = round_bright(bright)
		else:
			bright = 0
		
		if bright > 10:
			bright = round(bright)

		if bright > MAX_BRIGHT:
			bright = MAX_BRIGHT
		
		print("MINUTE: " + str(minuteDiff))
		print("DIFF: " + str(percDiff))
		print("BRIGHT: " + str(bright))
		
		time.sleep(SLEEP_TIME)

def checkButton():
	
	button_was_pressed  = False
	button_was_released = True

	while abort == False:

		button_state = GPIO.input(BUTTON_PIN)

		if button_state == False:

			if button_was_pressed == True and button_was_released == False:
				ts = time.time()

				if ts - button_press_time >= 1:
					print("BUTTON HELD")
					handle_button_hold()
					button_was_pressed = False
			
			elif button_was_released == False:
				pass

			else:

				button_was_released = False

				button_was_pressed = True
				button_press_time  = time.time()

		else:

			if button_was_pressed == True:

				handle_button_press()

			button_was_pressed  = False
			button_was_released = True
		
		time.sleep(0.1)

start_new_thread(checkTime, ())
start_new_thread(checkButton, ())

setLights(BRIGHT_PIN, 0)

while abort == False:

	if override_light_on == True:
		pass

	elif disable_light == True:
		setLights(BRIGHT_PIN, 0)

	elif bright != oldbright:

		oldbright = bright

		if bright > 0:
			fadeLights(BRIGHT_PIN, bright)
		else:
			setLights(BRIGHT_PIN, bright)
	
	time.sleep(0.2)

setLights(BRIGHT_PIN, 0)

time.sleep(0.5)

pi.stop()

#except:
#	GPIO.output(ON_LED_PIN, GPIO.LOW)
#	GPIO.cleanup()
	
