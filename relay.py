import RPi.GPIO as GPIO
from time import sleep  
PIN=4


GPIO.setmode(GPIO.BCM)
print( 'mode set %d' % GPIO.BCM )

print( 'setup')
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.LOW)
sleep(2)


print( 'out 1')
GPIO.output(PIN, GPIO.HIGH)
sleep(2)


print ('out 0')
GPIO.output(PIN, GPIO.LOW)
sleep(2)


print ('cleanup')
GPIO.cleanup()

