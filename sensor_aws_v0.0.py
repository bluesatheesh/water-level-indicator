#Import GPIO configuration
import RPi.GPIO as GPIO
# Import the AWS IoT Device SDK
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
# Import json for parson endpoint.json file
import json
# Import os for finding name of current directory
import os
import time
#========================= Cloud Connection ==============================================
# Load the endpoint from file
with open('endpoint.json') as json_file:
    data = json.load(json_file)

# Fetch the deviceName from the current folder name
deviceName = os.path.split(os.getcwd())[1]

# Pub Sub and Cert Files path
pubTopic = 'IoTSDK/WaterLevelSensor'
keyPath = 'private.pem.key'
certPath = 'certificate.pem.crt'
caPath = 'AmazonRootCA1.pem'
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

#============================Initialization=================================================
TRIG = 6
ECHO = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
GPIO.setwarnings(False)
GPIO.output(TRIG, False)
time.sleep(1)
#===========================================================================================

def get_distance():
    distance_addition = 0
    K=0
    for X in range(21):
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
            if (distance > 150) and (X!=K):
                K=K+1
                continue
            distance_addition = distance_addition + distance
            time.sleep(0.1)
        except Exception as e :
            pass
    average_distance = distance_addition / (X+1 -K)
    actual_distance = round(average_distance,3)
    return actual_distance

distance = get_distance()
date_time = str(time.strftime("%Y-%m-%d %H:%M:%S"))
message = {}
message['Distance'] = distance
message['Time'] = date_time
data = json.dumps(message)
publishToIoTTopic(pubTopic, data)
GPIO.cleanup()
