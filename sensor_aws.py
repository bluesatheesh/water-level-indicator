# Import the AWS IoT Device SDK
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Import json for parson endpoint.json file
import json

# Import os for finding name of current directory
import os
import RPi.GPIO as GPIO
import time,os

import datetime

TRIG = 6
ECHO = 5
ALARM = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.output(TRIG, False)

GPIO.setup(ALARM,GPIO.OUT)
GPIO.output(ALARM, True)

print ("Waiting For Sensor To Settle")
time.sleep(1) #settling time 

def get_distance():
	dist_add = 0
	k=0
	for x in range(20):
		try:
			GPIO.output(TRIG, True)
			time.sleep(0.00001)
			GPIO.output(TRIG, False)

			while GPIO.input(ECHO)==0:
				pulse_start = time.time()

			while GPIO.input(ECHO)==1:
				pulse_end = time.time()

			pulse_duration = pulse_end - pulse_start
			
			distance = pulse_duration * 17150

			distance = round(distance, 3)
			print (x, "distance: ", distance)
		
			if(distance > 125):# ignore erroneous readings (max distance cannot be more than 125)
				k=k+1
				continue
		
			dist_add = dist_add + distance
			#print "dist_add: ", dist_add
			time.sleep(.1) # 100ms interval between readings
		
		except Exception as e:
            pass
	
	
	print ("x: ", x+1)
	print ("k: ", k)

	avg_dist=dist_add/(x+1 -k)
	dist=round(avg_dist,3)
	#print ("dist: ", dist)
	return dist

def low_level_warning(dist):
	level=114-dist
	if(level<40):
		print("level low : ", level)
		GPIO.output(ALARM, False)
	else:
		GPIO.output(ALARM, True)
		print("level ok")
low_level_warning(distance)
#########################################################################################

# Load the endpoint from file
with open('/home/ec2-user/environment/endpoint.json') as json_file:  
    data = json.load(json_file)

# Fetch the deviceName from the current folder name
deviceName = os.path.split(os.getcwd())[1]

# Pub Sub and Cert Files path
pubTopic = 'IoTSDK/WaterLevel/'
keyPath = 'private.pem.key'
certPath = 'certificate.pem.crt'
caPath = '/home/ec2-user/environment/root-CA.crt'
clientId = deviceName
host = data['endpointAddress']
port = 8883

# client using the useful variable above and connect it to AWS IoT
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(caPath, keyPath, certPath)
myAWSIoTMQTTClient.connect()

# Function to publish payload to IoT topic
def publishToIoTTopic(topic, payload):
    myAWSIoTMQTTClient.publish(topic, payload, 1)

# Infinite loop reading console input and publishing what it finds
while True:
    distance=get_distance()
    print ("distance: ", distance)

print ("---------------------")
    message = input('Enter a message on the next line to send to ' + pubTopic + ':\r\n')
    # Calling function to publish to IoT Topic
    publishToIoTTopic(pubTopic, message)