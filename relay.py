from time import sleep

import RPi.GPIO as GPIO

GPIO.setwarnings(False)

PIN = 4


GPIO.setmode(GPIO.BCM)
print(f"mode set {GPIO.BCM}")

print("setup")
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)
sleep(2)


print("out 1")
GPIO.output(PIN, GPIO.HIGH)
sleep(2)


# print ('out 0')
# GPIO.output(PIN, GPIO.LOW)
# sleep(2)


print("cleanup")
GPIO.cleanup(PIN)
GPIO.setwarnings(False)
